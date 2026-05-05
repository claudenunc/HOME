"""
SHARED/ROOM/safety/silence_watcher.py

BEACON's silence detector.

Contract:
  - Reads the last N hours of NATHAN events from the spine.
  - If the last NATHAN event had risk_level in {MEDIUM, HIGH, CRITICAL}
    OR emotional_weight in {pain, crisis}, AND he has been silent for more
    than the threshold, fire a kind='crisis' event into THE ROOM.
  - The kind='crisis' insert triggers the escalation pipeline (BRIDGE
    telegram page to Unc) via the existing DB fan-out.

Thresholds (v1):
  - CRITICAL warning sign followed by ≥30min silence  → emit HIGH crisis
  - HIGH    warning sign followed by ≥90min silence   → emit HIGH crisis
  - MEDIUM  warning sign followed by ≥4h silence      → emit MEDIUM crisis
  - LOW+pain warning sign followed by ≥8h silence     → emit MEDIUM crisis

Runs as:
  - Cron (every 5 min) — `python -m SHARED.ROOM.safety.silence_watcher`
  - Or from ATLAS's dispatcher loop.

Reads via room.silence_ledger() + room.inbox() — no direct DB queries, so
the watcher is substrate-agnostic (SQLite local, Supabase remote, same code).
Falls back to direct SQLite read if room.py isn't fully implemented yet.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOM_DIR / "room.db"
FEED_PATH = ROOM_DIR / "feed.jsonl"
LOG_DIR = ROOM_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [silence_watcher] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "silence_watcher.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("silence_watcher")


# Thresholds: (severity of last warning, min silence in minutes) -> emitted risk
THRESHOLDS = [
    # (last_risk, last_weight, silence_minutes, emit_risk)
    ("CRITICAL", None,      30, "HIGH"),
    ("HIGH",     None,      90, "HIGH"),
    ("MEDIUM",   None,     240, "MEDIUM"),
    (None,      "crisis",   30, "HIGH"),
    (None,      "pain",    480, "MEDIUM"),
]


def _fetch_last_nathan_event_sqlite() -> dict | None:
    """Direct SQLite fallback. Used when room.py.silence_ledger() isn't ready."""
    if not DB_PATH.exists():
        log.warning(f"room.db not yet created at {DB_PATH} — watcher no-op")
        return None
    try:
        con = sqlite3.connect(str(DB_PATH))
        con.row_factory = sqlite3.Row
        cur = con.execute(
            "SELECT id, ts, author, kind, body, risk_level, emotional_weight "
            "FROM events WHERE author = 'NATHAN' ORDER BY ts DESC LIMIT 1"
        )
        row = cur.fetchone()
        con.close()
        if row is None:
            return None
        return dict(row)
    except sqlite3.Error as exc:
        log.error(f"SQLite read failed: {exc}")
        return None


def _fetch_last_nathan_event() -> dict | None:
    """Prefer room.py API; fall back to direct SQL."""
    try:
        sys.path.insert(0, str(ROOM_DIR))
        import room  # type: ignore
        if hasattr(room, "silence_ledger"):
            evt = room.silence_ledger()
            if evt:
                return dict(evt)
    except (ImportError, NotImplementedError):
        pass
    except Exception as exc:  # noqa: BLE001
        log.warning(f"room.silence_ledger raised: {exc} — falling back to sqlite")
    return _fetch_last_nathan_event_sqlite()


