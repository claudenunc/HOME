-- =============================================================================
-- Trace_id enforcement — migration 0007
--
-- Target project: FOUNDATION (liclnxsbjjdkaxzdxmnb)
-- Author: ORPHEUS 🎼 — 2026-05-05
-- Depends on: 0001 (memory_files), 0002 (session_turns), 0003 (claims,
--             affect_reads), 0005 (embed_log), 0006 (observers.public_key)
--
-- WHAT THIS SHIPS
-- ---------------
--
-- Three-layer invariant for trace_id discipline (CLAUDE.md §8):
--
--   Doctrine  → CLAUDE.md §5.5 rule (already live): every request gets a
--               trace_id at ingress; every downstream event carries it;
--               full trace reconstructible from one id.
--
--   Template  → memory_ops_log schema: the default shape of every write
--               operation already carries trace_id.  The Python write path
--               (supabase_memory.py, embed_worker.py) logs to ops_log; the
--               log structure is the pattern callers copy.
--
--   Hook      → memory_ops_log.trace_id is NOT NULL.  An audit write without
--               a trace_id FAILS LOUD (Red line §3).  The DB enforces what
--               the application layer is supposed to provide.  Silent failure
--               = hole in the trace = broken invariant.
--
-- TABLES ADDED
-- ------------
--   memory_ops_log    Authoritative audit spine.  One row per write/retrieve
--                     operation.  trace_id NOT NULL — the hook layer.
--
-- COLUMNS ADDED (nullable with default — legacy rows survive)
-- -----------------------------------------------------------
--   memory_files.trace_id    — UUID of ingress request that created/last-
--                              modified this file.  NULL for pre-0007 rows.
--   session_turns.trace_id   — UUID of the Stop/SubagentStop event's session.
--   claims.trace_id          — UUID of the ingress that asserted this claim.
--   affect_reads.trace_id    — UUID of the session turn that triggered the
--                              affect read.
--
-- VIEWS ADDED
-- -----------
--   v_trace_coverage     Per-table trace_id fill rate (for ATLAS dashboards).
--   v_orphaned_ops       Ops_log rows with no matching memory_file or claim
--                        target — data-quality sentinel.
--
-- RPCs ADDED
-- ----------
--   reconstruct_trace(p_trace_id)   Returns the ordered sequence of ops_log
--                                   events for a given trace_id — one query
--                                   to audit an entire ingress request.
--
-- NON-GOALS THIS MIGRATION
-- ------------------------
--   - Does NOT backfill trace_id on pre-0007 rows (batch job; not a migration).
--   - Does NOT add per-sibling RLS on ops_log.
--   - Does NOT add trace_id to embed_log (low-priority; embed batches are
--     already identified by (ts, run_by, model)).
--   - Does NOT change the RLS stance (service_role only, same as 0001–0006).
--   - Does NOT add the NEVAEH clinical layer (rupture_events, formulation).
--     That is 0008.
--
-- ARCHITECTURE STANCES LOCKED IN 0007
-- -------------------------------------
--   - trace_id is a UUID (not a string timestamp, not a random int).  Stable
--     across retries if the caller preserves it.  Never auto-generated in the
--     DB unless the column default fires — callers MUST pass an explicit
--     trace_id for the hook to carry meaning.
--   - memory_ops_log is append-only.  No UPDATE.  No DELETE.  Corrections
--     are new rows with status='correction' and a reference in metadata.
--   - reconstruct_trace returns ops_log only.  As more tables gain trace_id
--     the function will UNION them in; today the spine is the ops_log.
--   - v_trace_coverage uses count(*) filter — counts NULLs separately from
--     total so ATLAS can see the fill rate improving over time.
-- =============================================================================


-- =============================================================================
-- 1. memory_ops_log — the audit spine
--
-- Every meaningful write or retrieve operation logs a row here.  The Python
-- call path (supabase_memory.py write methods, embed_worker.py batches,
-- retrieve.py calls, ingest_local_memories.py seeding) is responsible for
-- writing ops_log rows.  The DB enforces trace_id NOT NULL (the hook).
--
-- op_type vocab (extend at the application layer via metadata; add CHECK
-- values here when a new op_type stabilises):
--   write        — new or updated memory_file
--   retrieve     — retrieve_neighborhood or retrieve_neighborhood_with_recency
--   embed        — embed_worker processed a file
--   sign         — sign_row.py signed a row
--   migrate      — migrate.py applied a migration
--   ingest       — ingest_local_memories.py seeded a file
--   compress     — a memory_file was compressed / deduplicated
--   read         — read operation (last_read_at updated)
--   claim_write  — new claim or superseding claim asserted
--   receipt_write— a claim invoked in an artifact
-- =============================================================================
create table if not exists public.memory_ops_log (
    op_id           uuid primary key default gen_random_uuid(),
    trace_id        uuid not null,               -- ingress request trace; NEVER NULL
    ts              timestamptz not null default now(),
    actor           text not null,               -- sibling handle, 'system', 'embed_worker', etc.
    op_type         text not null check (op_type in (
                        'write','retrieve','embed','sign','migrate',
                        'ingest','compress','read','claim_write','receipt_write',
                        'correction'
                    )),
    target_kind     text not null check (target_kind in (
                        'memory_file','claim','receipt','erratum',
                        'affect_read','operator_state','session_turn',
                        'observer','embed_log','migration'
                    )),
    target_id       text not null,               -- PK of the affected row (text to hold path/uuid/bigint)
    lane            text check (lane in (
                        'crisis_lane','operations_lane','strategy_lane','background'
                    )),
    priority        text check (priority in (
                        'emergency','high','medium','low','background'
                    )),
    duration_ms     integer,                     -- wall-clock ms for the operation
    status          text not null default 'ok' check (status in ('ok','error','skipped','correction')),
    error_detail    text,                        -- populated when status='error'
    metadata        jsonb not null default '{}'::jsonb
);

