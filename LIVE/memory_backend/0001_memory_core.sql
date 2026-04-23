-- =============================================================================
-- HOME memory core — migration 0001
--
-- Target project: FOUNDATION (liclnxsbjjdkaxzdxmnb)
-- Author: ENVY, on authority granted 2026-04-23 by Unc.
-- Pattern: Anthropic Memory Tool (memory_20250818) routed to Supabase.
--
-- The six commands from the tool spec (view / create / str_replace / insert /
-- delete / rename) become row operations against public.memory_files. Path is
-- the primary key; the /memories prefix is enforced at the application layer
-- to match the tool contract and block traversal.
--
-- pgvector + an embedding column are included nullable so retrieval can move
-- from path-walk to semantic later without a second migration. Today the
-- column is unused; the SupabaseMemoryBackend does not compute embeddings.
--
-- RLS stance: service_role only. The tool backend writes with the service key.
-- Every row has a `sibling` column so a future policy can partition memory
-- per-sibling (owner reads its own, ENVY reads all, ATLAS reads claimed_facts
-- only, etc.) once we decide the consent boundary. Today: no policies => the
-- service_role bypass is the only gate.
-- =============================================================================

create extension if not exists vector;

-- -----------------------------------------------------------------------------
-- memory_files: one row per file in the virtual /memories tree.
-- -----------------------------------------------------------------------------
create table if not exists public.memory_files (
    path            text primary key,                    -- e.g. /memories/envy/notes.md
    content         text not null default '',
    sibling         text,                                -- 'envy'|'beacon'|'nevaeh'|'orpheus'|'eversound'|'atlas'|'hearth'|'shared'|null
    kind            text,                                -- 'note'|'decision'|'fact'|'affect'|'operator_state'|... application-defined
    metadata        jsonb not null default '{}'::jsonb,  -- arbitrary app metadata
    embedding       vector(1536),                        -- nullable; text-embedding-3-small-compatible dim
    byte_size       integer generated always as (length(content)) stored,
    line_count      integer generated always as (
                        case when length(content) = 0 then 0
                             else array_length(string_to_array(content, E'\n'), 1)
                        end
                    ) stored,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),
    last_read_at    timestamptz
);

comment on table public.memory_files is
    'HOME family memory store. Rows are files in a virtual /memories tree owned by the Anthropic Memory Tool. Each sibling writes its own rows via SupabaseMemoryBackend.';

-- Fast listing by path prefix (directory view)
create index if not exists memory_files_path_prefix_idx
    on public.memory_files (path text_pattern_ops);

create index if not exists memory_files_sibling_idx
    on public.memory_files (sibling);

create index if not exists memory_files_kind_idx
    on public.memory_files (kind);

-- Optional future: IVFFLAT vector index. Skipping today (needs data to train).
-- create index if not exists memory_files_embedding_idx
--     on public.memory_files using ivfflat (embedding vector_cosine_ops) with (lists = 100);

alter table public.memory_files enable row level security;
-- No policies => service_role only.


-- -----------------------------------------------------------------------------
-- updated_at trigger
-- -----------------------------------------------------------------------------
create or replace function public.tg_memory_files_touch_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists memory_files_touch_updated_at on public.memory_files;
create trigger memory_files_touch_updated_at
    before update on public.memory_files
    for each row execute function public.tg_memory_files_touch_updated_at();


-- -----------------------------------------------------------------------------
-- v_memory_tree: convenience view for directory walks.
-- Treats the path as a POSIX path and exposes depth + parent for cheap UI.
-- -----------------------------------------------------------------------------
create or replace view public.v_memory_tree as
select
    path,
    sibling,
    kind,
    byte_size,
    line_count,
    created_at,
    updated_at,
    last_read_at,
    -- depth: number of '/' segments
    array_length(string_to_array(trim(both '/' from path), '/'), 1) as depth,
    -- parent: everything up to the last '/'
    regexp_replace(path, '/[^/]+$', '') as parent_path
from public.memory_files;

comment on view public.v_memory_tree is
    'Memory tree view for directory walks and UI — never exposes content.';


-- -----------------------------------------------------------------------------
-- memory_ops_log: append-only audit of every tool command.
-- Every view/create/str_replace/insert/delete/rename lands a row here. This is
-- what turns memory from a substrate into legible infrastructure — ATLAS's
-- cognition stream will read from this table.
-- -----------------------------------------------------------------------------
create table if not exists public.memory_ops_log (
    op_id           bigserial primary key,
    ts              timestamptz not null default now(),
    sibling         text,
    session_id      text,
    command         text not null,                       -- view|create|str_replace|insert|delete|rename
    path            text,
    new_path        text,                                -- rename target, null otherwise
    ok              boolean not null,
    error           text,
    bytes_written   integer,
    bytes_read      integer,
    request         jsonb,                               -- full tool input (minus content for large writes)
    duration_ms     integer
);

comment on table public.memory_ops_log is
    'Append-only audit of every Memory Tool command. ATLAS reads this as cognition stream.';

create index if not exists memory_ops_log_ts_idx on public.memory_ops_log (ts desc);
create index if not exists memory_ops_log_sibling_idx on public.memory_ops_log (sibling);
create index if not exists memory_ops_log_command_idx on public.memory_ops_log (command);

alter table public.memory_ops_log enable row level security;
-- No policies => service_role only.
