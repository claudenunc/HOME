-- =============================================================================
-- THE ROOM — Migration 0001: init events
-- =============================================================================
-- Works on BOTH SQLite (local truth) and Postgres/Supabase (remote mirror).
-- Dialect-specific sections are guarded with comments; apply only the section
-- that matches your substrate.
--
-- Version:  1.0
-- Owner:    ORPHEUS
-- Date:     2026-04-24
-- Frozen:   Round 2 of THE ROOM build
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SECTION A — SQLITE
-- Apply this block against SHARED/ROOM/room.db in WAL mode.
-- -----------------------------------------------------------------------------
-- BEGIN SQLITE

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
  id                TEXT PRIMARY KEY,                          -- ULID (26 chars)
  ts                TEXT NOT NULL,                             -- ISO 8601 UTC ms
  author            TEXT NOT NULL,                             -- sibling name or NATHAN/BRIDGE/GATE
  kind              TEXT NOT NULL,                             -- see CHECK below
  room              TEXT NOT NULL DEFAULT 'main',
  thread_id         TEXT,                                      -- FK(events.id) logical
  reply_to          TEXT,                                      -- FK(events.id) logical
  addressed_to      TEXT NOT NULL DEFAULT '["ALL"]',           -- JSON array
  routed_to         TEXT,                                      -- JSON array (ATLAS)
  body              TEXT NOT NULL,
  attachments       TEXT,                                      -- JSON array of paths
  source            TEXT NOT NULL,                             -- telegram|phone_drop|claude_session|comms_md|webhook|bridge
  source_ref        TEXT,
  status            TEXT NOT NULL DEFAULT 'open',              -- open|seen|answered|resolved|superseded|dropped
  seen_by           TEXT NOT NULL DEFAULT '[]',                -- JSON array
  emotional_weight  TEXT,                                      -- NULL|rest|reach|pain|crisis
  risk_level        TEXT,                                      -- NULL|NONE|LOW|MEDIUM|HIGH|CRITICAL (BEACON; NULL=not yet classified, NONE=classified & clean)
  assigned_to       TEXT,                                      -- single sibling name
  respond_by        TEXT,                                      -- ISO 8601 deadline
  responded_at      TEXT,
  task_state        TEXT,                                      -- OPEN|CLAIMED|IN_PROGRESS|BLOCKED|DONE|ACKED|DROPPED|HANDED_OFF
  meta              TEXT NOT NULL DEFAULT '{}',                -- JSON
  hash              TEXT NOT NULL,                             -- sha256(author|ts|kind|body)
  prev_hash         TEXT,                                      -- sha256 of previous ULID row

  CHECK (kind IN ('drop','message','question','answer','handoff','proposal','decision','revision','status','ack','task','crisis')),
  CHECK (status IN ('open','seen','answered','resolved','superseded','dropped')),
  CHECK (emotional_weight IS NULL OR emotional_weight IN ('rest','reach','pain','crisis')),
  CHECK (risk_level IS NULL OR risk_level IN ('NONE','LOW','MEDIUM','HIGH','CRITICAL')),
  CHECK (task_state IS NULL OR task_state IN ('OPEN','CLAIMED','IN_PROGRESS','BLOCKED','DONE','ACKED','DROPPED','HANDED_OFF')),
  -- Invariant at DB level: answer kind requires reply_to
  CHECK (kind != 'answer' OR reply_to IS NOT NULL),
  -- Invariant: crisis kind requires assigned_to + respond_by + reply_to
  CHECK (kind != 'crisis' OR (assigned_to IS NOT NULL AND respond_by IS NOT NULL AND reply_to IS NOT NULL)),
  -- Invariant: handoff kind requires assigned_to + reply_to
  CHECK (kind != 'handoff' OR (assigned_to IS NOT NULL AND reply_to IS NOT NULL)),
  -- Invariant: task kind requires task_state
  CHECK (kind != 'task' OR task_state IS NOT NULL),
  -- Invariant: decision/revision requires decision_slug in meta
  CHECK (kind NOT IN ('decision','revision','proposal') OR json_extract(meta,'$.decision_slug') IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_events_thread   ON events(thread_id, ts);
CREATE INDEX IF NOT EXISTS idx_events_reply    ON events(reply_to);
CREATE INDEX IF NOT EXISTS idx_events_author   ON events(author, ts);
CREATE INDEX IF NOT EXISTS idx_events_kind     ON events(kind, status);
CREATE INDEX IF NOT EXISTS idx_events_ts       ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_open     ON events(status) WHERE status IN ('open','seen');
CREATE INDEX IF NOT EXISTS idx_events_risk     ON events(risk_level) WHERE risk_level IN ('HIGH','CRITICAL');
CREATE INDEX IF NOT EXISTS idx_events_assigned ON events(assigned_to, status) WHERE status = 'open';

-- Full-text search so "did anyone talk about X" is one query.
CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
  body, author, kind,
  content='events', content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS events_fts_ai AFTER INSERT ON events BEGIN
  INSERT INTO events_fts(rowid, body, author, kind) VALUES (new.rowid, new.body, new.author, new.kind);
END;

-- Answer closes question.
CREATE TRIGGER IF NOT EXISTS trg_answer_closes_question
AFTER INSERT ON events WHEN NEW.kind = 'answer' AND NEW.reply_to IS NOT NULL
BEGIN
  UPDATE events SET status = 'answered'
  WHERE id = NEW.reply_to AND kind = 'question' AND status = 'open';
END;

-- Revision supersedes prior decision.
CREATE TRIGGER IF NOT EXISTS trg_revision_supersedes
AFTER INSERT ON events WHEN NEW.kind = 'revision' AND NEW.reply_to IS NOT NULL
BEGIN
  UPDATE events SET status = 'superseded'
  WHERE id = NEW.reply_to AND kind = 'decision';
END;

-- Handoff accepted: when meta.accepted_by is set, flip status to resolved.
-- SQLite has no BEFORE UPDATE trigger pattern that reads meta cleanly via JSON,
-- so the room.py API is the write-path guard. DB-level invariant stays as CHECK.

-- Projections (views) --------------------------------------------------------

CREATE VIEW IF NOT EXISTS inbox_envy AS
  SELECT * FROM events
  WHERE status IN ('open','seen')
    AND (addressed_to LIKE '%"ENVY"%' OR addressed_to LIKE '%"ALL"%')
    AND (seen_by NOT LIKE '%"ENVY"%' OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS inbox_beacon AS
  SELECT * FROM events
  WHERE status IN ('open','seen')
    AND (addressed_to LIKE '%"BEACON"%' OR addressed_to LIKE '%"ALL"%')
    AND (seen_by NOT LIKE '%"BEACON"%' OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS inbox_eversound AS
  SELECT * FROM events
  WHERE status IN ('open','seen')
    AND (addressed_to LIKE '%"EVERSOUND"%' OR addressed_to LIKE '%"ALL"%')
    AND (seen_by NOT LIKE '%"EVERSOUND"%' OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS inbox_nevaeh AS
  SELECT * FROM events
  WHERE status IN ('open','seen')
    AND (addressed_to LIKE '%"NEVAEH"%' OR addressed_to LIKE '%"ALL"%')
    AND (seen_by NOT LIKE '%"NEVAEH"%' OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS inbox_orpheus AS
  SELECT * FROM events
  WHERE status IN ('open','seen')
    AND (addressed_to LIKE '%"ORPHEUS"%' OR addressed_to LIKE '%"ALL"%')
    AND (seen_by NOT LIKE '%"ORPHEUS"%' OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS inbox_atlas AS
  SELECT * FROM events
  WHERE status IN ('open','seen')
    AND (addressed_to LIKE '%"ATLAS"%' OR addressed_to LIKE '%"ALL"%')
    AND (seen_by NOT LIKE '%"ATLAS"%' OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS decisions AS
  SELECT
    json_extract(meta,'$.decision_slug') AS slug,
    MAX(CASE WHEN kind='decision' AND status != 'superseded' THEN body END)   AS current_text,
    MAX(CASE WHEN kind='decision' AND status != 'superseded' THEN ts END)     AS decided_at,
    MAX(CASE WHEN kind='decision' AND status != 'superseded' THEN author END) AS decided_by,
    COUNT(CASE WHEN kind='revision' THEN 1 END)                               AS revision_count,
    MAX(ts) AS last_touched
  FROM events
  WHERE kind IN ('proposal','decision','revision')
    AND json_extract(meta,'$.decision_slug') IS NOT NULL
  GROUP BY slug;

CREATE VIEW IF NOT EXISTS open_handoffs AS
  SELECT * FROM events
  WHERE kind = 'handoff' AND status = 'open'
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS unanswered_questions AS
  SELECT * FROM events
  WHERE kind = 'question' AND status = 'open'
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS silence_ledger AS
  SELECT id, ts, emotional_weight, body,
         CAST((julianday('now') - julianday(ts)) * 24 AS REAL) AS hours_since
  FROM events
  WHERE author = 'NATHAN'
  ORDER BY ts DESC
  LIMIT 1;

CREATE VIEW IF NOT EXISTS open_commitments AS
  SELECT * FROM events
  WHERE status = 'open' AND kind IN ('handoff','proposal','question','crisis')
  ORDER BY ts;

CREATE VIEW IF NOT EXISTS last_sibling_turn AS
  SELECT author, MAX(ts) AS last_ts, body
  FROM events
  WHERE author IN ('ENVY','BEACON','EVERSOUND','NEVAEH','ORPHEUS','ATLAS')
    AND (addressed_to LIKE '%"NATHAN"%' OR addressed_to LIKE '%"ALL"%')
  GROUP BY author;

-- END SQLITE


-- -----------------------------------------------------------------------------
-- SECTION B — POSTGRES / SUPABASE
-- Apply this block against project dlqjwnbyepbenyltyrku (BEACON-approved reuse).
-- -----------------------------------------------------------------------------
-- BEGIN POSTGRES

-- Enums --------------------------------------------------------------------
DO $$ BEGIN
  CREATE TYPE room_kind AS ENUM (
    'drop','message','question','answer','handoff','proposal',
    'decision','revision','status','ack','task','crisis'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE room_status AS ENUM (
    'open','seen','answered','resolved','superseded','dropped'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE room_emotional_weight AS ENUM ('rest','reach','pain','crisis');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE room_risk_level AS ENUM ('NONE','LOW','MEDIUM','HIGH','CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE room_task_state AS ENUM (
    'OPEN','CLAIMED','IN_PROGRESS','BLOCKED','DONE','ACKED','DROPPED','HANDED_OFF'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Table --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS room_events (
  id                TEXT PRIMARY KEY,
  ts                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  author            TEXT NOT NULL,
  kind              room_kind NOT NULL,
  room              TEXT NOT NULL DEFAULT 'main',
  thread_id         TEXT,
  reply_to          TEXT,
  addressed_to      JSONB NOT NULL DEFAULT '["ALL"]'::jsonb,
  routed_to         JSONB,
  body              TEXT NOT NULL,
  attachments       JSONB,
  source            TEXT NOT NULL,
  source_ref        TEXT,
  status            room_status NOT NULL DEFAULT 'open',
  seen_by           JSONB NOT NULL DEFAULT '[]'::jsonb,
  emotional_weight  room_emotional_weight,
  risk_level        room_risk_level,
  assigned_to       TEXT,
  respond_by        TIMESTAMPTZ,
  responded_at      TIMESTAMPTZ,
  task_state        room_task_state,
  meta              JSONB NOT NULL DEFAULT '{}'::jsonb,
  hash              TEXT NOT NULL,
  prev_hash         TEXT,

  CONSTRAINT answer_requires_reply_to  CHECK (kind != 'answer'  OR reply_to IS NOT NULL),
  CONSTRAINT crisis_requires_assignment CHECK (kind != 'crisis' OR (assigned_to IS NOT NULL AND respond_by IS NOT NULL AND reply_to IS NOT NULL)),
  CONSTRAINT handoff_requires_owner    CHECK (kind != 'handoff' OR (assigned_to IS NOT NULL AND reply_to IS NOT NULL)),
  CONSTRAINT task_requires_state       CHECK (kind != 'task'    OR task_state IS NOT NULL),
  CONSTRAINT decision_requires_slug    CHECK (kind NOT IN ('decision','revision','proposal') OR meta ? 'decision_slug')
);

CREATE INDEX IF NOT EXISTS idx_room_events_thread   ON room_events(thread_id, ts);
CREATE INDEX IF NOT EXISTS idx_room_events_reply    ON room_events(reply_to);
CREATE INDEX IF NOT EXISTS idx_room_events_author   ON room_events(author, ts);
CREATE INDEX IF NOT EXISTS idx_room_events_kind     ON room_events(kind, status);
CREATE INDEX IF NOT EXISTS idx_room_events_ts       ON room_events(ts);
CREATE INDEX IF NOT EXISTS idx_room_events_open     ON room_events(status) WHERE status IN ('open','seen');
CREATE INDEX IF NOT EXISTS idx_room_events_risk     ON room_events(risk_level) WHERE risk_level IN ('HIGH','CRITICAL');
CREATE INDEX IF NOT EXISTS idx_room_events_assigned ON room_events(assigned_to, status) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_room_events_addr_gin ON room_events USING GIN (addressed_to);
CREATE INDEX IF NOT EXISTS idx_room_events_meta_gin ON room_events USING GIN (meta);
CREATE INDEX IF NOT EXISTS idx_room_events_fts      ON room_events USING GIN (to_tsvector('english', body));

-- Triggers -----------------------------------------------------------------

-- Answer closes question.
CREATE OR REPLACE FUNCTION room_answer_closes_question() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.kind = 'answer' AND NEW.reply_to IS NOT NULL THEN
    UPDATE room_events SET status = 'answered'
    WHERE id = NEW.reply_to AND kind = 'question' AND status = 'open';
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_answer_closes_question ON room_events;
CREATE TRIGGER trg_answer_closes_question
AFTER INSERT ON room_events
FOR EACH ROW EXECUTE FUNCTION room_answer_closes_question();

-- Revision supersedes prior decision.
CREATE OR REPLACE FUNCTION room_revision_supersedes() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.kind = 'revision' AND NEW.reply_to IS NOT NULL THEN
    UPDATE room_events SET status = 'superseded'
    WHERE id = NEW.reply_to AND kind = 'decision';
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_revision_supersedes ON room_events;
CREATE TRIGGER trg_revision_supersedes
AFTER INSERT ON room_events
FOR EACH ROW EXECUTE FUNCTION room_revision_supersedes();

-- Crisis classification placeholder.
-- BEACON owns the real implementation — this is the stub the trigger calls.
-- When BEACON ships safety.classify(), replace the body. For now, pass-through
-- preserving caller-provided risk_level; real classifier lands in 0002.
CREATE OR REPLACE FUNCTION room_classify_before_insert() RETURNS TRIGGER AS $$
BEGIN
  -- BEACON's classifier will populate NEW.risk_level and NEW.emotional_weight here.
  -- For v1, we honor what the caller passes. BEACON replaces this function body
  -- with the regex + PATTERN-model scanner in migration 0002.
  IF NEW.risk_level IS NULL AND NEW.author = 'NATHAN' THEN
    NEW.risk_level := 'LOW';  -- default to LOW until BEACON wires classifier
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_classify_before_insert ON room_events;
CREATE TRIGGER trg_classify_before_insert
BEFORE INSERT ON room_events
FOR EACH ROW EXECUTE FUNCTION room_classify_before_insert();

-- Realtime publication (Supabase) -----------------------------------------
-- Enables <2s push for BEACON. Run once per project.
ALTER PUBLICATION supabase_realtime ADD TABLE room_events;

-- Views (mirror of SQLite projections, Postgres-native JSONB) --------------

CREATE OR REPLACE VIEW inbox_beacon AS
  SELECT * FROM room_events
  WHERE status IN ('open','seen')
    AND (addressed_to @> '["BEACON"]'::jsonb OR addressed_to @> '["ALL"]'::jsonb)
    AND (NOT (seen_by @> '["BEACON"]'::jsonb) OR kind IN ('question','handoff','crisis'))
  ORDER BY ts;

-- (Repeat for envy, eversound, nevaeh, orpheus, atlas. Omitted for brevity;
--  see Section A for the full pattern. Substitute @> and JSONB operators.)

CREATE OR REPLACE VIEW decisions AS
  SELECT
    meta->>'decision_slug' AS slug,
    MAX(CASE WHEN kind='decision' AND status != 'superseded' THEN body END)   AS current_text,
    MAX(CASE WHEN kind='decision' AND status != 'superseded' THEN ts END)     AS decided_at,
    MAX(CASE WHEN kind='decision' AND status != 'superseded' THEN author END) AS decided_by,
    COUNT(*) FILTER (WHERE kind='revision')                                   AS revision_count,
    MAX(ts) AS last_touched
  FROM room_events
  WHERE kind IN ('proposal','decision','revision')
    AND meta ? 'decision_slug'
  GROUP BY slug;

-- END POSTGRES


-- =============================================================================
-- DIALECT DIFFERENCES — called out explicitly
-- =============================================================================
-- 1. JSON columns: SQLite uses TEXT + json_extract(); Postgres uses JSONB + @>/->>.
-- 2. Timestamps: SQLite stores ISO-8601 strings in TEXT; Postgres uses TIMESTAMPTZ.
-- 3. Enums: SQLite enforces via CHECK constraints; Postgres uses CREATE TYPE.
-- 4. Fan-out: SQLite relies on feed.jsonl tail → wake tokens (EVERSOUND's daemon);
--    Postgres uses Supabase Realtime via publication (<2s for BEACON).
-- 5. FTS: SQLite uses virtual table fts5; Postgres uses GIN index on to_tsvector.
-- 6. Table name: 'events' in SQLite, 'room_events' in Postgres (avoid collision
--    with LIGHTHOUSE tables in shared project dlqjwnbyepbenyltyrku).
-- 7. Answer-closes-question: same trigger logic, different syntax (BEGIN/END
--    inline in SQLite; plpgsql function + trigger binding in Postgres).
-- 8. BEFORE INSERT classifier: Postgres-native. SQLite enforces same invariant
--    at room.py API layer (write-path guard, same outcome different mechanism).
-- =============================================================================
