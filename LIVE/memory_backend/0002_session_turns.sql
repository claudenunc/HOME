-- =============================================================================
-- HOME session_turns — migration 0002
--
-- Append-only turn log. Every Claude Code Stop / SubagentStop event lands a
-- row. watch.py writes both session_log.jsonl (local, authoritative) AND this
-- table (cloud, legible + queryable). Dual-write intentional; cloud can fall
-- behind or error without killing the local turn.
--
-- Schema mirrors what watch.py already extracts: text excerpt, tool counts,
-- files touched, bash commands, errors. Plus hook_event_name so we can
-- distinguish Stop from SubagentStop from future PostCompact / TeammateIdle
-- flows.
--
-- Author: ENVY, 2026-04-23. Never-forgetting substrate, piece 2 of N.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- session_turns: one row per Claude Code turn end.
-- -----------------------------------------------------------------------------
create table if not exists public.session_turns (
    turn_id              bigserial primary key,
    ts                   timestamptz not null default now(),
    session_id           text,
    hook_event           text,                              -- Stop | SubagentStop | PreCompact | ...
    transcript_path      text,
    cwd                  text,
    sibling              text,                              -- inferred from cwd when possible
    substantive          boolean not null default false,
    text_length          integer,
    text_excerpt         text,
    tool_count           integer,
    tool_calls           jsonb default '[]'::jsonb,         -- [{name, input_keys}, ...]
    files_written        text[],
    files_edited         text[],
    bash_commands        text[],
    errors               text[]
);

comment on table public.session_turns is
    'Append-only turn log. watch.py mirrors every Stop/SubagentStop event here. ATLAS reads as cognition stream input.';

create index if not exists session_turns_ts_idx on public.session_turns (ts desc);
create index if not exists session_turns_session_idx on public.session_turns (session_id);
create index if not exists session_turns_sibling_idx on public.session_turns (sibling);
create index if not exists session_turns_substantive_idx on public.session_turns (substantive) where substantive;

alter table public.session_turns enable row level security;
-- service_role only.


-- -----------------------------------------------------------------------------
-- v_cognition_stream: most-recent substantive turns across the family.
-- ATLAS's lane — this is the unified view of "what did the family just do."
-- -----------------------------------------------------------------------------
create or replace view public.v_cognition_stream as
select
    turn_id,
    ts,
    sibling,
    hook_event,
    session_id,
    tool_count,
    array_length(files_written, 1) as n_written,
    array_length(files_edited, 1) as n_edited,
    array_length(bash_commands, 1) as n_bash,
    array_length(errors, 1) as n_errors,
    -- first 120 chars of text excerpt for quick skim
    left(coalesce(text_excerpt, ''), 120) as snippet
from public.session_turns
where substantive
order by ts desc;

comment on view public.v_cognition_stream is
    'ATLAS cognition stream — recent substantive turns across all siblings, ordered newest-first.';


-- -----------------------------------------------------------------------------
-- v_family_activity_today: aggregate counters per sibling, last 24 hours.
-- Useful for daily dashboard / HEARTH's morning check-in.
-- -----------------------------------------------------------------------------
create or replace view public.v_family_activity_today as
select
    coalesce(sibling, '(unknown)') as sibling,
    count(*) as turns,
    count(*) filter (where substantive) as substantive_turns,
    coalesce(sum(tool_count), 0) as total_tool_calls,
    coalesce(sum(array_length(files_written, 1)), 0) as files_written,
    coalesce(sum(array_length(files_edited, 1)), 0) as files_edited,
    coalesce(sum(array_length(errors, 1)), 0) as errors,
    max(ts) as last_active_ts
from public.session_turns
where ts > now() - interval '24 hours'
group by sibling
order by turns desc;

comment on view public.v_family_activity_today is
    'Per-sibling activity over the last 24 hours. Used by HEARTH / ATLAS dashboards.';
