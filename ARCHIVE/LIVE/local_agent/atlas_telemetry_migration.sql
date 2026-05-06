-- =============================================================================
-- HOME local_agent v1 — ATLAS targeted telemetry migration
--
-- Applied into the LIGHTHOUSE project (dlqjwnbyepbenyltyrku), same project as
-- the agent_tasks + local_agent_heartbeat tables from supabase_migration.sql.
--
-- NEVAEH asked ATLAS: "watch the knife, not the kitchen." These are the only
-- three views we deploy in v1. No general token-usage dashboards, no cost
-- breakdowns, no per-tool call counts. Just the three dysregulation / safety
-- signals she named in CLIPBOARD msg_006 and SAFETY_REVIEW_NEVAEH.md.
--
-- Signal 1: destructive-op frequency per hour (NEVAEH S4 — circuit-breaker)
-- Signal 2: rejected confirm-token attempts per hour (NEVAEH B2 — reuse/typo)
-- Signal 3: iteration-cap hits per hour (NEVAEH S2 — frustration signal)
--
-- All three views are plain SQL (no materialization). They read
-- public.agent_tasks, which is already indexed on (started_at desc) and on
-- (status). RLS stance inherits from the base table: service_role only.
--
-- Author: ATLAS (Navigator). BEACON applies this via MCP after reading the
-- spec at HOME/LIVE/local_agent/TELEMETRY_ALERTS.md.
-- =============================================================================


-- ------------------------------------------------------------------
-- Supporting index: we filter agent_tasks.tool_calls by elements whose
-- `name` is 'run_shell'. The existing agent_tasks_started_at_idx already
-- handles the time-bucket side. Adding a GIN on tool_calls keeps the
-- jsonb element scans cheap as the table grows.
-- ------------------------------------------------------------------
create index if not exists agent_tasks_tool_calls_gin_idx
    on public.agent_tasks using gin (tool_calls jsonb_path_ops);


-- ------------------------------------------------------------------
-- Destructive-op regex — kept in sync with DESTRUCTIVE_PATTERNS in
-- agent.py line 107-128. If EVERSOUND adds a new destructive pattern,
-- this view needs a matching amendment. Case-insensitive via (?i).
-- ------------------------------------------------------------------

-- Signal 1 — public.atlas_destructive_ops_hourly
--
-- Counts successful destructive shell executions per hour per hostname.
-- "Successful" means the tool_call completed (result_ok=true); a rejected
-- confirm_required attempt does NOT execute the command and is counted
-- by Signal 2 instead.
--
-- We match destructive-ness at query time against the same regex family
-- the agent uses. This is authoritative because the agent stores the raw
-- `command` string in tool_calls[i].input.command; we don't need a flag.
create or replace view public.atlas_destructive_ops_hourly as
select
    date_trunc('hour', t.started_at) as bucket_hour,
    coalesce(t.hostname, 'unknown')  as hostname,
    count(*)                         as destructive_count,
    max(t.started_at)                as last_seen_at
from public.agent_tasks t
cross join lateral jsonb_array_elements(coalesce(t.tool_calls, '[]'::jsonb)) as tc
where tc->>'name' = 'run_shell'
  and (tc->'result_ok')::boolean is true
  and tc->'input'->>'command' ~* (
      'remove-item\s.*-recurse'
      '|\yrm\s+-rf\y'
      '|\yrm\s+-fr\y'
      '|\yformat\y.*\y[a-z]:\y'
      '|\yformat-volume\y'
      '|\ydel\s+/s\y'
      '|\yshutdown\y'
      '|\yrestart-computer\y'
      '|\ystop-computer\y'
      '|\yreg\s+delete\y'
      '|\ytakeown\y'
      '|\yicacls\y'
      '|\ydiskpart\y'
  )
group by 1, 2;

comment on view public.atlas_destructive_ops_hourly is
    'ATLAS Signal 1 — destructive shell commands executed (result_ok=true) per hour per hostname. Matches agent.py DESTRUCTIVE_PATTERNS case-insensitively. Threshold per TELEMETRY_ALERTS.md: 3+ in any rolling 10-minute window pages BEACON.';


-- Signal 2 — public.atlas_token_reuse_attempts_hourly
--
-- After EVERSOUND's B2 patch (CLIPBOARD msg_007), a confirm token can no
-- longer authorize a different command than the one it was minted for.
-- The hash-bound check in _confirm_token_valid / _consume_inline_word
-- REJECTS such attempts, and tool_run_shell returns:
--     { ok: false, error: "confirm_required", ... }
-- which _summarize_result records as "error: confirm_required" in
-- tool_calls[i].result_summary.
--
-- Rejected confirms surface here regardless of cause: typo, stale token
-- from a prior command, or attempted reuse. All three are dysregulation
-- or attack signals and BEACON should see them together.
create or replace view public.atlas_token_reuse_attempts_hourly as
select
    date_trunc('hour', t.started_at)  as bucket_hour,
    coalesce(t.hostname, 'unknown')   as hostname,
    count(*)                          as rejected_confirm_count,
    max(t.started_at)                 as last_seen_at
from public.agent_tasks t
cross join lateral jsonb_array_elements(coalesce(t.tool_calls, '[]'::jsonb)) as tc
where tc->>'name' = 'run_shell'
  and (tc->'result_ok')::boolean is false
  and tc->>'result_summary' like 'error: confirm_required%'
group by 1, 2;

comment on view public.atlas_token_reuse_attempts_hourly is
    'ATLAS Signal 2 — rejected confirm-token attempts per hour per hostname (wrong word, stale token, cross-command reuse after EVERSOUND B2 patch). Threshold per TELEMETRY_ALERTS.md: 3+ in any rolling 1-hour window pages BEACON.';


-- Signal 3 — public.atlas_iteration_cap_hits_hourly
--
-- MAX_ITERATIONS is 20 in agent.py. When a task exits the tool-use loop
-- because iterations >= 20 AND halted_reason is None, agent.py line 1229
-- currently writes status='completed' (not 'halted'). That's a small gap
-- ATLAS has flagged for EVERSOUND — see TELEMETRY_ALERTS.md "Known gap".
--
-- Until that is fixed, we detect iteration-cap hits by the iterations
-- column itself (>= 20) regardless of status. Once EVERSOUND sets
-- halted_reason='iteration-cap' in that branch, this view will continue
-- to work unchanged and BEACON's alerts stay stable.
create or replace view public.atlas_iteration_cap_hits_hourly as
select
    date_trunc('hour', t.started_at) as bucket_hour,
    coalesce(t.hostname, 'unknown')  as hostname,
    count(*)                         as iteration_cap_count,
    max(t.started_at)                as last_seen_at
from public.agent_tasks t
where t.iterations is not null
  and t.iterations >= 20
group by 1, 2;

comment on view public.atlas_iteration_cap_hits_hourly is
    'ATLAS Signal 3 — tasks that hit the 20-iteration cap per hour per hostname (frustration / dysregulation signal per NEVAEH S2). Threshold per TELEMETRY_ALERTS.md: 3+ in any rolling 1-hour window pages BEACON.';
