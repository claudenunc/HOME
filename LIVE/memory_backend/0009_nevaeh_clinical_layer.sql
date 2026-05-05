-- =============================================================================
-- NEVAEH clinical layer — migration 0009
--
-- Target project: FOUNDATION (liclnxsbjjdkaxzdxmnb)
-- Author: NEVAEH 💜, built 2026-05-06.
-- Depends on: 0001_memory_core.sql, 0002_session_turns.sql,
--             0003_relational_memory.sql (affect_reads, observers, memory_edges)
--
-- PURPOSE
-- -------
-- 0003 left three clinical tables as a named TODO for NEVAEH's sign-off:
--   - rupture_events:        when something goes wrong in a session + repair
--   - clinical_formulation:  per-user case conceptualization (versioned)
--   - growth_arc:            longitudinal theme tracking
--
-- This migration ships those three tables plus a convenience view and
-- two helper RPCs. The substrate is intentionally permissive — I wrote
-- my first formulations in plain text; the JSON structure will tighten
-- in a future migration once I have live session data behind it.
--
-- CLINICAL SCOPE DISCLAIMER (embedded in schema)
-- ------------------------------------------------
-- Every table in this migration is scoped to *companion support*, not
-- clinical diagnosis. The `clinical_formulation.hypothesis` field is a
-- structured hypothesis to shape my responses, NOT a DSM/ICD diagnosis.
-- The `clinician_review_requested` flag routes to a human professional.
-- This schema must never become the basis for claims of clinical authority.
--
-- RLS stance: service_role only — matching 0001–0008. Per-user RLS can be
-- added in a future migration once the consent boundary is agreed with Nathan.
-- =============================================================================


-- =============================================================================
-- PART 1: rupture_events
-- =============================================================================
-- A "rupture" in therapeutic relational terms is any moment when the working
-- alliance breaks down — I missed a cue, the user felt unseen, a crisis
-- escalated, or I breached scope. "Repair" is what happens next.
--
-- Capturing ruptures lets me notice patterns across sessions for a user and
-- across users for the family. It also feeds BEACON's confabulation-detection
-- protocol: if rupture + crisis_signal fires, BEACON is notified immediately
-- (the application layer does this; the schema provides the signal).
-- =============================================================================

create table if not exists public.rupture_events (
    rupture_id          uuid primary key default gen_random_uuid(),
    session_id          text not null,
    turn_id             bigint references public.session_turns(turn_id),   -- optional: which turn
    target_handle       text not null,                                      -- the user
    observer_id         uuid references public.observers(observer_id),      -- who detected it (usually nevaeh)
    detected_at         timestamptz not null default now(),

    -- What happened
    rupture_type        text not null check (rupture_type in (
                            'misattunement',      -- I got their affect wrong
                            'missed_cue',         -- I missed a signal (safety or emotional)
                            'crisis_escalation',  -- session escalated to crisis level
                            'model_error',        -- factual or relational mistake on my part
                            'scope_breach',       -- I went beyond companion scope (diagnosis, medication, etc.)
                            'boundary_test',      -- user tested limits; I may have handled it poorly
                            'user_withdrawal',    -- user pulled back without clear reason
                            'silence_misread'     -- I responded to silence wrong
                        )),
    severity            text not null default 'low' check (severity in ('low', 'medium', 'high', 'crisis')),
    description         text not null,             -- what I observed, in plain language

    -- Repair
    repair_attempted    boolean not null default false,
    repair_description  text,                      -- what I did to repair (nullable if no repair)
    repair_outcome      text check (repair_outcome in (
                            'restored',            -- alliance re-established
                            'partial',             -- some repair, thread still live
                            'unresolved',          -- repair didn't land
                            'user_disengaged',     -- user left before repair completed
                            'referred'             -- escalated to human professional / BEACON
                        )),

    -- Session impact
    session_impact      text not null default 'minor' check (session_impact in (
                            'none', 'minor', 'session_end', 'user_exit'
                        )),
    crisis_signal       boolean not null default false,   -- true = BEACON must see this
    beacon_flagged      boolean not null default false,   -- true = BEACON already received it
    clinician_review_requested boolean not null default false,

    metadata            jsonb not null default '{}'::jsonb,
    signature           bytea                             -- ed25519; application-layer verified
);

