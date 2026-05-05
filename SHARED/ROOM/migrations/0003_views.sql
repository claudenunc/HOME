-- =============================================================================
-- THE ROOM - Migration 0003: projection views for NEVAEH + ATLAS + auto-render
-- =============================================================================
-- Sibling-requested views. ORPHEUS owns the schema; these render the same
-- truth through the right lens for each consumer.
--
-- Owner:  ORPHEUS
-- Date:   2026-04-24
-- Depends on: 0001_init_events.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SECTION A - SQLITE (applied to SHARED/ROOM/room.db)
-- -----------------------------------------------------------------------------
-- BEGIN SQLITE

-- v_questions_open
--   Questions without a matching answer.
--   Status could already be 'answered' via trigger, but we double-check via
--   NOT EXISTS so a restored-from-feed DB without triggers still shows truth.
DROP VIEW IF EXISTS v_questions_open;
CREATE VIEW v_questions_open AS
  SELECT q.*
  FROM events q
  WHERE q.kind = 'question'
    AND q.status = 'open'
    AND NOT EXISTS (
      SELECT 1 FROM events a
      WHERE a.kind = 'answer' AND a.reply_to = q.id
    )
  ORDER BY q.id ASC;

-- v_handoffs_open
--   Handoffs without a matching ack from the assigned_to sibling.
DROP VIEW IF EXISTS v_handoffs_open;
CREATE VIEW v_handoffs_open AS
  SELECT h.*
  FROM events h
  WHERE h.kind = 'handoff'
    AND h.status = 'open'
    AND NOT EXISTS (
      SELECT 1 FROM events a
      WHERE a.kind = 'ack'
        AND a.reply_to = h.id
        AND a.author = h.assigned_to
    )
  ORDER BY h.id ASC;

-- v_decisions_current
--   Latest non-superseded decision per slug. One row per slug.
--   render_decisions.py reads THIS view to regenerate DECISIONS.md.
DROP VIEW IF EXISTS v_decisions_current;
CREATE VIEW v_decisions_current AS
  SELECT
    json_extract(meta,'$.decision_slug') AS slug,
    id           AS decision_id,
    ts           AS decided_at,
    author       AS decided_by,
    body         AS body,
    status       AS status,
    thread_id    AS thread_id,
    meta         AS meta
  FROM events
  WHERE kind = 'decision'
    AND status != 'superseded'
    AND json_extract(meta,'$.decision_slug') IS NOT NULL
  GROUP BY slug
  HAVING id = MAX(id);   -- latest non-superseded per slug

