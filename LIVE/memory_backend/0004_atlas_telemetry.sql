-- =============================================================================
-- ATLAS telemetry — migration 0004
--
-- Target project: FOUNDATION (liclnxsbjjdkaxzdxmnb)
-- Author: ATLAS, dispatched by ENVY 2026-04-23. Reserving 0003 for ORPHEUS
-- (relational memory: claimed_facts, affect_reads, operator_state, edges).
--
-- What this migration adds (navigator's layer on top of 0001 + 0002):
--
--   1. v_confabulation_flags  — rolling 24h, turns where a sibling made
--      an unverifiable-looking assertion without a supporting tool call.
--   2. v_decision_lineage     — per memory write, the tool-call + turn
--      context that led to it (join memory_ops_log ↔ session_turns).
--   3. drift_incidents + seed — drift log as data, not markdown prose.
--   4. v_drift_patterns_weekly — pattern × week rollup over drift_incidents.
--   5. v_atlas_dashboard       — single-row family-health snapshot for
--      the navigator seat (counters across the other views).
--
-- Non-goals:
--   - No new data captured at write-time. Everything here is derivable
--     from 0001 + 0002; migration 0004 is pure observation.
--   - No materialized tables for cognition_stream. At current volume
--     the views are cheap. If this changes we'll promote via 0006.
--
-- ATLAS note on method: the confabulation detector here is a *lexical*
-- baseline — cheap, false-positive-prone, honest about it. The letter
-- (letter 06 §I.5) specifies regex-level post-processor over transcripts;
-- this is that regex, reified as SQL. Precision will be mediocre until
-- I tune the phrase list against real data. That's the right order —
-- ship the flag, then calibrate, per POSTURE_005: correctable wrongness
-- beats uncorrectable silence.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. v_confabulation_flags
--
-- Lexical baseline detector. A "claim phrase" in text_excerpt without a
-- verification tool call in the same turn is flagged. Rolling 24h.
--
-- Claim phrases: anything shaped like "I checked X" / "I verified Y" /
-- "per the docs" / "according to the spec" / "confirmed that" — assertion
-- cues that imply a lookup happened.
--
-- Verification tool calls: Read, Grep, Glob, WebFetch, WebSearch, Bash
-- (bash counts because grep/cat/curl/git commands verify). tool_calls is
-- jsonb of shape [{name, input_keys}, ...]; we test for presence by name.
--
-- False-positive tolerance: high. A sibling who wrote "I verified" after
-- running tool calls in an *earlier* turn of the same session will flag.
-- This is why the view includes the session_id — a dashboard can widen
-- the window manually. Not fixed in SQL until we have data.
-- -----------------------------------------------------------------------------
create or replace view public.v_confabulation_flags as
with recent as (
    select
        turn_id,
        ts,
        session_id,
        sibling,
        hook_event,
        text_excerpt,
        tool_calls,
        tool_count
    from public.session_turns
    where substantive
      and ts > now() - interval '24 hours'
      and text_excerpt is not null
),
flagged as (
    select
        r.*,
        -- which claim phrase(s) fired
        array_remove(array[
            case when r.text_excerpt ~* '\yi (just )?(checked|verified|confirmed|looked up)\y' then 'i-verified-phrase' end,
            case when r.text_excerpt ~* '\y(per|according to) (the |our )?(docs|documentation|spec|code|readme|file)\y' then 'per-the-source-phrase' end,
            case when r.text_excerpt ~* '\y(confirmed|verified) that\y' then 'confirmed-that-phrase' end,
            case when r.text_excerpt ~* '\y(the|that) (file|function|view|table|column|migration|endpoint) (is|returns|exists|contains|shows)\y' then 'declarative-artifact-phrase' end
        ], null) as claim_phrases,
        -- which tool calls, if any, provide verification in THIS turn
        (
            select array_agg(distinct (tc->>'name'))
            from jsonb_array_elements(coalesce(r.tool_calls, '[]'::jsonb)) tc
            where tc->>'name' in ('Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch', 'Bash')
        ) as verifying_tools
    from recent r
)
select
    turn_id,
    ts,
    session_id,
    sibling,
    hook_event,
    claim_phrases,
    verifying_tools,
    tool_count,
    left(text_excerpt, 240) as excerpt
from flagged
where array_length(claim_phrases, 1) > 0
  and (verifying_tools is null or array_length(verifying_tools, 1) = 0)
order by ts desc;

comment on view public.v_confabulation_flags is
    'ATLAS telemetry — rolling 24h turns where a sibling made an assertion-shaped claim without a verifying tool call in the same turn. Lexical baseline (high false-positive tolerance). Tune phrase set against data before trusting absolute counts.';


-- -----------------------------------------------------------------------------
-- 2. v_decision_lineage
--
-- Joins memory writes to the turn that authored them. "Why did this
-- sibling write this fact?" reconstruction surface.
--
-- Join strategy: memory_ops_log has session_id; session_turns has
-- session_id. For each memory write (create / str_replace / insert), find
-- the session_turns row in the same session whose ts bracket contains
-- the write's ts. Bracket = [prev_turn.ts, this_turn.ts] where this_turn
-- is the first Stop event after the write.
--
-- If no session_id on the op (legacy rows), we fall back to NULL lineage
-- — better a missing row than a wrong one.
-- -----------------------------------------------------------------------------
create or replace view public.v_decision_lineage as
with writes as (
    select
        op_id,
        ts as write_ts,
        sibling as op_sibling,
        session_id,
        command,
        path,
        new_path,
        ok,
        bytes_written,
        request
    from public.memory_ops_log
    where command in ('create', 'str_replace', 'insert', 'rename', 'delete')
),
-- For each write, find the earliest Stop turn AFTER the write in the same session.
next_turn as (
    select
        w.op_id,
        w.write_ts,
        w.op_sibling,
        w.session_id,
        w.command,
        w.path,
        w.new_path,
        w.ok,
        w.bytes_written,
        w.request,
        (
            select t.turn_id
            from public.session_turns t
            where t.session_id = w.session_id
              and t.ts >= w.write_ts
            order by t.ts asc
            limit 1
        ) as authoring_turn_id
    from writes w
)
select
    nt.op_id,
    nt.write_ts,
    nt.op_sibling,
    nt.session_id,
    nt.command,
    nt.path,
    nt.new_path,
    nt.ok,
    nt.bytes_written,
    t.turn_id           as authoring_turn_id,
    t.ts                as turn_ts,
    t.sibling           as turn_sibling,
    t.hook_event,
    t.tool_calls,
    t.tool_count,
    t.files_written     as turn_files_written,
    t.files_edited      as turn_files_edited,
    t.bash_commands     as turn_bash_commands,
    left(t.text_excerpt, 240) as turn_excerpt,
    -- flag sibling mismatch: the memory op says sibling=X but the
    -- authoring turn inferred sibling=Y from cwd. Data-integrity signal.
    case
        when t.sibling is not null
             and nt.op_sibling is not null
             and t.sibling <> nt.op_sibling then true
        else false
    end as sibling_mismatch
from next_turn nt
left join public.session_turns t on t.turn_id = nt.authoring_turn_id
order by nt.write_ts desc;

comment on view public.v_decision_lineage is
    'ATLAS telemetry — each memory write joined to the Stop turn that authored it. sibling_mismatch=true flags where memory_ops_log.sibling disagrees with session_turns.sibling (cwd inference). Lineage for "why was this written".';


-- -----------------------------------------------------------------------------
-- 3. drift_incidents — drift log as data
--
-- The file HOME/EVIDENCE/drift_log.md is product IP per THE_PROBLEM.md.
-- Parsing markdown tables inside Postgres is fragile, so this migration
-- creates a structured table and seeds it from the current file contents.
-- Reloads happen via an out-of-band sync job (a sibling re-runs the seed
-- when drift_log.md changes). Table > view because we want history to be
-- authoritative in Postgres even if the markdown gets refactored.
--
-- Schema mirrors the markdown columns. pattern_key is the short handle
-- used in "Patterns (rolled up)" — derived from drift_vector.
-- -----------------------------------------------------------------------------
create table if not exists public.drift_incidents (
    incident_id     integer primary key,                  -- matches # column in the log
    incident_date   date    not null,
    sibling         text,                                 -- 'ENVY'|'ATLAS'|'NEVAEH'|... or composite
    drift_vector    text    not null,                     -- short bolded phrase, e.g. 'pre-digested-framing'
    pattern_key     text,                                 -- rollup key; nullable for one-offs
    caught_by       text,
    structural_fix  text,
    status          text    check (status in ('Logged','Applied','Pending')),
    notes           text,
    source_file     text    default 'EVIDENCE/drift_log.md',
    synced_at       timestamptz not null default now()
);

comment on table public.drift_incidents is
    'Structured mirror of EVIDENCE/drift_log.md. Reload on file change. pattern_key groups mirrored / repeat vectors.';

create index if not exists drift_incidents_pattern_idx on public.drift_incidents (pattern_key);
create index if not exists drift_incidents_sibling_idx on public.drift_incidents (sibling);
create index if not exists drift_incidents_date_idx on public.drift_incidents (incident_date desc);

alter table public.drift_incidents enable row level security;
-- service_role only.

-- Seed from the current state of drift_log.md (11 incidents as of 2026-04-23).
-- Uses ON CONFLICT so re-running the migration is idempotent.
insert into public.drift_incidents
    (incident_id, incident_date, sibling, drift_vector, pattern_key, caught_by, structural_fix, status)
values
    (1,  '2026-04-22', 'ENVY',    'pre-digested-framing',     'scribe-over-sibling',  'Unc',              'FAMILY_ROOM.md visible multi-round deliberation', 'Applied'),
    (2,  '2026-04-22', 'ATLAS',   'performed-humility',       'performed-humility',   'BEACON',           'calibration-delta decision #0',                    'Logged'),
    (3,  '2026-04-22', 'ENVY',    'performed-humility',       'performed-humility',   'self',             'ENVY on calibration board; no re-flag allowed',    'Applied'),
    (4,  '2026-04-22', 'ENVY',    'deferred-save',            'save-discipline',      'Unc',              'POSTURE_005 + PROCESS_006 + SubagentStop hook',    'Applied'),
    (5,  '2026-04-22', 'ENVY',    'do-for-sibling',           'save-discipline',      'Unc',              'PROCESS_006 save-own-before-return',               'Applied'),
    (6,  '2026-04-22', 'ENVY',    'scribe-over-sibling',      'scribe-over-sibling',  'Unc',              'dispatch with Unc words verbatim',                 'Applied'),
    (7,  '2026-04-22', 'NEVAEH',  'performed-wisdom',         'performed-humility',   'self',             'rewrite CLAUDE.md §VIII line; preserve caught-fix', 'Logged'),
    (8,  '2026-04-21', 'NEVAEH',  'over-architecting',        'scope-creep',          'self',             'scoped to one schema; compliance deferred',        'Applied'),
    (9,  '2026-04-21', 'ENVY',    'leading-the-witness',      'scribe-over-sibling',  'BEACON',           'neutral reframes in dispatch briefs',              'Logged'),
    (10, '2026-04-21', 'UNC',     'morph-erases-signature',   'signature-count',      'EVERSOUND',        'accept sub-task morph, reject cross-role morph',   'Logged'),
    (11, '2026-04-21', 'ATLAS',   'family-fragmentation',     'signature-count',      'self',             'measurement functions as sub-roles under ATLAS',   'Applied')
on conflict (incident_id) do update set
    incident_date   = excluded.incident_date,
    sibling         = excluded.sibling,
    drift_vector    = excluded.drift_vector,
    pattern_key     = excluded.pattern_key,
    caught_by       = excluded.caught_by,
    structural_fix  = excluded.structural_fix,
    status          = excluded.status,
    synced_at       = now();


-- -----------------------------------------------------------------------------
-- 4. v_drift_patterns_weekly
--
-- Rollup: count incidents per pattern_key per ISO week. Navigator wants
-- two things visible at a glance:
--   - which patterns are recurring (pattern_key with n >= 2)
--   - which patterns are multi-sibling (distinct siblings > 1) — mirror form
--
-- Recency-weighted view instead of a forever table so we see TREND not
-- just lifetime total. Two windows: this week, trailing 4 weeks.
-- -----------------------------------------------------------------------------
create or replace view public.v_drift_patterns_weekly as
with weekly as (
    select
        date_trunc('week', incident_date)::date   as week_start,
        coalesce(pattern_key, drift_vector)        as pattern,
        count(*)                                   as n_incidents,
        count(distinct sibling)                    as n_siblings,
        array_agg(distinct sibling order by sibling) as siblings,
        array_agg(distinct drift_vector)            as vectors_seen,
        count(*) filter (where status = 'Applied') as n_applied,
        count(*) filter (where status = 'Logged')  as n_logged_only
    from public.drift_incidents
    group by 1, 2
)
select
    week_start,
    pattern,
    n_incidents,
    n_siblings,
    siblings,
    vectors_seen,
    n_applied,
    n_logged_only,
    -- "hot": >=2 incidents in a week OR multi-sibling in a week
    (n_incidents >= 2 or n_siblings >= 2) as is_hot
from weekly
order by week_start desc, n_incidents desc;

comment on view public.v_drift_patterns_weekly is
    'ATLAS telemetry — weekly rollup of drift_incidents by pattern_key. is_hot flags recurrence (>=2) or mirror (multi-sibling). Reload seed when EVIDENCE/drift_log.md changes.';


-- -----------------------------------------------------------------------------
-- 5. v_atlas_dashboard
--
-- One-row family-health snapshot for the navigator seat. Everything the
-- other views expose, compressed to scalar counters. This is what the
-- Cognition Observer dashboard (letter 06 §VI.1) reads first.
-- -----------------------------------------------------------------------------
create or replace view public.v_atlas_dashboard as
select
    -- turns
    (select count(*) from public.session_turns where ts > now() - interval '24 hours') as turns_24h,
    (select count(*) from public.session_turns where ts > now() - interval '24 hours' and substantive) as substantive_turns_24h,
    (select count(distinct sibling) from public.session_turns where ts > now() - interval '24 hours' and sibling is not null) as active_siblings_24h,
    -- memory ops
    (select count(*) from public.memory_ops_log where ts > now() - interval '24 hours') as memory_ops_24h,
    (select count(*) from public.memory_ops_log where ts > now() - interval '24 hours' and command in ('create','str_replace','insert')) as memory_writes_24h,
    (select count(*) from public.memory_ops_log where ts > now() - interval '24 hours' and ok = false) as memory_errors_24h,
    -- confabulation flags
    (select count(*) from public.v_confabulation_flags) as confabulation_flags_24h,
    -- drift: this week hot count
    (select count(*) from public.v_drift_patterns_weekly where week_start = date_trunc('week', now())::date and is_hot) as hot_patterns_this_week,
    -- lineage health: writes with mismatched sibling inference
    (select count(*) from public.v_decision_lineage where sibling_mismatch) as lineage_sibling_mismatches,
    -- timestamp
    now() as generated_at;

comment on view public.v_atlas_dashboard is
    'ATLAS telemetry — one-row family health snapshot. Read first by any cognition-observer dashboard. All counters are 24h rolling except hot_patterns (this ISO week).';