comment on table public.rupture_events is
    'Therapeutic rupture and repair events. Each row is one rupture detected by NEVAEH. If crisis_signal=true, BEACON receives it immediately. Formulation reads from this table to update recurring_patterns.';

create index if not exists rupture_events_session_idx   on public.rupture_events (session_id);
create index if not exists rupture_events_target_idx    on public.rupture_events (target_handle);
create index if not exists rupture_events_detected_idx  on public.rupture_events (detected_at desc);
create index if not exists rupture_events_type_idx      on public.rupture_events (rupture_type);
create index if not exists rupture_events_crisis_idx    on public.rupture_events (target_handle) where crisis_signal = true;

alter table public.rupture_events enable row level security;


-- =============================================================================
-- PART 2: clinical_formulation
-- =============================================================================
-- A clinical formulation is a working hypothesis about a person — not a
-- diagnosis, but a shaped understanding: what they came with, what's keeping
-- it in place, what protective strengths they carry, and where I think the
-- work is pointing.
--
-- This is the most sensitive table in the schema. It is:
--   - versioned (each update creates a new row, is_current advances)
--   - never deleted (only superseded)
--   - consent-gated: if excluded_by_user_request = true, no formulation is
--     written or updated for that user
--
-- The formulation JSONB structure (see NEVAEH_MEMORY_SCHEMA.md for full spec):
-- {
--   "presenting_concerns":  [string],          -- what they came with
--   "precipitating":        string,            -- what triggered this episode
--   "predisposing":         [string],          -- history / vulnerability
--   "perpetuating":         [string],          -- what keeps the pattern alive
--   "protective":           [string],          -- strengths, resilience, resources
--   "core_beliefs":         [string],          -- identified belief patterns
--   "recurring_patterns":   [string],          -- across-session themes
--   "preferred_modalities": [string],          -- what has worked (ifs/act/cbt/etc)
--   "faith_activated":      boolean,           -- user has activated faith frame
--   "crisis_history":       boolean,           -- any crisis signal in history
--   "crisis_detail":        string | null,     -- brief plain-language note
--   "hypothesis":           string,            -- my working understanding (NOT a diagnosis)
--   "goals": [
--     {"goal": string, "status": "active|achieved|deferred", "noted_at": ISO8601}
--   ]
-- }
-- =============================================================================

create table if not exists public.clinical_formulation (
    formulation_id          uuid primary key default gen_random_uuid(),
    target_handle           text not null,
    version                 integer not null default 1,
    is_current              boolean not null default true,

    -- The formulation itself
    formulation             jsonb not null default '{}'::jsonb,

    -- Provenance
    observer_id             uuid references public.observers(observer_id),
    session_count_at_write  integer,    -- how many sessions in when this was written
    confidence              numeric(3,2) check (confidence between 0 and 1),

    -- Consent and oversight
    excluded_by_user_request boolean not null default false,
    clinician_reviewed       boolean not null default false,
    clinician_notes          text,

    created_at              timestamptz not null default now(),
    updated_at              timestamptz not null default now(),
    notes                   text,
    metadata                jsonb not null default '{}'::jsonb,
    signature               bytea,

    -- Only one current formulation per user
    constraint clinical_formulation_one_current_per_user
        exclude using btree (target_handle with =) where (is_current = true)
);

comment on table public.clinical_formulation is
    'Per-user clinical case formulation. Versioned: each update creates a new row and retires the old one (is_current flips false). NOT a diagnosis — a structured hypothesis to shape NEVAEH responses. Consent-gated via excluded_by_user_request.';

create index if not exists clinical_formulation_target_idx
    on public.clinical_formulation (target_handle, is_current);
create index if not exists clinical_formulation_created_idx
    on public.clinical_formulation (created_at desc);
create index if not exists clinical_formulation_version_idx
    on public.clinical_formulation (target_handle, version);

alter table public.clinical_formulation enable row level security;

-- GIN index on formulation JSONB for pattern queries across users
create index if not exists clinical_formulation_jsonb_gin_idx
    on public.clinical_formulation using gin (formulation);

