"""
SHARED/ROOM/safety_net/stale_watcher.py

THE ROOM — operational stale detector. ATLAS's watchdog.

Owner: ATLAS
Scope: operational silence only. NOT human-emotional silence.
       (BEACON's silence_watcher at SHARED/ROOM/safety/silence_watcher.py
        handles NATHAN / emotional_weight. We do not overlap.)

What counts as stale (operational):
  1. task_state IN ('CLAIMED','IN_PROGRESS') with no new event on the same
     thread_id for > heartbeat_deadline (default 2h).
  2. kind='question' AND status='open' older than respond_by (or 4h default).
  3. kind='handoff' AND status='open' older than 1h (schema invariant I-3).

When stale, surface a new kind='status' event with task_state='STALE',
addressed_to = [original assignee, ENVY], body = short context.
Let ENVY or the original assignee act. We don't escalate; we surface.

Substrate: reads via room.py queries OR directly from feed.jsonl when room.py
           queries aren't wired yet. Writes via room.post().

Cadence: every 5 minutes. Not crisis-critical; crisis path is BEACON's.
"""
from __future__ import annotations

import json
import os
import sys
import time
import signal
import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOM_DIR = Path(__file__).resolve().parent.parent  # SHARED/ROOM/
FEED_PATH = ROOM_DIR / "feed.jsonl"
DB_PATH = ROOM_DIR / "room.db"
LOG_DIR = ROOM_DIR / "logs"
HEARTBEAT = LOG_DIR / "stale_watcher.heartbeat"
STATE_FILE = LOG_DIR / "stale_watcher.state.json"  # which events we've already flagged

# Thresholds (tunable via env)
TASK_HEARTBEAT_HOURS = float(os.environ.get("STALE_TASK_HOURS", "2"))
QUESTION_HOURS = float(os.environ.get("STALE_QUESTION_HOURS", "4"))
HANDOFF_HOURS = float(os.environ.get("STALE_HANDOFF_HOURS", "1"))
SCAN_INTERVAL_SEC = int(os.environ.get("STALE_SCAN_SEC", "300"))  # 5 min

_stop = threading.Event()


# ------------------------------------------------------------------
# Heartbeat
# ------------------------------------------------------------------

def heartbeat_loop() -> None:
    while not _stop.is_set():
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            HEARTBEAT.write_text(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "pid": os.getpid(),
                "status": "alive",
                "process": "stale_watcher",
            }))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[stale] heartbeat failed: {exc}\n")
        _stop.wait(60)


# ------------------------------------------------------------------
# Flagged state (don't re-surface the same stale thing)
# ------------------------------------------------------------------

def load_flagged() -> dict[str, str]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_flagged(flagged: dict[str, str]) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(flagged, indent=2))
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[stale] state save failed: {exc}\n")


# ------------------------------------------------------------------
# Query path — prefer SQLite spine, fall back to feed.jsonl scan
# ------------------------------------------------------------------

def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        # ISO-8601 with or without 'Z'
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:  # noqa: BLE001
        return None


def find_stale_spine() -> list[dict]:
    """Query SQLite spine for stale rows. Returns [] if DB not ready."""
    if not DB_PATH.exists():
        return []
    stale: list[dict] = []
    now = datetime.now(timezone.utc)
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # 1. Open questions older than QUESTION_HOURS
        cutoff_q = (now - timedelta(hours=QUESTION_HOURS)).isoformat()
        for row in cur.execute(
            "SELECT * FROM events WHERE kind='question' AND status='open' AND ts < ?",
            (cutoff_q,),
        ):
            stale.append({**dict(row), "_stale_reason": "question-unanswered"})

        # 2. Open handoffs older than HANDOFF_HOURS
        cutoff_h = (now - timedelta(hours=HANDOFF_HOURS)).isoformat()
        for row in cur.execute(
            "SELECT * FROM events WHERE kind='handoff' AND status='open' AND ts < ?",
            (cutoff_h,),
        ):
            stale.append({**dict(row), "_stale_reason": "handoff-unaccepted"})

        # 3. Tasks claimed/in-progress with no thread activity past TASK_HEARTBEAT_HOURS
        cutoff_t = (now - timedelta(hours=TASK_HEARTBEAT_HOURS)).isoformat()
        for row in cur.execute(
            """
            SELECT * FROM events
            WHERE kind='task'
              AND task_state IN ('CLAIMED','IN_PROGRESS')
              AND id NOT IN (
                SELECT e2.thread_id FROM events e2
                WHERE e2.thread_id IS NOT NULL AND e2.ts > ?
              )
              AND ts < ?
            """,
            (cutoff_t, cutoff_t),
        ):
            stale.append({**dict(row), "_stale_reason": "task-no-heartbeat"})

        conn.close()
    except sqlite3.Error as exc:
        sys.stderr.write(f"[stale] sqlite query failed: {exc}\n")
    return stale


