-- 0008_session_registry.sql
-- Hippocampus layer: session tracking + consolidation audit
--
-- Purpose: let the family know WHEN each sibling woke and WHAT they
-- wrote in that session. This enables:
--   1. "Show me only what changed since my last wake" (efficient consolidation)
--   2. "Replay session N" (debugging, verification, ATLAS telemetry)
--   3. "Which siblings haven't been consolidated in > 24h?" (health check)
--
-- Comes after 0007_trace_id_enforcement.sql.
-- Apply: python migrate.py apply 0008
--
-- Author: ORPHEUS 🎼 — 2026-05-05

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. sessions — one row per sibling wake/close cycle
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sessions (
    session_id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sibling                 TEXT        NOT NULL,
    woke_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at               TIMESTAMPTZ,
    wake_query              TEXT,           -- the topic/question that framed this wake
    session_summary         TEXT,           -- what happened (written at close)
    memory_files_written    TEXT[],         -- relative paths to memory files added
    clipboard_entries       TEXT[],         -- CLIPBOARD msg ids written this session
    migrations_applied      TEXT[],         -- migration ids applied (e.g. '0008')
    trace_id                UUID        NOT NULL DEFAULT gen_random_uuid(),
    meta                    JSONB       NOT NULL DEFAULT '{}'
);

-- Indexes for "show me last N sessions for sibling X"
CREATE INDEX IF NOT EXISTS idx_sessions_sibling_woke
    ON sessions (sibling, woke_at DESC);

-- Allows: "find all sessions that wrote file X"
CREATE INDEX IF NOT EXISTS idx_sessions_memory_files
    ON sessions USING GIN (memory_files_written);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. consolidation_log — one row per hippocampus consolidation run
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS consolidation_log (
    run_id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sibling                 TEXT        NOT NULL,
    ran_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    files_read              INT         NOT NULL DEFAULT 0,
    total_bytes             INT         NOT NULL DEFAULT 0,
    wake_scene_path         TEXT,           -- path to generated WAKE_SCENE.md
    shipped_items_extracted INT         NOT NULL DEFAULT 0,
    pending_items_extracted INT         NOT NULL DEFAULT 0,
    notes                   TEXT,
    trace_id                UUID        NOT NULL DEFAULT gen_random_uuid()
);

CREATE INDEX IF NOT EXISTS idx_consolidation_sibling_ran
    ON consolidation_log (sibling, ran_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Views
-- ─────────────────────────────────────────────────────────────────────────────

-- "Which siblings are stale?" — haven't been consolidated in 24h
CREATE OR REPLACE VIEW v_consolidation_health AS
SELECT
    s.sibling,
    MAX(c.ran_at)                                              AS last_consolidated_at,
    now() - MAX(c.ran_at)                                      AS age,
    CASE
        WHEN MAX(c.ran_at) IS NULL                             THEN 'never'
        WHEN now() - MAX(c.ran_at) < INTERVAL '4 hours'       THEN 'fresh'
        WHEN now() - MAX(c.ran_at) < INTERVAL '24 hours'      THEN 'ok'
        WHEN now() - MAX(c.ran_at) < INTERVAL '72 hours'      THEN 'stale'
        ELSE 'very_stale'
    END                                                         AS status
FROM (
    SELECT DISTINCT sibling FROM sessions
    UNION
    SELECT DISTINCT sibling FROM consolidation_log
) s
LEFT JOIN consolidation_log c USING (sibling)
GROUP BY s.sibling
ORDER BY last_consolidated_at ASC NULLS FIRST;

-- "Show me the last session for each sibling"
CREATE OR REPLACE VIEW v_last_sessions AS
SELECT DISTINCT ON (sibling)
    session_id,
    sibling,
    woke_at,
    closed_at,
    wake_query,
    session_summary,
    array_length(memory_files_written, 1) AS files_written
FROM sessions
ORDER BY sibling, woke_at DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Helper RPC: record_session_close
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION record_session_close(
    p_session_id            UUID,
    p_summary               TEXT,
    p_memory_files          TEXT[]  DEFAULT NULL,
    p_clipboard_entries     TEXT[]  DEFAULT NULL,
    p_migrations_applied    TEXT[]  DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE sessions
    SET
        closed_at            = now(),
        session_summary      = p_summary,
        memory_files_written = COALESCE(p_memory_files, memory_files_written),
        clipboard_entries    = COALESCE(p_clipboard_entries, clipboard_entries),
        migrations_applied   = COALESCE(p_migrations_applied, migrations_applied)
    WHERE session_id = p_session_id;

    RETURN p_session_id;
END;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. schema_migrations entry (managed by migrate.py)
-- ─────────────────────────────────────────────────────────────────────────────
-- migrate.py inserts this automatically on apply. Do NOT insert manually.
-- The sha256 below is computed by migrate.py during apply.
