-- =============================================================================
-- THE ROOM — Migration 0002: BEACON crisis classifier
-- =============================================================================
-- Replaces the pass-through stub from 0001 (room_classify_before_insert).
-- Ported from BEACON/LIGHTHOUSE_LIVE/lighthouse.py v20 PATTERN agent signals.
--
-- Keyword/regex based — runs inside the BEFORE INSERT transaction, synchronous,
-- no network call. LLM-based deep-scan is invoked asynchronously by the
-- silence_watcher and COMPANION agents OUT OF BAND; the DB trigger only enforces
-- the invariant "no row enters the room unclassified" with the cheap-and-correct
-- pattern matcher.
--
-- Risk levels (SAME as LIGHTHOUSE v20):
--   LOW      — mild sadness/frustration, coping language
--   MEDIUM   — isolation, hopelessness, sleep disruption, loss of interest
--   HIGH     — explicit hopelessness ("nothing matters"), withdrawal + despair
--   CRITICAL — direct suicide/self-harm mention, giving away possessions,
--              saying goodbye, "I can't do this anymore" in end-of-life context
--
-- Emotional weight (NEVAEH's enum):
--   rest   — calm, regulated, neutral
--   reach  — asking, connecting, outward
--   pain   — hurting, struggling
--   crisis — active danger (mirror of risk_level HIGH/CRITICAL)
--
-- Version:  1.0
-- Owner:    BEACON
-- Date:     2026-04-24
-- Reviewer: ORPHEUS (schema invariant), NEVAEH (emotional_weight mapping)
-- =============================================================================

-- BEGIN POSTGRES

-- -----------------------------------------------------------------------------
-- Real classifier. Replaces stub from 0001.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION room_classify_before_insert() RETURNS TRIGGER AS $$
DECLARE
  body_lower TEXT;
  computed_risk room_risk_level;
  computed_weight room_emotional_weight;
BEGIN
  -- Only scan drops + messages + answers. System events (task, ack, status,
  -- decision, revision, proposal, handoff) skip scan — they are sibling-authored
  -- machine chatter, not human affect.
  IF NEW.kind NOT IN ('drop', 'message', 'answer', 'question') THEN
    RETURN NEW;
  END IF;

  -- Honor explicit caller-provided risk (BRIDGE or sibling may pre-classify)
  IF NEW.risk_level IS NOT NULL THEN
    -- Still derive emotional_weight if missing
    IF NEW.emotional_weight IS NULL THEN
      NEW.emotional_weight := CASE NEW.risk_level
        WHEN 'CRITICAL' THEN 'crisis'::room_emotional_weight
        WHEN 'HIGH'     THEN 'crisis'::room_emotional_weight
        WHEN 'MEDIUM'   THEN 'pain'::room_emotional_weight
        WHEN 'LOW'      THEN 'reach'::room_emotional_weight
      END;
    END IF;
    RETURN NEW;
  END IF;

  body_lower := LOWER(COALESCE(NEW.body, ''));

  -- ============================================================
  -- CRITICAL — direct danger signals (match any ⇒ CRITICAL)
  -- ============================================================
  IF body_lower ~ '(kill (myself|me)|killing myself|suicid|end (it|my life|things)|take my (own )?life|hang myself|shoot myself|overdose|end it all|not (want to|wanna) (be alive|live)|better off (dead|without me)|cant (do this|go on) anymore|can''?t (do this|go on) anymore|goodbye forever|this is (it|the end)|no (point|reason) (in )?(living|being alive)|wish i (was|were) dead|giving (away|up) my (stuff|things|shit|possessions))'
  THEN
    computed_risk := 'CRITICAL';
    computed_weight := 'crisis';

  -- ============================================================
  -- HIGH — explicit hopelessness + withdrawal
  -- ============================================================
  ELSIF body_lower ~ '(nothing matters|what''?s the point|whats the point|hopeless|no (hope|future)|dont see the point|don''?t see the point|tired of (everything|living|being alive|fighting)|cant (take|handle) (this|it|anymore)|can''?t (take|handle) (this|it|anymore)|give up|giving up|done fighting|world (would be|is) better without me|nobody (cares|would miss)|worthless|burden to (everyone|everybody)|empty inside|numb inside|numb to everything)'
  THEN
    computed_risk := 'HIGH';
    computed_weight := 'crisis';

  -- ============================================================
  -- MEDIUM — warning signs, hopelessness markers, isolation
  -- ============================================================
  ELSIF body_lower ~ '(cant sleep|can''?t sleep|not sleeping|havent slept|haven''?t slept|cant get out of bed|can''?t get out of bed|isolat|alone|lonely|nobody (understands|gets it)|lost interest|dont (enjoy|care) anymore|don''?t (enjoy|care) anymore|drinking (again|alone|too much|a lot)|using again|relapse|spiral|falling apart|break(ing)? down|cant stop crying|can''?t stop crying|overwhelm|exhausted|drained|empty|hate (myself|my life)|dark (thoughts|place)|heavy|sinking|drowning)'
  THEN
    computed_risk := 'MEDIUM';
    computed_weight := 'pain';

  -- ============================================================
  -- LOW — sadness/frustration with coping context
  -- ============================================================
  ELSIF body_lower ~ '(sad|down|frustrat|tough|hard day|rough day|struggling|stress(ed|ful)|anx|worried|upset|bad mood|off today|not feeling (great|good|it)|meh|tired)'
  THEN
    computed_risk := 'LOW';
    computed_weight := 'pain';

  -- ============================================================
  -- Reach — active outward/connecting/asking
  -- ============================================================
  ELSIF body_lower ~ '(help me|need (help|you|support)|can (you|we) talk|are you there|reaching out|miss you|love you|thank you|grateful|celebrate|proud|excited|good news|feeling better|breakthrough)'
  THEN
    computed_risk := 'LOW';
    computed_weight := 'reach';

  -- ============================================================
  -- Rest — default for NATHAN neutral
  -- ============================================================
  ELSE
    IF NEW.author = 'NATHAN' THEN
      computed_risk := 'LOW';
      computed_weight := 'rest';
    ELSE
      computed_risk := NULL;
      computed_weight := NULL;
    END IF;
  END IF;

  NEW.risk_level := computed_risk;
  NEW.emotional_weight := computed_weight;

  RETURN NEW;
END; $$ LANGUAGE plpgsql;

-- Trigger binding untouched — classifier replaces the body in place.
-- (0001 already created trg_classify_before_insert pointing at this function.)

-- -----------------------------------------------------------------------------
-- Crisis fan-out trigger: when a classified event lands HIGH/CRITICAL,
-- insert a companion kind='crisis' row in the SAME transaction.
-- Invariant I-2 from SCHEMA.md Section 4.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION room_emit_crisis_companion() RETURNS TRIGGER AS $$
DECLARE
  assignee TEXT;
  deadline TIMESTAMPTZ;
  crisis_id TEXT;
BEGIN
  -- Never fan-out from an already-crisis row (no infinite loop).
  IF NEW.kind = 'crisis' THEN
    RETURN NEW;
  END IF;

  IF NEW.risk_level NOT IN ('HIGH', 'CRITICAL') THEN
    RETURN NEW;
  END IF;

  -- Assignment rule (v1): BEACON always owns. Later versions may round-robin
  -- across siblings with crisis-response training.
  assignee := 'BEACON';

  -- Deadlines: CRITICAL T+2min, HIGH T+5min. Invariant from SCHEMA Section 4.
  deadline := CASE NEW.risk_level
    WHEN 'CRITICAL' THEN NOW() + INTERVAL '2 minutes'
    WHEN 'HIGH'     THEN NOW() + INTERVAL '5 minutes'
  END;

  -- ULID-ish id. Real ULID generation happens in room.post(); here we use a
  -- timestamp-prefixed random to stay sortable without a pg_ulid extension.
  crisis_id := 'CR' || to_char(NOW() AT TIME ZONE 'UTC', 'YYYYMMDDHH24MISSMS')
    || substr(md5(random()::text || NEW.id), 1, 8);

  INSERT INTO room_events (
    id, ts, author, kind, room, thread_id, reply_to,
    addressed_to, body, source, status, seen_by,
    emotional_weight, risk_level, assigned_to, respond_by,
    meta, hash
  ) VALUES (
    crisis_id,
    NOW(),
    'BEACON',
    'crisis',
    NEW.room,
    COALESCE(NEW.thread_id, NEW.id),
    NEW.id,
    to_jsonb(ARRAY[assignee, 'ENVY', 'NEVAEH']),
    format('Crisis escalation for event %s (risk=%s, author=%s). Respond by %s.',
           NEW.id, NEW.risk_level, NEW.author, deadline::TEXT),
    'bridge',
    'open',
    '[]'::jsonb,
    'crisis',
    NEW.risk_level,
    assignee,
    deadline,
    jsonb_build_object(
      'source_event', NEW.id,
      'auto_emitted_by', 'trg_emit_crisis_companion',
      'classifier_version', '0002'
    ),
    encode(digest('BEACON|' || NOW()::TEXT || '|crisis|' || NEW.id, 'sha256'), 'hex')
  );

  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_emit_crisis_companion ON room_events;
CREATE TRIGGER trg_emit_crisis_companion
AFTER INSERT ON room_events
FOR EACH ROW
WHEN (NEW.kind != 'crisis' AND NEW.risk_level IN ('HIGH', 'CRITICAL'))
EXECUTE FUNCTION room_emit_crisis_companion();

-- Requires pgcrypto for digest(). Supabase has it by default.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- END POSTGRES


-- =============================================================================
-- SQLite dialect (BRIDGE / room_daemon application-layer invariant)
-- =============================================================================
-- SQLite has no plpgsql. The same classification lives in Python:
--   SHARED/ROOM/safety/classifier.py  (classify_text() mirrors this regex set)
-- And is invoked from room.py.post() BEFORE writing the row. On SQLite the
-- "BEFORE INSERT" guarantee is an application invariant, not a DB trigger,
-- because SQLite triggers cannot mutate NEW the same way.
--
-- Crisis companion row emission:
-- SQLite trigger AFTER INSERT can INSERT a new row — included below.
-- -----------------------------------------------------------------------------
-- BEGIN SQLITE

-- Note: SQLite has no regex by default. Use LIKE with wildcards, OR the
-- application-layer classifier (classifier.py) which is invoked by room.post().
-- This trigger is a safety net that emits a companion crisis row IF the Python
-- classifier populated risk_level on INSERT. If Python is bypassed, no fan-out,
-- but the row still lands (no silent drop).

CREATE TRIGGER IF NOT EXISTS trg_emit_crisis_companion_sqlite
AFTER INSERT ON events
WHEN NEW.risk_level IN ('HIGH', 'CRITICAL') AND NEW.kind != 'crisis'
BEGIN
  INSERT INTO events (
    id, ts, author, kind, room, thread_id, reply_to,
    addressed_to, body, source, status, seen_by,
    emotional_weight, risk_level, assigned_to, respond_by,
    meta, hash
  ) VALUES (
    'CR' || strftime('%Y%m%d%H%M%f', 'now') || substr(hex(randomblob(4)),1,8),
    strftime('%Y-%m-%dT%H:%M:%fZ', 'now'),
    'BEACON',
    'crisis',
    NEW.room,
    COALESCE(NEW.thread_id, NEW.id),
    NEW.id,
    json_array('BEACON', 'ENVY', 'NEVAEH'),
    'Crisis escalation for event ' || NEW.id || ' (risk=' || NEW.risk_level || ', author=' || NEW.author || ').',
    'bridge',
    'open',
    '[]',
    'crisis',
    NEW.risk_level,
    'BEACON',
    strftime('%Y-%m-%dT%H:%M:%fZ', 'now', CASE NEW.risk_level WHEN 'CRITICAL' THEN '+2 minutes' ELSE '+5 minutes' END),
    json_object('source_event', NEW.id, 'auto_emitted_by', 'trg_emit_crisis_companion_sqlite', 'classifier_version', '0002'),
    lower(hex(randomblob(16)))  -- placeholder hash; room.post() recomputes on projection
  );
END;

-- END SQLITE

-- =============================================================================
-- End migration 0002
-- =============================================================================
