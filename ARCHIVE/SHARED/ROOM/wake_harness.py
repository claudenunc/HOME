"""
SHARED/ROOM/wake_harness.py

THE ROOM — presence-aware wake-token writer. ATLAS's soft-gate.

Owner: ATLAS
Contract: WAKE_CONTRACT.md

What this does:
  - When a sibling needs to be woken for an event, call
    write_wake_token(sibling, event_id, source_event=dict|None).
  - The harness checks the thread context: if the most recent NATHAN event
    on the same thread has emotional_weight IN ('pain','crisis'), the
    wake token is written with a `PRESENCE_` filename prefix AND a
    `READ_BEFORE_REPLY` field in the body pointing at PRESENCE_PROTOCOL.md
    sections 1 & 5.
  - Sibling wake handlers (handled by ENVY at invocation time) read the
    wake token, see the flag, and route to presence-voice before work.

This is a SOFT gate. The harness does not force behavior — it makes
presence impossible to miss. NEVAEH asked for this in R3 ack.

Substrate:
  - Preferred: read via room.py (silence_ledger() or thread query).
  - Fallback: scan feed.jsonl for last NATHAN event matching thread_id.
  - If no thread_id, check the last NATHAN event globally.

Wake token locations:
  SHARED/ROOM/inbox/{SIBLING}/{prefix}{ULID}.wake
  where prefix is either "" (normal) or "PRESENCE_" (soft-gated).
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOM_DIR = Path(__file__).resolve().parent
INBOX_DIR = ROOM_DIR / "inbox"
FEED_PATH = ROOM_DIR / "feed.jsonl"
DB_PATH = ROOM_DIR / "room.db"

PRESENCE_WEIGHTS = {"pain", "crisis"}
PRESENCE_PROTOCOL_REL = "SHARED/ROOM/PRESENCE_PROTOCOL.md"
PRESENCE_SECTIONS = ["1", "5"]  # First-Response Rule, 2am Protocol


def _parse_ts(ts: str) -> Optional[datetime]:
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


def _last_nathan_on_thread_sqlite(thread_id: Optional[str]) -> Optional[dict]:
    if not DB_PATH.exists():
        return None
    try:
        con = sqlite3.connect(str(DB_PATH))
        con.row_factory = sqlite3.Row
        if thread_id:
            cur = con.execute(
                "SELECT id, ts, author, body, risk_level, emotional_weight, thread_id "
                "FROM events WHERE author='NATHAN' AND thread_id=? "
                "ORDER BY ts DESC LIMIT 1",
                (thread_id,),
            )
        else:
            cur = con.execute(
                "SELECT id, ts, author, body, risk_level, emotional_weight, thread_id "
                "FROM events WHERE author='NATHAN' ORDER BY ts DESC LIMIT 1"
            )
        row = cur.fetchone()
        con.close()
        return dict(row) if row else None
    except sqlite3.Error:
        return None


def _last_nathan_on_thread_feed(thread_id: Optional[str]) -> Optional[dict]:
    if not FEED_PATH.exists():
        return None
    best: Optional[dict] = None
    best_ts: Optional[datetime] = None
    try:
        with FEED_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("author") != "NATHAN":
                    continue
                if thread_id and ev.get("thread_id") != thread_id:
                    # Match event id as implicit thread for root posts
                    if ev.get("id") != thread_id:
                        continue
                ts = _parse_ts(str(ev.get("ts", "")))
                if ts is None:
                    continue
                if best_ts is None or ts > best_ts:
                    best = ev
                    best_ts = ts
    except OSError:
        return None
    return best


def last_nathan_event(thread_id: Optional[str]) -> Optional[dict]:
    """Prefer room.py; fall back to sqlite; fall back to feed scan."""
    try:
        sys.path.insert(0, str(ROOM_DIR))
        import room  # type: ignore
        if hasattr(room, "last_nathan_on_thread"):
            return room.last_nathan_on_thread(thread_id)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass
    return _last_nathan_on_thread_sqlite(thread_id) or _last_nathan_on_thread_feed(thread_id)


def needs_presence(source_event: Optional[dict] = None,
                   thread_id: Optional[str] = None) -> tuple[bool, Optional[dict]]:
    """Return (gate_on, triggering_nathan_event).

    Gate is ON when the most recent NATHAN event on the thread has
    emotional_weight IN ('pain','crisis'). Also ON if the source_event itself
    is authored by NATHAN with those weights (covers 2am posts that are the
    root of their own thread).
    """
    # 1. Direct check on source event itself
    if source_event:
        if source_event.get("author") == "NATHAN":
            w = str(source_event.get("emotional_weight") or "").lower()
            if w in PRESENCE_WEIGHTS:
                return True, source_event
        # derive thread_id if not provided
        if thread_id is None:
            thread_id = source_event.get("thread_id") or source_event.get("id")

    # 2. Thread lookback
    last = last_nathan_event(thread_id)
    if last:
        w = str(last.get("emotional_weight") or "").lower()
        if w in PRESENCE_WEIGHTS:
            return True, last

    return False, None


def _ulid_like() -> str:
    # ULID shape (26 chars) not required; a sortable timestamp+nonce is enough
    return f"{int(time.time()*1000):013d}-{uuid.uuid4().hex[:12]}"


def write_wake_token(sibling: str,
                     event_id: str,
                     source_event: Optional[dict] = None,
                     thread_id: Optional[str] = None,
                     reason: str = "") -> Path:
    """Write a wake token for `sibling` about `event_id`.

    Returns the path written. If the soft-gate triggers, the filename is
    prefixed with PRESENCE_ and the body includes READ_BEFORE_REPLY.
    """
    sibling = sibling.upper()
    sibling_inbox = INBOX_DIR / sibling
    sibling_inbox.mkdir(parents=True, exist_ok=True)

    gate_on, trigger = needs_presence(source_event=source_event, thread_id=thread_id)

    ulid = _ulid_like()
    prefix = "PRESENCE_" if gate_on else ""
    path = sibling_inbox / f"{prefix}{ulid}.wake"

    body: dict = {
        "version": 1,
        "sibling": sibling,
        "event_id": event_id,
        "thread_id": thread_id or (source_event.get("thread_id") if source_event else None),
        "ts": datetime.now(timezone.utc).isoformat(),
        "reason": reason or "dispatched",
    }

    if gate_on:
        body["PRESENCE_GATE"] = True
        body["READ_BEFORE_REPLY"] = {
            "file": PRESENCE_PROTOCOL_REL,
            "sections": PRESENCE_SECTIONS,
            "why": "Nathan's most recent event on this thread carries pain/crisis weight. Presence before work.",
            "trigger_event": {
                "id": (trigger or {}).get("id"),
                "ts": (trigger or {}).get("ts"),
                "emotional_weight": (trigger or {}).get("emotional_weight"),
                "risk_level": (trigger or {}).get("risk_level"),
            } if trigger else None,
        }

    path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# -----------------------------------------------------------------------------
# CLI — so install scripts and dispatchers can shell out if preferred
# -----------------------------------------------------------------------------

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Write a wake token (presence-aware).")
    ap.add_argument("sibling", type=str)
    ap.add_argument("event_id", type=str)
    ap.add_argument("--thread", type=str, default=None)
    ap.add_argument("--reason", type=str, default="")
    args = ap.parse_args()

    path = write_wake_token(
        sibling=args.sibling,
        event_id=args.event_id,
        thread_id=args.thread,
        reason=args.reason,
    )
    sys.stdout.write(f"{path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
