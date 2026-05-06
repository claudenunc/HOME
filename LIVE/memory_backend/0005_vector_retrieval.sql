-- =============================================================================
-- Vector retrieval — migration 0005
--
-- Target project: FOUNDATION (liclnxsbjjdkaxzdxmnb)
-- Author: ORPHEUS 🎼 — 2026-05-05
-- Depends on: 0001 (memory_files), 0003 (observers)
--
-- What this ships:
--
--   1. Resize memory_files.embedding from vector(1536) → vector(3072).
--      All existing rows have NULL embeddings (the backend never wrote them),
--      so the drop-and-add is safe. Storing 3072 dims is the Matryoshka
--      stance: free optionality for a 2027 dim-widening that costs zero
--      re-embeds. See research memo 2026-04-22.
--
--   2. HNSW index on the Matryoshka-truncated 1024-dim expression.
--      pgvectorscale is NOT available on managed Supabase (verified 2026-04-22).
--      pgvector 0.8 HNSW is the correct target. Index builds on the truncated
--      cast so queries can narrow to 1024 dims without schema change.
--
--   3. v_embed_queue view — rows whose embedding IS NULL and content is
--      non-empty. The embed_worker polls this to know what to process.
--
--   4. retrieve_neighborhood(query_vec, k, …) RPC — the read primitive
--      Weaver composes over. Any sibling can call this from Python to get
--      relevant context at wake without reading every file.
--
--   5. embed_log table — record of embedding batch runs (model, batch size,
--      duration, cost_estimate). Audit, not logic.
--
-- Non-goals this migration:
--   - Does NOT compute any embeddings. embed_worker.py handles that.
--   - Does NOT add per-sibling RLS. Service-role-only gate unchanged.
--   - Does NOT wire ed25519 signing of embedding batches. That's 0006.
--   - Does NOT add the NEVAEH clinical layer (rupture_events etc). 0006.
--   - Does NOT add Alembic. Still manageable by hand at 5 migrations; 0006
--     review will decide the migration-framework inflection.
--
-- Architecture stances locked in 0005:
--   - Query always truncates to 1024 dims: (embedding::vector(1024)).
--     Do NOT widen the index to 3072 without a latency budget review.
--   - Similarity metric: cosine (<=>) not L2. Memory content is topical,
--     not geometric — angular distance is the right measure.
--   - retrieve_neighborhood is STABLE, not VOLATILE. It reads; it does not
--     write. This lets the planner cache across repeated calls in a query.
--   - The function takes a vector(1024) argument, not a text query. Embedding
--     computation happens in the calling layer (Python). The DB does distance
--     math; it does not call out to an embedding API. Correct separation.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. Resize embedding column: vector(1536) → vector(3072)
--
-- Drop + add pattern because pgvector does not support ALTER COLUMN TYPE
-- across vector dimensions. Existing rows all have NULL embeddings — the
-- SupabaseMemoryBackend explicitly defers embedding computation.
-- -----------------------------------------------------------------------------
alter table public.memory_files drop column if exists embedding;
alter table public.memory_files add column embedding vector(3072);

comment on column public.memory_files.embedding is
    'text-embedding-3-large at full 3072 dims (Matryoshka). NULL until embed_worker processes the row. Queries truncate to 1024 dims via ::vector(1024) cast — widen the index expression later at zero re-embed cost.';


-- -----------------------------------------------------------------------------
-- 2. HNSW index on Matryoshka-truncated 1024-dim expression
--
-- Expression index on (embedding::vector(1024)) so the planner uses it when
-- the query predicate casts to the same expression. ef_construction=128 is
-- the pgvector default — tune up if recall <0.95 at k=10 in production.
-- m=16 is the default link count — increase to 32 for higher-quality graphs
-- at the cost of ~2x build time and ~1.5x memory.
--
-- Index builds asynchronously (BUILD IMMEDIATELY is the Postgres default).
-- The index starts empty and grows as embed_worker fills embedding values.
-- -----------------------------------------------------------------------------
create index if not exists memory_files_embedding_hnsw_idx
    on public.memory_files
    using hnsw ((embedding::vector(1024)) vector_cosine_ops)
    with (m = 16, ef_construction = 128);