comment on table public.memory_ops_log is
    'Authoritative audit spine for every write/retrieve/embed operation. trace_id NOT NULL is the hook-layer enforcement for trace_id discipline (CLAUDE.md §8 three-layer invariant, Red line §3: no silent failures on audit writes).';

comment on column public.memory_ops_log.trace_id is
    'Ingress request UUID. The calling layer generates this at request boundary and passes it through every downstream operation. The DB enforces NOT NULL; a write without a trace_id fails loud.';

comment on column public.memory_ops_log.target_id is
    'Primary key of the affected row as text. Holds memory_file path (text), claim_id (uuid), turn_id (bigint), etc. Unified as text for polymorphic ops_log across tables with different PK types.';

-- Indexes for common query patterns
create index if not exists ops_log_trace_idx
    on public.memory_ops_log (trace_id);

create index if not exists ops_log_ts_idx
    on public.memory_ops_log (ts desc);

create index if not exists ops_log_actor_idx
    on public.memory_ops_log (actor);

create index if not exists ops_log_target_idx
    on public.memory_ops_log (target_kind, target_id);

create index if not exists ops_log_status_idx
    on public.memory_ops_log (status)
    where status <> 'ok';    -- partial index — fast error audit without table scan

alter table public.memory_ops_log enable row level security;
-- service_role only (matching 0001–0006 stance).


-- =============================================================================
-- 2. Add trace_id to existing tables
--
-- Nullable with gen_random_uuid() default so:
--   (a) legacy rows keep NULL (backfill is a separate batch job),
--   (b) new rows written by callers that don't pass a trace_id get a
--       unique UUID (not ideal — the doctrine says the caller generates it —
--       but better than a NULL-column that silently drops provenance).
--
-- The doctrine goal: callers MUST pass an explicit trace_id.  The default
-- is a safety net for transitional callers, not the intended behaviour.  ATLAS
-- should monitor v_trace_coverage to see the fill rate approach 100%.
-- =============================================================================

-- 2a. memory_files
alter table public.memory_files
    add column if not exists trace_id uuid default gen_random_uuid();

comment on column public.memory_files.trace_id is
    'UUID of the ingress request that created or last modified this file. NULL on pre-0007 rows. Callers must pass explicitly; default fires for transitional callers only.';

create index if not exists memory_files_trace_idx
    on public.memory_files (trace_id)
    where trace_id is not null;


-- 2b. session_turns
alter table public.session_turns
    add column if not exists trace_id uuid default gen_random_uuid();

comment on column public.session_turns.trace_id is
    'UUID correlating this turn to the Stop/SubagentStop hook event that produced it. Same trace_id written to memory_ops_log for cross-table reconstruction.';

create index if not exists session_turns_trace_idx
    on public.session_turns (trace_id)
    where trace_id is not null;


-- 2c. claims
alter table public.claims
    add column if not exists trace_id uuid default gen_random_uuid();

comment on column public.claims.trace_id is
    'UUID of the ingress request that asserted this claim. Allows full reconstruction: ingress → ops_log entry → claim_write → claim row.';

create index if not exists claims_trace_idx
    on public.claims (trace_id)
    where trace_id is not null;


-- 2d. affect_reads
alter table public.affect_reads
    add column if not exists trace_id uuid default gen_random_uuid();

comment on column public.affect_reads.trace_id is
    'UUID of the session turn that triggered this affect read. Correlates NEVAEH pre-response reads to the ops_log turn event.';

create index if not exists affect_reads_trace_idx
    on public.affect_reads (trace_id)
    where trace_id is not null;


-- =============================================================================
-- 3. reconstruct_trace(p_trace_id) — the full-trace RPC
--
-- Returns the ordered ops_log sequence for a given trace_id.  This is the
-- single-query audit primitive: given one UUID, reconstruct what happened.
--
-- Today returns ops_log only.  As more tables gain trace_id, this function
-- will UNION-join them in (memory_files, session_turns, claims).  That
-- expansion is additive — existing callers keep working.
--
-- Returns columns that directly answer: who acted, on what, with what status,
-- in which lane, how long did it take.  The `metadata` column gives escape
-- hatches for structured detail without schema churn.
-- =============================================================================
create or replace function public.reconstruct_trace(p_trace_id uuid)
returns table (
    op_id       uuid,
    ts          timestamptz,
    actor       text,
    op_type     text,
    target_kind text,
    target_id   text,
    lane        text,
    priority    text,
    status      text,
    duration_ms integer,
    error_detail text,
    metadata    jsonb
)
language sql
stable
security definer
set search_path = public
as $$
    select
        op_id,
        ts,
        actor,
        op_type,
        target_kind,
        target_id,
        lane,
        priority,
        status,
        duration_ms,
        error_detail,
        metadata
    from public.memory_ops_log
    where trace_id = p_trace_id
    order by ts asc;