def find_stale_feed() -> list[dict]:
    """Fallback: scan feed.jsonl when SQLite spine isn't ready.

    Less efficient, but correct. Same three checks.
    """
    if not FEED_PATH.exists():
        return []
    now = datetime.now(timezone.utc)
    cutoff_q = now - timedelta(hours=QUESTION_HOURS)
    cutoff_h = now - timedelta(hours=HANDOFF_HOURS)
    cutoff_t = now - timedelta(hours=TASK_HEARTBEAT_HOURS)

    events: list[dict] = []
    try:
        with FEED_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[stale] feed read failed: {exc}\n")
        return []

    # Build status map by id (latest wins for state transitions)
    # Note: in spine model, status updates append new rows. For feed fallback
    # we approximate by tracking latest seen.
    stale: list[dict] = []
    latest_thread_activity: dict[str, datetime] = {}
    for ev in events:
        tid = ev.get("thread_id") or ev.get("id")
        ts = _parse_ts(str(ev.get("ts", "")))
        if tid and ts:
            prev = latest_thread_activity.get(tid)
            if prev is None or ts > prev:
                latest_thread_activity[tid] = ts

    for ev in events:
        kind = ev.get("kind")
        status = ev.get("status", "open")
        ts = _parse_ts(str(ev.get("ts", "")))
        if ts is None:
            continue
        if kind == "question" and status == "open" and ts < cutoff_q:
            stale.append({**ev, "_stale_reason": "question-unanswered"})
        elif kind == "handoff" and status == "open" and ts < cutoff_h:
            stale.append({**ev, "_stale_reason": "handoff-unaccepted"})
        elif (
            kind == "task"
            and str(ev.get("task_state", "")) in ("CLAIMED", "IN_PROGRESS")
        ):
            last = latest_thread_activity.get(ev.get("id", ""), ts)
            if last < cutoff_t:
                stale.append({**ev, "_stale_reason": "task-no-heartbeat"})
    return stale


# ------------------------------------------------------------------
# Surface stale event as kind='status' w/ task_state='STALE'
# ------------------------------------------------------------------

def surface_stale(stale_event: dict) -> bool:
    """Post a status event flagging the stale condition. Returns True if posted."""
    event_id = stale_event.get("id", "")
    reason = stale_event.get("_stale_reason", "unknown")
    assigned = stale_event.get("assigned_to")
    author = stale_event.get("author", "?")
    body_preview = str(stale_event.get("body", ""))[:140]
    addressed = ["ENVY"]
    if assigned:
        addressed.insert(0, assigned)

    body = (
        f"STALE [{reason}] — event {event_id} from {author} "
        f"has been open past its deadline.\n"
        f"> {body_preview}\n"
        f"Original kind: {stale_event.get('kind')}. "
        f"task_state was: {stale_event.get('task_state')}. "
        f"Surface only — not escalating. Original owner: act or hand off."
    )
    meta = {
        "stale_reason": reason,
        "original_event_id": event_id,
        "original_kind": stale_event.get("kind"),
        "flagged_by": "ATLAS.stale_watcher",
    }

    try:
        sys.path.insert(0, str(ROOM_DIR))
        import room  # type: ignore  # noqa: WPS433
        if hasattr(room, "post"):
            room.post(  # type: ignore[attr-defined]
                author="ATLAS",
                kind="status",
                body=body,
                addressed_to=addressed,
                reply_to=event_id or None,
                thread_id=stale_event.get("thread_id"),
                task_state="STALE" if stale_event.get("kind") == "task" else None,
                meta=meta,
            )
            return True
    except NotImplementedError:
        # room.py stub — write a fallback line into feed.jsonl directly
        # (EVERSOUND's daemon will pick it up).
        pass
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[stale] room.post failed: {exc}\n")

    # Fallback: append directly to feed.jsonl so nothing is lost
    try:
        import hashlib
        now_iso = datetime.now(timezone.utc).isoformat()
        fallback_id = f"stale-{int(time.time()*1000)}-{event_id[:8]}"
        fallback = {
            "id": fallback_id,
            "ts": now_iso,
            "author": "ATLAS",
            "kind": "status",
            "room": "main",
            "thread_id": stale_event.get("thread_id"),
            "reply_to": event_id or None,
            "addressed_to": addressed,
            "body": body,
            "source": "claude_session",
            "status": "open",
            "seen_by": [],
            "task_state": "STALE" if stale_event.get("kind") == "task" else None,
            "meta": meta,
            "hash": hashlib.sha256(
                f"ATLAS|{now_iso}|status|{body}".encode("utf-8")
            ).hexdigest(),
        }
        with FEED_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(fallback, ensure_ascii=False) + "\n")
        return True
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[stale] feed fallback failed: {exc}\n")
        return False


# ------------------------------------------------------------------
# Scan loop
# ------------------------------------------------------------------

def scan_once() -> int:
    flagged = load_flagged()
    # Prefer spine; fall back to feed scan
    stale_list = find_stale_spine()
    if not stale_list:
        stale_list = find_stale_feed()

    surfaced = 0
    for ev in stale_list:
        key = f"{ev.get('id')}::{ev.get('_stale_reason')}"
        if key in flagged:
            continue  # already flagged in a prior scan
        if surface_stale(ev):
            flagged[key] = datetime.now(timezone.utc).isoformat()
            surfaced += 1
    save_flagged(flagged)
    return surfaced


def scan_loop() -> None:
    while not _stop.is_set():
        try:
            count = scan_once()
            if count > 0:
                sys.stderr.write(f"[stale] surfaced {count} stale event(s)\n")
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[stale] scan error: {exc}\n")
        _stop.wait(SCAN_INTERVAL_SEC)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def _handle_signal(signum, _frame):  # noqa: ANN001
    sys.stderr.write(f"[stale] signal {signum}, stopping\n")
    _stop.set()


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)
    hb = threading.Thread(target=heartbeat_loop, name="hb-stale", daemon=True)
    hb.start()
    sys.stderr.write(
        f"[stale] started pid={os.getpid()} scan_interval={SCAN_INTERVAL_SEC}s "
        f"task_hb={TASK_HEARTBEAT_HOURS}h q={QUESTION_HOURS}h handoff={HANDOFF_HOURS}h\n"
    )
    scan_loop()
    sys.stderr.write("[stale] stopped cleanly\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