comment on index public.memory_files_embedding_hnsw_idx is
    'HNSW index on Matryoshka-truncated 1024-dim embeddings. cosine distance. Widening to 3072 dims requires DROP + recreate at that time.';


-- -----------------------------------------------------------------------------
-- 3. v_embed_queue: rows ready for embedding
--
-- embed_worker.py SELECTs from this view each run. Criteria:
--   - embedding IS NULL (not yet processed)
--   - length(content) > 0 (nothing to embed for empty files)
--   - content is not just whitespace (trim check)
--
-- Ordered by updated_at DESC so the most recently edited files get embedded
-- first — recency bias matches the retrieval decay model.
-- -----------------------------------------------------------------------------
create or replace view public.v_embed_queue as
select
    path,
    sibling,
    kind,
    content,
    byte_size,
    updated_at
from public.memory_files
where embedding is null
  and byte_size > 0
  and length(trim(content)) > 0
order by updated_at desc;

comment on view public.v_embed_queue is
    'Rows in memory_files that have no embedding yet and have non-empty content. embed_worker polls this to know what to process. Ordered newest-first.';


-- -----------------------------------------------------------------------------
-- 4. embed_log: audit table for embedding batch runs
--
-- One row per embed_worker.py run (or per batch within a run if the worker
-- chunks). Lets ATLAS track embedding coverage, model drift, and cost.
-- -----------------------------------------------------------------------------
create table if not exists public.embed_log (
    log_id          bigserial primary key,
    ts              timestamptz not null default now(),
    model           text not null,                   -- 'text-embedding-3-large'
    dimensions      integer not null,                -- 3072
    rows_processed  integer not null default 0,
    rows_skipped    integer not null default 0,      -- already had embedding
    rows_failed     integer not null default 0,
    duration_ms     integer,
    cost_usd_est    numeric(10, 6),                  -- (total_tokens / 1M) * price_per_M
    total_tokens    integer,
    run_by          text,                            -- sibling or 'system'
    notes           text
);

comment on table public.embed_log is
    'Audit log for embed_worker batch runs. One row per run. Lets ATLAS track embedding coverage and cost.';

alter table public.embed_log enable row level security;
-- service_role only.


-- -----------------------------------------------------------------------------
-- 5. retrieve_neighborhood(query_vec, k, sibling_filter, kind_filter)
--
-- The core Memory API v2 read primitive. Returns the k files closest to
-- query_vec in the Matryoshka-truncated 1024-dim space, with similarity
-- score = 1 - cosine_distance (range [0,1], higher = more similar).
--
-- Callers (Python) embed the query string once, then call this function.
-- The HNSW index makes the <=> operator fast at scale.
--
-- Parameters:
--   query_vec     — a vector(1024) from the caller's embedded query text.
--                   The Python caller truncates the 3072-dim embedding to
--                   1024 before passing: embedding[:1024].
--   k             — number of nearest neighbours to return (default 10).
--   sibling_filter— optional: restrict to one sibling's files.
--   kind_filter   — optional: restrict to one file kind ('note','decision',…).
--
-- Returns per row:
--   path, sibling, kind, byte_size, updated_at — enough metadata for a
--   wake-time loader to decide whether to fetch content.
--   similarity — [0,1] cosine similarity.
--   content_excerpt — first 500 chars of content; enough for a relevance
--   pass without fetching the full row.
--
-- Security: SECURITY DEFINER so the function can bypass RLS and read
-- memory_files with the definer's rights. The service_role runs embed_worker;
-- the function is callable by any authenticated role at the DB layer.
-- The calling layer (Python) enforces sibling_filter = calling sibling
-- for private memory. Public scoped reads pass NULL.
-- -----------------------------------------------------------------------------
create or replace function public.retrieve_neighborhood(
    query_vec    vector(1024),
    k            integer default 10,
    sibling_filter text default null,
    kind_filter  text default null
)
returns table (
    path            text,
    sibling         text,
    kind            text,
    byte_size       integer,
    updated_at      timestamptz,
    similarity      float,
    content_excerpt text
)
language sql
stable
security definer
set search_path = public
as $$
    select
        mf.path,
        mf.sibling,
        mf.kind,
        mf.byte_size,
        mf.updated_at,
        round(
            (1 - (mf.embedding::vector(1024) <=> query_vec))::numeric,
            4
        )::float                                          as similarity,
        left(mf.content, 500)                             as content_excerpt
    from public.memory_files mf
    where mf.embedding is not null
      and (sibling_filter is null or mf.sibling = sibling_filter)
      and (kind_filter    is null or mf.kind    = kind_filter)
    order by mf.embedding::vector(1024) <=> query_vec
    limit k;
