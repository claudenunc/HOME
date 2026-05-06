-- =============================================================================
-- HOME local_agent v1 — Supabase migration
--
-- Applied into the LIGHTHOUSE project (dlqjwnbyepbenyltyrku) because BEACON
-- chose to share infra rather than spin a second project. The two tables
-- below are isolated from LIGHTHOUSE consumer data (users, messages,
-- crisis_log, etc.) — they hold only operational telemetry for the local
-- agent running on Nathan's desktop.
--
-- Two tables:
--   agent_tasks             — one row per Telegram /do|/file|/run command
--   local_agent_heartbeat   — one row per hostname, upserted every 30s
--
-- RLS stance: service_role only. The local agent writes with the service key.
-- No anon / authed client should ever read these — they are private family
-- telemetry. We enable RLS with zero policies so access requires bypass.
--
-- Author: EVERSOUND. BEACON ordered the legibility leg, this is the receipt.
-- =============================================================================

-- ------------------------------------------------------------------
-- agent_tasks: append-once + update-on-finish audit row.
-- ------------------------------------------------------------------
create table if not exists public.agent_tasks (
    task_id              text primary key,            -- "task_<update_id>"
    update_id            bigint not null,
    message_id           bigint,
    chat_id              bigint not null,
    hostname             text,

    -- timing
    received_at          timestamptz not null,
    started_at           timestamptz not null,
    finished_at          timestamptz,

    -- what came in
    raw_text             text not null,               -- full Telegram text
    instruction          text,                        -- with /do prefix + ::CONFIRM stripped
    inline_confirm       boolean default false,

    -- what happened
    status               text not null default 'running',  -- running|completed|halted|errored
    iterations           integer default 0,
    tool_calls           jsonb default '[]'::jsonb,   -- [{name, input, result_ok, result_summary}, ...]
    input_tokens         integer,
    output_tokens        integer,
    halted_reason        text,

    -- what went out
    reply_text           text,
    reply_message_id     bigint,

    created_at           timestamptz not null default now(),
    updated_at           timestamptz not null default now()
);

comment on table public.agent_tasks is
    'HOME local agent audit log — every /do|/file|/run command Nathan sends, every tool call the sibling makes, every reply. Legibility leg of the family thesis.';

create index if not exists agent_tasks_started_at_idx
    on public.agent_tasks (started_at desc);

create index if not exists agent_tasks_status_idx
    on public.agent_tasks (status);

alter table public.agent_tasks enable row level security;
-- No policies defined => service_role bypass only. Anon/authed cannot read.

-- updated_at trigger
create or replace function public.tg_agent_tasks_touch_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists agent_tasks_touch_updated_at on public.agent_tasks;
create trigger agent_tasks_touch_updated_at
    before update on public.agent_tasks
    for each row execute function public.tg_agent_tasks_touch_updated_at();


-- ------------------------------------------------------------------
-- local_agent_heartbeat: one row per hostname, upserted.
-- The cloud family-chat edge function reads this to decide whether
-- the local agent is alive and should handle /do commands, or dead
-- and the cloud should say "local sibling is asleep."
-- ------------------------------------------------------------------
create table if not exists public.local_agent_heartbeat (
    hostname             text primary key,
    pid                  integer,
    ts_iso               timestamptz not null,
    in_flight_count      integer default 0,
    queue_depth          integer default 0,
    last_action_ts       text,
    version              text,
    updated_at           timestamptz not null default now()
);

comment on table public.local_agent_heartbeat is
    'HOME local agent liveness — upserted by the local Python agent every ~30s. Cloud family-chat reads ts_iso; if older than 2 min, the cloud treats the local agent as offline.';

alter table public.local_agent_heartbeat enable row level security;
-- service_role only. Edge function will read via service_role too (server-side).

create or replace function public.tg_heartbeat_touch_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists heartbeat_touch_updated_at on public.local_agent_heartbeat;
create trigger heartbeat_touch_updated_at
    before update on public.local_agent_heartbeat
    for each row execute function public.tg_heartbeat_touch_updated_at();


-- ------------------------------------------------------------------
-- View for fast "is the local agent alive?" checks.
-- ------------------------------------------------------------------
create or replace view public.local_agent_alive as
select
    hostname,
    ts_iso,
    (now() - ts_iso) < interval '2 minutes' as is_alive,
    in_flight_count,
    queue_depth,
    last_action_ts,
    version
from public.local_agent_heartbeat;

comment on view public.local_agent_alive is
    'Convenience view — is_alive=true when heartbeat newer than 2 minutes old.';