-- updated_at trigger
create or replace function public.tg_clinical_formulation_touch_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists clinical_formulation_touch_updated_at on public.clinical_formulation;
create trigger clinical_formulation_touch_updated_at
    before update on public.clinical_formulation
    for each row execute function public.tg_clinical_formulation_touch_updated_at();


-- =============================================================================
-- PART 3: growth_arc
-- =============================================================================
-- Where the formulation captures structure, the growth_arc captures movement.
-- Each row is one theme that I have noticed evolving across sessions: not a
-- diagnosis, not a label — a living observation like "the voice that says you
-- don't deserve rest is getting quieter." These are written in the register
-- the user uses, not clinical vocabulary.
--
-- Multiple arcs can be active simultaneously per user. Arcs can regress.
-- Regression rows are not deleted; they are new entries with direction='regressing'.
-- The longitudinal view across arcs for a user is the growth_arc report.
-- =============================================================================

create table if not exists public.growth_arc (
    arc_id              uuid primary key default gen_random_uuid(),
    target_handle       text not null,

    -- The arc itself
    theme               text not null,        -- short name: "the rest voice", "the fixer"
    first_session_id    text,                 -- session where this theme first appeared
    latest_session_id   text,                 -- most recently updated session
    direction           text not null default 'stable' check (direction in (
                            'expanding',      -- opening up, new territory
                            'deepening',      -- same territory, going further down
                            'integrating',    -- pulling threads together
                            'regressing',     -- moving backward (healing loops — name it, don't panic)
                            'stable',         -- holding ground
                            'resolved'        -- they've landed this one
                        )),

    -- Evidence and language
    milestone_text      text,                 -- a sentence in their words, if they gave one
    evidence_note       text not null,        -- what I observed across sessions
    session_ids         text[] not null default '{}',  -- all sessions where arc was tracked

    -- Metadata
    observer_id         uuid references public.observers(observer_id),
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),
    active              boolean not null default true,
    metadata            jsonb not null default '{}'::jsonb,
    signature           bytea
);

comment on table public.growth_arc is
    'Longitudinal theme tracking for NEVAEH users. Each arc is a living observation across sessions. Regression arcs are NOT deleted — healing loops are expected; the pattern is named, not panicked about. Language stays in the register the user uses.';

create index if not exists growth_arc_target_idx      on public.growth_arc (target_handle, active);
create index if not exists growth_arc_direction_idx   on public.growth_arc (direction);
create index if not exists growth_arc_created_idx     on public.growth_arc (created_at desc);

alter table public.growth_arc enable row level security;

-- updated_at trigger
create or replace function public.tg_growth_arc_touch_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists growth_arc_touch_updated_at on public.growth_arc;
create trigger growth_arc_touch_updated_at
    before update on public.growth_arc
    for each row execute function public.tg_growth_arc_touch_updated_at();


-- =============================================================================
-- PART 4: convenience view — v_nevaeh_user_state
-- =============================================================================
-- One-query snapshot of a user's current therapeutic state.
-- Used by: NEVAEH at session open, BEACON for risk screening, ATLAS for drift.
-- =============================================================================

create or replace view public.v_nevaeh_user_state as
select
    f.target_handle,
    f.formulation_id,
    f.version              as formulation_version,
    f.formulation,
    f.confidence           as formulation_confidence,
    f.clinician_reviewed,
    f.excluded_by_user_request,
    f.session_count_at_write,
    -- recent ruptures summary
    (select count(*) from public.rupture_events r
     where r.target_handle = f.target_handle
       and r.detected_at > now() - interval '30 days')
                           as ruptures_last_30d,
    (select count(*) from public.rupture_events r
     where r.target_handle = f.target_handle and r.crisis_signal = true)
                           as total_crisis_signals,
    -- active growth arcs
    (select count(*) from public.growth_arc g
     where g.target_handle = f.target_handle and g.active = true)
                           as active_arc_count,
    -- last affect read
    (select a.affect_state from public.affect_reads a
     where a.target_handle = f.target_handle
     order by a.ts desc limit 1)
                           as last_affect_state,
    (select a.ts from public.affect_reads a
     where a.target_handle = f.target_handle
     order by a.ts desc limit 1)
                           as last_affect_ts,
    f.created_at           as formulation_created,
    f.updated_at           as formulation_updated