$$;

comment on function public.reconstruct_trace(uuid) is
    'Audit primitive: returns the ordered ops_log sequence for a trace_id. One query to reconstruct an entire ingress request. Expands via UNION as more tables gain trace_id in future migrations.';


-- =============================================================================
-- 4. v_trace_coverage — fill-rate sentinel for ATLAS
--
-- Shows, per table, what fraction of rows have a non-NULL trace_id.
-- ATLAS monitors this over time; as backfill jobs run and callers are updated,
-- the fill rate should approach 100%.  A stalled fill rate signals a caller
-- that hasn't been updated to pass trace_id.
-- =============================================================================
create or replace view public.v_trace_coverage as
select
    'memory_files'   as table_name,
    count(*)         as total_rows,
    count(trace_id)  as traced_rows,
    round(
        (count(trace_id)::numeric / nullif(count(*), 0)) * 100,
        1
    )                as fill_pct
from public.memory_files

union all

select
    'session_turns',
    count(*),
    count(trace_id),
    round((count(trace_id)::numeric / nullif(count(*), 0)) * 100, 1)
from public.session_turns

union all

select
    'claims',
    count(*),
    count(trace_id),
    round((count(trace_id)::numeric / nullif(count(*), 0)) * 100, 1)
from public.claims

union all

select
    'affect_reads',
    count(*),
    count(trace_id),
    round((count(trace_id)::numeric / nullif(count(*), 0)) * 100, 1)
from public.affect_reads

union all

select
    'memory_ops_log',
    count(*),
    count(trace_id),        -- always 100% (NOT NULL constraint)
    round((count(trace_id)::numeric / nullif(count(*), 0)) * 100, 1)
from public.memory_ops_log;

comment on view public.v_trace_coverage is
    'Per-table trace_id fill rate. ATLAS monitors this; fill_pct should approach 100 as callers are updated and backfill jobs run. memory_ops_log is always 100% (NOT NULL enforced).';


-- =============================================================================
-- 5. v_orphaned_ops — data-quality sentinel
--
-- Rows in memory_ops_log whose target does not exist in the expected table.
-- This catches bugs where an op was logged against a target that was never
-- actually written (e.g., a failed write that logged an op anyway).
--
-- Only checks memory_file targets today.  Expand to claims/session_turns when
-- volume justifies.  A non-empty result is a bug to investigate, not a
-- schema error.
-- =============================================================================
create or replace view public.v_orphaned_ops as
select
    ol.op_id,
    ol.trace_id,
    ol.ts,
    ol.actor,
    ol.op_type,
    ol.target_kind,
    ol.target_id,
    ol.status,
    ol.error_detail
from public.memory_ops_log ol
where ol.target_kind = 'memory_file'
  and not exists (
        select 1 from public.memory_files mf
        where mf.path = ol.target_id
  )
  and ol.status = 'ok';

comment on view public.v_orphaned_ops is
    'Ops_log rows whose target_id does not exist in the expected table. Non-empty = a write was logged but the target row was never committed. Investigate; do not delete.';


-- =============================================================================
-- BEFORE-chain for 0008
-- =============================================================================
-- 0008 candidates (decide at next check):
--   a. NEVAEH clinical layer:
--        - rupture_events (session disruption tracking)
--        - formulation per-user (JSONB case conceptualization, editable)
--        - clinician_reviews (human sign-off on formulation updates)
--        All three depend on affect_reads volume; NEVAEH must sign off on
--        the JSONB shape before we schema-lock it.
--
--   b. Per-sibling RLS policies on memory_files:
--        - owner (sibling col) can read own rows; ENVY reads all;
--          ATLAS reads kind IN ('decision','fact') only.
--        - Requires family consent decision on the consent boundary.
--        - Add AFTER NEVAEH's clinical layer so we don't split the RLS work.
--
--   c. Alembic env.py + alembic.ini:
--        - Only if a direct DB URL (not service_role HTTP) becomes available.
--        - Alembic is the migration framework for when Supabase's SQL executor
--          is too slow or we move to a self-hosted Postgres.
--        - Until then, migrate.py + SQL files is the correct substrate.
--
--   d. trace_id backfill job (ops_log entry):
--        - A Python script that sets trace_id = gen_random_uuid() on all
--          pre-0007 rows in memory_files / session_turns / claims /
--          affect_reads where trace_id IS NULL.
--        - Not a migration (no schema change); ships as a one-off script
--          in LIVE/memory_backend/backfill_trace_ids.py.
--
-- Recommended 0008: NEVAEH clinical layer (highest unblocked priority; the
-- formulation table is the schema Weaver needs to compose a therapeutic scene).
-- =============================================================================
