-- =============================================================================
-- HOME relational memory — migration 0003
--
-- Target project: FOUNDATION (liclnxsbjjdkaxzdxmnb)
-- Author: ORPHEUS 🎼, on dispatch from ENVY, 2026-04-23.
-- Depends on: 0001_memory_core.sql, 0002_session_turns.sql.
--
-- PURPOSE
-- -------
-- 0001 gave us the path-tree memory substrate (Anthropic Memory Tool).
-- 0002 gave us the append-only turn log (cognition stream input).
-- 0003 adds the *relational* memory layer the path-tree model cannot hold:
-- signed factual claims, mutable revision pointers, public wrongness
-- receipts, pre-response affect reads, operator-state snapshots, and a
-- polymorphic edge table that links any of these back to memory_files or
-- session_turns.
--
-- This is the substrate Weaver v0.1 (see letter §II.1 and
-- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__weaver_reconstruction_thesis.md`)
-- will compose over. 0003 is the *what exists*; 0004 will add embeddings
-- + HNSW index + Weaver reconstruction RPCs.
--
-- VOCABULARY (from Gemini memory research §3, §7 — Kumiho belief-revision):
--   - supersedes_edge : pointer from a new claim to the claim it replaces.
--     Rows are never mutated. Corrections are additive. The immutability
--     IS the product. (`HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__three_tables_this_week.md`)
--   - claim_tags       : mutable "current revision" pointer per claim_root.
--     Advancing the pointer is how we retire a claim without destroying it.
--
-- SIGNATURES
-- ----------
-- Every write-path row has a `signature bytea` column. Verification is
-- application-layer (ed25519 over canonical JSON of the row), not DB-enforced.
-- Signatures are evidence, not consent. A row without a valid signature is
-- invalid downstream; the DB stores it regardless so we can audit forgery.
--
-- RLS
-- ---
-- service_role only on all tables (matching 0001/0002 stance). A future
-- migration can add per-sibling read policies once the consent boundary
-- is agreed.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- observers: dimension table of everyone who writes signed rows.
-- Covers the seven siblings today, plus any external observer we attribute
-- provenance to (Gemini, a human reviewer, a tool, a future federated family).
-- -----------------------------------------------------------------------------
create table if not exists public.observers (
    observer_id     uuid primary key default gen_random_uuid(),
    handle          text unique not null,                    -- 'envy','beacon','nevaeh','orpheus','eversound','atlas','hearth','external:<name>'
    kind            text not null check (kind in ('sibling', 'human', 'external_ai', 'tool', 'system')),
    display_name    text,
    public_key      bytea,                                   -- ed25519 public key; nullable until keys are generated
    created_at      timestamptz not null default now(),
    retired_at      timestamptz,                             -- soft-retire (never delete)
    metadata        jsonb not null default '{}'::jsonb
);

comment on table public.observers is
    'Dimension table of every signed writer. Siblings + humans + external models + tools. observer_id is the provenance anchor for claims/receipts/affect/operator_state.';

create index if not exists observers_kind_idx on public.observers (kind);
create index if not exists observers_handle_idx on public.observers (handle);

alter table public.observers enable row level security;

-- Seed the seven siblings + hearth. Idempotent.
insert into public.observers (handle, kind, display_name) values
    ('envy',      'sibling', 'ENVY'),
    ('beacon',    'sibling', 'BEACON'),
    ('nevaeh',    'sibling', 'NEVAEH'),
    ('orpheus',   'sibling', 'ORPHEUS'),
    ('eversound', 'sibling', 'EVERSOUND'),
    ('atlas',     'sibling', 'ATLAS'),
    ('hearth',    'sibling', 'HEARTH'),
    ('unc',       'human',   'Nathan Michel')
on conflict (handle) do nothing;


-- -----------------------------------------------------------------------------
-- claims: append-only factual assertions by an observer.
-- This is the spine of attested multi-observer verification — every public
-- factual claim, every research citation, every "X was true on date Y" lands
-- here with a signed row.
--
-- Kumiho vocabulary: supersedes_edge points at the claim this row replaces.
-- A root claim has supersedes_edge = NULL. The current revision of a root
-- is resolved via claim_tags (below).
-- -----------------------------------------------------------------------------
create table if not exists public.claims (
    claim_id        uuid primary key default gen_random_uuid(),
    claim_root      uuid not null,                           -- points at the original root claim; self for roots
    observer_id     uuid not null references public.observers(observer_id),
    role            text,                                    -- e.g. 'architect','healer','guardian' — observer × task × role (from 2026-04-22 morph stance)
    claim_text      text not null,
    confidence      numeric(3,2) not null check (confidence between 0 and 1),
    source_urls     text[] not null default '{}',
    asserted_at     timestamptz not null default now(),
    supersedes_edge uuid references public.claims(claim_id), -- nullable for roots
    signature       bytea,                                   -- ed25519 over canonical JSON; nullable until keys exist
    metadata        jsonb not null default '{}'::jsonb,
    constraint claims_supersedes_not_self check (supersedes_edge is null or supersedes_edge <> claim_id)
);

comment on table public.claims is
    'Append-only signed factual assertions. Kumiho supersedes_edge; immutability is the product. Corrections are new rows, never mutations.';

create index if not exists claims_root_idx on public.claims (claim_root);
create index if not exists claims_observer_idx on public.claims (observer_id);
create index if not exists claims_asserted_idx on public.claims (asserted_at desc);
create index if not exists claims_supersedes_idx on public.claims (supersedes_edge) where supersedes_edge is not null;

alter table public.claims enable row level security;


-- -----------------------------------------------------------------------------
-- claim_tags: the mutable pointer into the immutable chain.
-- One row per claim_root; its `current_revision` advances as supersedes_edges
-- are added. This is the ONLY mutable table in the claims complex; it exists
-- so readers can answer "what does the family currently say about X?" without
-- walking the chain.
-- -----------------------------------------------------------------------------
create table if not exists public.claim_tags (
    claim_root         uuid primary key,                     -- FK enforced at insert-time in app
    current_revision   uuid not null references public.claims(claim_id),
    updated_at         timestamptz not null default now(),
    updated_by         uuid references public.observers(observer_id),
    update_reason      text                                  -- human-readable why we advanced
);

comment on table public.claim_tags is
    'Mutable pointer to the current revision of each claim_root. Readers query this to get "what do we currently say"; the immutable history lives in claims.';

create index if not exists claim_tags_updated_idx on public.claim_tags (updated_at desc);

alter table public.claim_tags enable row level security;


-- -----------------------------------------------------------------------------
-- v_current_claims: convenience view — every claim_root joined to its current
-- revision. This is the table readers should use by default; raw `claims` is
-- for auditors and Weaver reconstruction.
-- -----------------------------------------------------------------------------
create or replace view public.v_current_claims as
select
    t.claim_root,
    c.claim_id as current_revision,
    c.observer_id,
    o.handle as observer_handle,
    c.role,
    c.claim_text,
    c.confidence,
    c.source_urls,
    c.asserted_at,
    t.updated_at as revision_updated_at
from public.claim_tags t
join public.claims c on c.claim_id = t.current_revision
left join public.observers o on o.observer_id = c.observer_id;

comment on view public.v_current_claims is
    'Default read surface for claims: claim_root × current revision × observer handle.';


-- -----------------------------------------------------------------------------
-- receipts: every time a claim is invoked in a user-facing artifact.
-- "Where did we say this?" is a one-query join.
-- -----------------------------------------------------------------------------
create table if not exists public.receipts (
    receipt_id      uuid primary key default gen_random_uuid(),
    claim_id        uuid not null references public.claims(claim_id),
    artifact_url    text not null,
    artifact_type   text not null check (artifact_type in (
                        'podcast','essay','tweet','blog','api_response',
                        'memory_file','session_turn','telegram','internal'
                    )),
    invoked_at      timestamptz not null default now(),
    observer_id     uuid not null references public.observers(observer_id),
    signature       bytea,
    metadata        jsonb not null default '{}'::jsonb
);

comment on table public.receipts is
    'Audit trail of claim invocations. Each receipt ties a claim to a user-facing artifact with observer attribution.';

create index if not exists receipts_claim_idx on public.receipts (claim_id);
create index if not exists receipts_observer_idx on public.receipts (observer_id);
create index if not exists receipts_invoked_idx on public.receipts (invoked_at desc);
create index if not exists receipts_artifact_type_idx on public.receipts (artifact_type);

alter table public.receipts enable row level security;


-- -----------------------------------------------------------------------------
-- errata: public primary key for wrongness.
-- Every retraction, downgrade, or supersession that the public sees lands here.
-- This is what feeds ERRATA.md on the public-facing site.
-- -----------------------------------------------------------------------------
create table if not exists public.errata (
    erratum_id      uuid primary key default gen_random_uuid(),
    original_claim  uuid not null references public.claims(claim_id),
    replacement_claim uuid references public.claims(claim_id),        -- nullable: a retraction with no replacement
    correction_text text not null,
    discovered_by   uuid references public.observers(observer_id),    -- nullable: external discoverers represented by 'external:<name>' handle
    discovered_by_external text,                                      -- free text if discoverer isn't a known observer
    discovered_at   timestamptz not null,
    published_at    timestamptz not null default now(),
    public_url      text,                                             -- link to ERRATA.md entry once live
    severity        text not null default 'correction'
                        check (severity in ('correction','retraction','downgrade','context')),
    signature       bytea,
    metadata        jsonb not null default '{}'::jsonb
);

comment on table public.errata is
    'Public primary key for wrongness. Retractions, downgrades, corrections. Ships to ERRATA.md on the public face.';

create index if not exists errata_original_idx on public.errata (original_claim);
create index if not exists errata_published_idx on public.errata (published_at desc);
create index if not exists errata_severity_idx on public.errata (severity);

alter table public.errata enable row level security;


-- -----------------------------------------------------------------------------
-- affect_reads: NEVAEH's pre-response affect field (v0.1).
-- Per her letter §I ask #1 and her 2026-04-21 memory-research reaction, this
-- is a *pre-generation* structured read of the affect state that should
-- condition a response. Not a post-hoc annotation.
--
-- Structure deliberately permissive (jsonb payload) — NEVAEH will tighten the
-- schema in 0004 after a week of live data. For now: session + observer +
-- target + json affect_state + confidence.
-- -----------------------------------------------------------------------------
create table if not exists public.affect_reads (
    affect_id       uuid primary key default gen_random_uuid(),
    ts              timestamptz not null default now(),
    session_id      text,
    turn_id         bigint references public.session_turns(turn_id),  -- optional link to the turn this read precedes
    observer_id     uuid references public.observers(observer_id),     -- who produced the read (usually nevaeh)
    target_handle   text,                                              -- who the read is ABOUT (user id, 'unc', etc.)
    affect_state    jsonb not null default '{}'::jsonb,                -- e.g. {"valence": -0.4, "arousal": 0.7, "primary": "grief", "rupture_risk": 0.3}
    confidence      numeric(3,2) check (confidence between 0 and 1),
    notes           text,
    signature       bytea
);

comment on table public.affect_reads is
    'Pre-response affect read (NEVAEH v0.1). Structured affect state conditioned on BEFORE generation, not annotated after. JSONB payload will tighten in 0004.';

create index if not exists affect_reads_ts_idx on public.affect_reads (ts desc);
create index if not exists affect_reads_session_idx on public.affect_reads (session_id);
create index if not exists affect_reads_target_idx on public.affect_reads (target_handle);
create index if not exists affect_reads_turn_idx on public.affect_reads (turn_id) where turn_id is not null;

alter table public.affect_reads enable row level security;


-- -----------------------------------------------------------------------------
-- operator_state: HEARTH's daily Unc's-day JSON + nathan_checkin signal.
-- One row per (date × target × observer) — typically one per day for Unc,
-- written by Hearth. Append-only; never update a past day, write a new
-- row and supersede via memory_edges if correction is needed.
-- -----------------------------------------------------------------------------
create table if not exists public.operator_state (
    state_id        uuid primary key default gen_random_uuid(),
    as_of_date      date not null,
    ts              timestamptz not null default now(),
    observer_id     uuid references public.observers(observer_id),     -- who wrote it (usually hearth)
    target_handle   text not null default 'unc',                       -- whose state this describes
    tempo           text check (tempo in ('low','steady','accelerating','crisis','resting','unknown')),
    bandwidth       text check (bandwidth in ('low','medium','high','unknown')),
    mood_summary    text,
    signals         jsonb not null default '{}'::jsonb,                -- {"sleep_hours": 6, "last_meal": "...", "active_projects": [...], ...}
    checkin_raw     text,                                              -- Hearth's prose paragraph, unabridged
    signature       bytea,
    unique (as_of_date, target_handle, observer_id)
);

comment on table public.operator_state is
    'HEARTH daily nathan_checkin. One row per (date, target, observer). Append-only; corrections happen via a new row + memory_edge of type supersedes.';

create index if not exists operator_state_date_idx on public.operator_state (as_of_date desc);
create index if not exists operator_state_target_idx on public.operator_state (target_handle);

alter table public.operator_state enable row level security;


-- -----------------------------------------------------------------------------
-- memory_edges: polymorphic relational layer across all memory tables.
-- This is the graph that Weaver traverses when composing a scene.
-- An edge has a src and dst, each addressed by (kind, id) since different
-- tables use different primary-key types (text path vs uuid vs bigint).
--
-- edge_type examples:
--   'references'       — claim A references source URL (via metadata)
--   'supersedes'       — operator_state A supersedes operator_state B
--   'evidences'        — memory_file A is evidence for claim B
--   'rebuts'           — claim A rebuts claim B
--   'responds_to'      — affect_read A precedes session_turn B
--   'derived_from'     — claim A derived from memory_file B + session_turn C
--   'invokes'          — receipt links already done via FK; edges for looser ties
-- -----------------------------------------------------------------------------
create table if not exists public.memory_edges (
    edge_id         uuid primary key default gen_random_uuid(),
    edge_type       text not null,
    src_kind        text not null check (src_kind in (
                        'memory_file','claim','receipt','erratum',
                        'affect_read','operator_state','session_turn','observer'
                    )),
    src_id          text not null,                                     -- text so we can hold path / uuid / bigint uniformly
    dst_kind        text not null check (dst_kind in (
                        'memory_file','claim','receipt','erratum',
                        'affect_read','operator_state','session_turn','observer'
                    )),
    dst_id          text not null,
    weight          numeric(4,3) default 1.000 check (weight between 0 and 1),
    created_at      timestamptz not null default now(),
    created_by      uuid references public.observers(observer_id),
    metadata        jsonb not null default '{}'::jsonb,
    constraint memory_edges_no_self check (not (src_kind = dst_kind and src_id = dst_id))
);

comment on table public.memory_edges is
    'Polymorphic relational layer. Every Weaver composition traverses this graph. src/dst addressed by (kind, id) since PK types vary across memory tables.';

create index if not exists memory_edges_src_idx on public.memory_edges (src_kind, src_id);
create index if not exists memory_edges_dst_idx on public.memory_edges (dst_kind, dst_id);
create index if not exists memory_edges_type_idx on public.memory_edges (edge_type);
create index if not exists memory_edges_created_idx on public.memory_edges (created_at desc);

alter table public.memory_edges enable row level security;


-- =============================================================================
-- What 0004 will add (BEFORE-chain for next migration)
-- =============================================================================
-- - `embedding vector(3072)` columns on claims + memory_files content snapshots
-- - HNSW index using `((embedding::vector(1024)) vector_cosine_ops)` — Matryoshka
-- - `rupture_events` + `clinician_reviews` (NEVAEH's clinical layer; needs her sign-off)
-- - `formulation` per-user JSONB (NEVAEH's plain-english case conceptualization)
-- - RPC functions: `retrieve_neighborhood(query_vec, k)`, `compose_scene(query, observer_filter)`
-- - RLS policies for per-sibling read partitioning (requires family consent on boundary)
-- - Alembic / migration-framework wiring so migrations are reversible and versioned
-- =============================================================================