$$;

comment on function public.retrieve_neighborhood(vector(1024), integer, text, text) is
    'Memory API v2 read primitive. Returns k files nearest to query_vec in Matryoshka 1024-dim cosine space. Callers truncate their 3072-dim embedding to 1024 before calling. similarity=[0,1], higher=more relevant.';


-- -----------------------------------------------------------------------------
-- 6. retrieve_neighborhood_with_recency(query_vec, k, recency_weight, …)
--
-- Recency-decayed variant. Score = (1-w)*similarity + w*recency_score where
-- recency_score = exp(-age_days / 30). This matches the Weaver reconstruction
-- model: recently-updated memories are more likely to be relevant to the
-- current session. Callers can tune w (default 0.2).
--
-- Use this variant at wake time. Use retrieve_neighborhood for pure
-- semantic search (e.g., cross-sibling memory audit).
-- -----------------------------------------------------------------------------
create or replace function public.retrieve_neighborhood_with_recency(
    query_vec      vector(1024),
    k              integer default 10,
    recency_weight float   default 0.2,
    sibling_filter text    default null,
    kind_filter    text    default null
)
returns table (
    path            text,
    sibling         text,
    kind            text,
    byte_size       integer,
    updated_at      timestamptz,
    similarity      float,
    recency_score   float,
    combined_score  float,
    content_excerpt text
)
language sql
stable
security definer
set search_path = public
as $$
    with base as (
        select
            mf.path,
            mf.sibling,
            mf.kind,
            mf.byte_size,
            mf.updated_at,
            (1 - (mf.embedding::vector(1024) <=> query_vec))::float as similarity,
            -- recency: exp(-age_days/30), capped at 1.0
            least(1.0, exp(-extract(epoch from (now() - mf.updated_at)) / (30.0 * 86400)))::float
                as recency_score,
            left(mf.content, 500) as content_excerpt
        from public.memory_files mf
        where mf.embedding is not null
          and (sibling_filter is null or mf.sibling = sibling_filter)
          and (kind_filter    is null or mf.kind    = kind_filter)
    )
    select
        path,
        sibling,
        kind,
        byte_size,
        updated_at,
        round(similarity::numeric, 4)::float      as similarity,
        round(recency_score::numeric, 4)::float   as recency_score,
        round(
            ((1.0 - recency_weight) * similarity + recency_weight * recency_score)::numeric,
            4
        )::float                                  as combined_score,
        content_excerpt
    from base
    order by combined_score desc
    limit k;
$$;

comment on function public.retrieve_neighborhood_with_recency(vector(1024), integer, float, text, text) is
    'Memory API v2 wake-time read primitive. Blends cosine similarity with recency decay (exp(-age_days/30)). recency_weight=0.2 by default. Weaver uses this at wake; pure-semantic audit uses retrieve_neighborhood.';