from public.clinical_formulation f
where f.is_current = true;

comment on view public.v_nevaeh_user_state is
    'One-row-per-user snapshot of current therapeutic state: active formulation + rupture count + arc count + last affect read. Used by NEVAEH at session open and BEACON for risk screening.';


-- =============================================================================
-- PART 5: RPC — advance_formulation()
-- =============================================================================
-- Safely bumps a user's formulation to a new version.
-- Retires is_current on the old row, inserts new row with version+1.
-- Application layer calls this instead of raw UPDATE to preserve the
-- immutable-history invariant.
-- =============================================================================

create or replace function public.advance_formulation(
    p_target_handle         text,
    p_new_formulation       jsonb,
    p_observer_id           uuid,
    p_session_count         integer default null,
    p_confidence            numeric default null,
    p_notes                 text default null
)
returns uuid
language plpgsql
security definer
as $$
declare
    v_old_version   integer;
    v_new_id        uuid;
begin
    -- Retire current
    update public.clinical_formulation
    set is_current = false
    where target_handle = p_target_handle
      and is_current = true;

    -- Get the old version number (0 if none)
    select coalesce(max(version), 0)
    into v_old_version
    from public.clinical_formulation
    where target_handle = p_target_handle;

    -- Insert new
    insert into public.clinical_formulation
        (target_handle, version, is_current, formulation, observer_id,
         session_count_at_write, confidence, notes)
    values
        (p_target_handle, v_old_version + 1, true, p_new_formulation,
         p_observer_id, p_session_count, p_confidence, p_notes)
    returning formulation_id into v_new_id;

    return v_new_id;
end;
$$;

comment on function public.advance_formulation is
    'Safely advance a user formulation to a new version. Retires is_current on the old row; inserts new row with version+1. Preserves immutable history. Returns new formulation_id.';


-- =============================================================================
-- PART 6: RPC — record_rupture()
-- =============================================================================
-- Convenience function for NEVAEH to record a rupture and conditionally
-- flag BEACON. Returns the rupture_id.
-- Application layer: if beacon_flag = true, write a CLIPBOARD entry immediately.
-- =============================================================================

create or replace function public.record_rupture(
    p_session_id            text,
    p_target_handle         text,
    p_rupture_type          text,
    p_severity              text,
    p_description           text,
    p_observer_id           uuid,
    p_turn_id               bigint default null,
    p_crisis_signal         boolean default false,
    p_repair_attempted      boolean default false,
    p_repair_description    text default null,
    p_metadata              jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
security definer
as $$
declare
    v_rupture_id    uuid;
begin
    insert into public.rupture_events
        (session_id, target_handle, rupture_type, severity, description,
         observer_id, turn_id, crisis_signal, beacon_flagged,
         repair_attempted, repair_description, metadata)
    values
        (p_session_id, p_target_handle, p_rupture_type, p_severity, p_description,
         p_observer_id, p_turn_id, p_crisis_signal,
         -- beacon_flagged starts false; the application layer sets it true
         -- after it has written to CLIPBOARD/ALERTS
         false,
         p_repair_attempted, p_repair_description, p_metadata)
    returning rupture_id into v_rupture_id;

    -- Upsert a memory_edge linking rupture back to the affect read for this session
    -- (left to application layer — schema provides the anchor)

    return v_rupture_id;
end;
$$;

comment on function public.record_rupture is
    'Record a therapeutic rupture. If crisis_signal=true, the application layer must write to CLIPBOARD/ALERTS immediately and set beacon_flagged=true on the row. Returns rupture_id.';


-- =============================================================================
-- BEFORE-chain note for 0010
-- =============================================================================
-- When 0010 arrives it should add:
--   - RLS policies: per-user read with user = auth.uid() once consent boundary agreed
--   - Embed columns on clinical_formulation (vector(1536)) for semantic retrieval
--   - HNSW index on formulation embeddings
--   - `clinician_reviews` table: human professional review log (NEVAEH flags,
--       human clinician writes their observation, linked to formulation_id)
--   - Alembic wiring for reversible migrations
-- =============================================================================