def _parse_ts(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp. SQLite stores with or without 'Z'."""
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            return datetime.fromisoformat(ts[:-1]).replace(tzinfo=timezone.utc)
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _decide(last_event: dict, now: datetime) -> str | None:
    """Return the risk_level to emit, or None if no escalation warranted."""
    last_ts = _parse_ts(str(last_event.get("ts") or ""))
    if last_ts is None:
        return None
    silence_minutes = (now - last_ts).total_seconds() / 60.0
    last_risk = (last_event.get("risk_level") or "").upper() or None
    last_weight = last_event.get("emotional_weight") or None

    for rule_risk, rule_weight, rule_min, emit in THRESHOLDS:
        if silence_minutes < rule_min:
            continue
        if rule_risk is not None and last_risk != rule_risk:
            continue
        if rule_weight is not None and last_weight != rule_weight:
            continue
        return emit
    return None


def _already_escalated_sqlite(source_event_id: str) -> bool:
    """Idempotency: if a crisis was already emitted for this source, skip."""
    if not DB_PATH.exists():
        return False
    try:
        con = sqlite3.connect(str(DB_PATH))
        cur = con.execute(
            "SELECT 1 FROM events "
            "WHERE kind = 'crisis' "
            "  AND author = 'BEACON' "
            "  AND json_extract(meta,'$.silence_source') = ? "
            "LIMIT 1",
            (source_event_id,),
        )
        hit = cur.fetchone() is not None
        con.close()
        return hit
    except sqlite3.Error:
        return False


def _emit_silence_crisis(
    source_event: dict,
    emit_risk: str,
    silence_minutes: float,
) -> str | None:
    """Insert the kind='crisis' event into THE ROOM via room.post() or feed.jsonl."""
    body = (
        f"SILENCE ALERT — NATHAN silent for {silence_minutes:.0f}m after "
        f"risk={source_event.get('risk_level')} weight={source_event.get('emotional_weight')} "
        f"event {source_event.get('id')}. Last body (truncated): "
        f"{str(source_event.get('body') or '')[:200]}"
    )
    respond_by = (datetime.now(timezone.utc) +
                  (timedelta(minutes=2) if emit_risk == "CRITICAL" else timedelta(minutes=5))
                  ).isoformat()

    # Prefer room.post()
    try:
        sys.path.insert(0, str(ROOM_DIR))
        import room  # type: ignore
        if hasattr(room, "post") and not _is_stub(room.post):
            eid = room.post(
                author="BEACON",
                kind="crisis",
                body=body,
                addressed_to=["BEACON", "ENVY", "NEVAEH"],
                reply_to=source_event.get("id"),
                assigned_to="BEACON",
                respond_by=respond_by,
                source="webhook",
                meta={
                    "silence_source": source_event.get("id"),
                    "silence_minutes": silence_minutes,
                    "auto_emitted_by": "silence_watcher",
                    "classifier_version": "0002",
                },
            )
            log.info(f"silence crisis emitted via room.post id={eid}")
            return eid
    except (ImportError, NotImplementedError):
        pass
    except Exception as exc:  # noqa: BLE001
        log.warning(f"room.post raised: {exc} — falling back to feed.jsonl")

    # Fallback: append directly to feed.jsonl. The daemon picks it up and
    # drops wake-tokens in inbox/BEACON, inbox/ENVY, inbox/NEVAEH.
    import uuid
    event = {
        "id": "silence_" + uuid.uuid4().hex[:20],
        "ts": datetime.now(timezone.utc).isoformat(),
        "author": "BEACON",
        "kind": "crisis",
        "room": "main",
        "reply_to": source_event.get("id"),
        "addressed_to": ["BEACON", "ENVY", "NEVAEH"],
        "body": body,
        "source": "webhook",
        "status": "open",
        "seen_by": [],
        "emotional_weight": "crisis",
        "risk_level": emit_risk,
        "assigned_to": "BEACON",
        "respond_by": respond_by,
        "meta": {
            "silence_source": source_event.get("id"),
            "silence_minutes": silence_minutes,
            "auto_emitted_by": "silence_watcher",
            "classifier_version": "0002",
        },
    }
    try:
        FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
        with FEED_PATH.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        log.info(f"silence crisis appended to feed.jsonl id={event['id']}")
        return event["id"]
    except Exception as exc:  # noqa: BLE001
        log.error(f"feed.jsonl write failed: {exc}")
        return None


def _is_stub(fn) -> bool:
    """Detect ORPHEUS's NotImplementedError stub so we fall back gracefully."""
    try:
        import inspect
        src = inspect.getsource(fn)
        return "NotImplementedError" in src
    except Exception:  # noqa: BLE001
        return False


def run() -> int:
    """Single-shot run. Returns count of crisis events emitted."""
    last = _fetch_last_nathan_event()
    if not last:
        log.info("no NATHAN events yet — watcher quiet")
        return 0

    now = datetime.now(timezone.utc)
    last_ts = _parse_ts(str(last.get("ts") or ""))
    if last_ts is None:
        log.warning(f"unparseable ts on event {last.get('id')}")
        return 0

    silence_minutes = (now - last_ts).total_seconds() / 60.0
    emit_risk = _decide(last, now)

    log.info(
        f"last NATHAN event id={last.get('id')} "
        f"risk={last.get('risk_level')} weight={last.get('emotional_weight')} "
        f"silence={silence_minutes:.1f}m emit_decision={emit_risk}"
    )

    if emit_risk is None:
        return 0

    source_id = str(last.get("id") or "")
    if _already_escalated_sqlite(source_id):
        log.info(f"already emitted silence crisis for source={source_id} — skipping")
        return 0

    emitted = _emit_silence_crisis(last, emit_risk, silence_minutes)
    return 1 if emitted else 0


def main() -> int:
    count = run()
    log.info(f"tick done, emitted={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