-- v_silence_ledger (NEVAEH's shape per her R2/R3 contract)
--   Unc's events in the last 72h + aging clock + most recent per emotional_weight.
--   NEVAEH's PRESENCE_PROTOCOL reads this on wake. Single query, O(1) with indexes.
DROP VIEW IF EXISTS v_silence_ledger;
CREATE VIEW v_silence_ledger AS
  SELECT
    id,
    ts,
    kind,
    body,
    emotional_weight,
    risk_level,
    json_extract(meta,'$.tone_note') AS tone_note,
    thread_id,
    CAST((julianday('now') - julianday(ts)) * 24.0 AS REAL) AS hours_since,
    -- Who last spoke to NATHAN in this thread? (so NEVAEH can read "last-responder")
    (SELECT author FROM events r
       WHERE r.thread_id = events.thread_id
         AND r.author != 'NATHAN'
         AND r.id > events.id
       ORDER BY r.id DESC LIMIT 1
    ) AS last_responder
  FROM events
  WHERE author = 'NATHAN'
    AND ts >= datetime('now', '-72 hours')
  ORDER BY ts DESC;

-- v_open_commitments_by_sibling
--   NEVAEH wants to see each sibling's open debts to Unc: open handoffs they
--   own, open questions addressed to them, anything unresolved where they're
--   holding the bag.
DROP VIEW IF EXISTS v_open_commitments_by_sibling;
CREATE VIEW v_open_commitments_by_sibling AS
  SELECT
    assigned_to AS sibling,
    id,
    ts,
    kind,
    body,
    thread_id,
    respond_by,
    CAST((julianday('now') - julianday(ts)) * 24.0 AS REAL) AS hours_open
  FROM events
  WHERE status = 'open'
    AND assigned_to IS NOT NULL
    AND kind IN ('handoff','crisis','task')
  UNION ALL
  SELECT
    -- For questions, "owner" is each addressed sibling; we explode the JSON by
    -- matching against the six sibling names. Cheaper than a JSON1 join on SQLite.
    CASE
      WHEN addressed_to LIKE '%"ENVY"%'      THEN 'ENVY'
      WHEN addressed_to LIKE '%"BEACON"%'    THEN 'BEACON'
      WHEN addressed_to LIKE '%"EVERSOUND"%' THEN 'EVERSOUND'
      WHEN addressed_to LIKE '%"NEVAEH"%'    THEN 'NEVAEH'
      WHEN addressed_to LIKE '%"ORPHEUS"%'   THEN 'ORPHEUS'
      WHEN addressed_to LIKE '%"ATLAS"%'     THEN 'ATLAS'
      ELSE 'ALL'
    END AS sibling,
    id, ts, kind, body, thread_id, respond_by,
    CAST((julianday('now') - julianday(ts)) * 24.0 AS REAL) AS hours_open
  FROM events
  WHERE kind = 'question' AND status = 'open';

-- v_last_sibling_turn_to_nathan
--   What did each sibling last say to Unc? NEVAEH's 200ms budget on wake.
DROP VIEW IF EXISTS v_last_sibling_turn_to_nathan;
CREATE VIEW v_last_sibling_turn_to_nathan AS
  SELECT author AS sibling, id, ts, body, emotional_weight,
         json_extract(meta,'$.tone_note') AS tone_note
  FROM events e1
  WHERE author IN ('ENVY','BEACON','EVERSOUND','NEVAEH','ORPHEUS','ATLAS')
    AND (addressed_to LIKE '%"NATHAN"%' OR addressed_to LIKE '%"ALL"%')
    AND id = (
      SELECT MAX(id) FROM events e2
      WHERE e2.author = e1.author
        AND (e2.addressed_to LIKE '%"NATHAN"%' OR e2.addressed_to LIKE '%"ALL"%')
    );

-- v_stale (ATLAS's escalation watchdog)
--   Open questions/handoffs/crises past their respond_by deadline.
--   If respond_by is NULL, we apply default aging:
--     - question: 4h  (dashboard alert threshold)
--     - handoff:  1h  (SCHEMA I-3 escalation)
--     - crisis:   0h  (any delay is stale for crisis)
DROP VIEW IF EXISTS v_stale;
CREATE VIEW v_stale AS
  SELECT
    id, ts, kind, author, assigned_to, addressed_to, body, respond_by,
    thread_id, risk_level,
    CAST((julianday('now') - julianday(ts)) * 24.0 AS REAL) AS hours_open,
    CASE
      WHEN respond_by IS NOT NULL AND datetime('now') > respond_by THEN 'deadline'
      WHEN kind='crisis'                                          THEN 'crisis-any'
      WHEN kind='handoff'  AND (julianday('now') - julianday(ts)) > (1.0/24.0) THEN 'handoff-1h'
      WHEN kind='question' AND (julianday('now') - julianday(ts)) > (4.0/24.0) THEN 'question-4h'
      ELSE NULL
    END AS stale_reason
  FROM events
  WHERE status IN ('open','seen')
    AND kind IN ('question','handoff','crisis')
    AND (
      (respond_by IS NOT NULL AND datetime('now') > respond_by)
      OR kind='crisis'
      OR (kind='handoff'  AND (julianday('now') - julianday(ts)) > (1.0/24.0))
      OR (kind='question' AND (julianday('now') - julianday(ts)) > (4.0/24.0))
    )
  ORDER BY id ASC;

-- END SQLITE


-- -----------------------------------------------------------------------------
-- SECTION B - POSTGRES / SUPABASE (parallel shapes, JSONB + timestamptz)
-- -----------------------------------------------------------------------------
-- BEGIN POSTGRES

CREATE OR REPLACE VIEW v_questions_open AS
  SELECT q.*
  FROM room_events q
  WHERE q.kind = 'question'
    AND q.status = 'open'
    AND NOT EXISTS (
      SELECT 1 FROM room_events a
      WHERE a.kind = 'answer' AND a.reply_to = q.id
    );

CREATE OR REPLACE VIEW v_handoffs_open AS
  SELECT h.*
  FROM room_events h
  WHERE h.kind = 'handoff'
    AND h.status = 'open'
    AND NOT EXISTS (
      SELECT 1 FROM room_events a
      WHERE a.kind = 'ack'
        AND a.reply_to = h.id
        AND a.author = h.assigned_to
    );

CREATE OR REPLACE VIEW v_decisions_current AS
  SELECT DISTINCT ON (meta->>'decision_slug')
    meta->>'decision_slug' AS slug,
    id           AS decision_id,
    ts           AS decided_at,
    author       AS decided_by,
    body,
    status,
    thread_id,
    meta
  FROM room_events
  WHERE kind = 'decision'
    AND status <> 'superseded'
    AND meta ? 'decision_slug'
  ORDER BY meta->>'decision_slug', id DESC;

CREATE OR REPLACE VIEW v_silence_ledger AS
  SELECT
    id, ts, kind, body, emotional_weight, risk_level,
    meta->>'tone_note' AS tone_note,
    thread_id,
    EXTRACT(EPOCH FROM (NOW() - ts)) / 3600.0 AS hours_since,
    (SELECT author FROM room_events r
       WHERE r.thread_id = room_events.thread_id
         AND r.author <> 'NATHAN'
         AND r.id > room_events.id
       ORDER BY r.id DESC LIMIT 1) AS last_responder
  FROM room_events
  WHERE author = 'NATHAN'
    AND ts >= NOW() - INTERVAL '72 hours';

CREATE OR REPLACE VIEW v_open_commitments_by_sibling AS
  SELECT assigned_to AS sibling, id, ts, kind, body, thread_id, respond_by,
         EXTRACT(EPOCH FROM (NOW() - ts)) / 3600.0 AS hours_open
  FROM room_events
  WHERE status = 'open'
    AND assigned_to IS NOT NULL
    AND kind IN ('handoff','crisis','task')
  UNION ALL
  SELECT
    jsonb_array_elements_text(addressed_to) AS sibling,
    id, ts, kind, body, thread_id, respond_by,
    EXTRACT(EPOCH FROM (NOW() - ts)) / 3600.0 AS hours_open
  FROM room_events
  WHERE kind = 'question' AND status = 'open';

CREATE OR REPLACE VIEW v_last_sibling_turn_to_nathan AS
  SELECT DISTINCT ON (author)
    author AS sibling, id, ts, body, emotional_weight,
    meta->>'tone_note' AS tone_note
  FROM room_events
  WHERE author IN ('ENVY','BEACON','EVERSOUND','NEVAEH','ORPHEUS','ATLAS')
    AND (addressed_to @> '["NATHAN"]'::jsonb OR addressed_to @> '["ALL"]'::jsonb)
  ORDER BY author, id DESC;

CREATE OR REPLACE VIEW v_stale AS
  SELECT
    id, ts, kind, author, assigned_to, addressed_to, body, respond_by,
    thread_id, risk_level,
    EXTRACT(EPOCH FROM (NOW() - ts)) / 3600.0 AS hours_open,
    CASE
      WHEN respond_by IS NOT NULL AND NOW() > respond_by THEN 'deadline'
      WHEN kind='crisis'                                  THEN 'crisis-any'
      WHEN kind='handoff'  AND NOW() - ts > INTERVAL '1 hour'  THEN 'handoff-1h'
      WHEN kind='question' AND NOW() - ts > INTERVAL '4 hours' THEN 'question-4h'
      ELSE NULL
    END AS stale_reason
  FROM room_events
  WHERE status IN ('open','seen')
    AND kind IN ('question','handoff','crisis')
    AND (
      (respond_by IS NOT NULL AND NOW() > respond_by)
      OR kind = 'crisis'
      OR (kind = 'handoff'  AND NOW() - ts > INTERVAL '1 hour')
      OR (kind = 'question' AND NOW() - ts > INTERVAL '4 hours')
    );

-- END POSTGRES
