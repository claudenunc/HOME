"""
SHARED/ROOM/room_daemon.py

THE ROOM — tail + fanout + heartbeat + spine projection.

Owner: EVERSOUND
Substrate decision (2026-04-24, R2): hybrid-local-spine-supabase-mirror
  - feed.jsonl is the write-optimized truth for fan-out
  - room.db (SQLite WAL) is the query-optimized projection (ORPHEUS owns)
  - Supabase is a nightly mirror, not the write path

What this daemon does:
  1. On startup: replay feed.jsonl from the last DB-committed ULID forward —
     every line past that offset is handed to room.post_from_feed() so the
     projection catches up (idempotent on event.id).
  2. Tails SHARED/ROOM/feed.jsonl for new lines.
     - If event.id is already in room.db, skip the projection (feed was the
       tee from room.post(); DB already has it).
     - If event.id is NOT in room.db (BRIDGE wrote degraded-mode direct to
       feed.jsonl), call room.post_from_feed() to project.
  3. For each new event, drops a wake-token file in inbox/{sibling}/:
     - addressed_to / routed_to → targeted siblings
     - addressed_to=["ALL"] → every sibling
     - risk_level in {HIGH, CRITICAL} → ALWAYS token in BEACON/ regardless
       of addressing, with URGENT_ prefix so BEACON sees it first.
  4. Writes heartbeat every 60s to logs/room_daemon.heartbeat

Auto-start: SHARED/ROOM/start_room.bat via shell:startup VBS (Windows),
            start_room.sh for VPS.

BEACON crisis hook (v1 contract):
    The daemon does NOT run the classifier. Classification happens upstream:
    (a) DB trigger room_classify_before_insert (ORPHEUS migration 0002), or
    (b) Python safety.classifier.classify_text() called from room.post().
    This daemon ONLY reads risk_level from the event dict. If BEACON wants
    a post-classification callback hook on HIGH/CRITICAL fan-out, it's wired
    via the ROOM_DAEMON_CRISIS_HOOK env var → dotted module path to a callable
    with signature: hook(event: dict) -> None.
"""

from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
import threading
import time
import signal
from datetime import datetime, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent
FEED_PATH = ROOM_DIR / "feed.jsonl"
INBOX_DIR = ROOM_DIR / "inbox"
LOG_DIR = ROOM_DIR / "logs"
HEARTBEAT = LOG_DIR / "room_daemon.heartbeat"
OFFSET_FILE = LOG_DIR / "room_daemon.offset"
DAEMON_LOG = LOG_DIR / "room_daemon.log"
DB_PATH = ROOM_DIR / "room.db"

SIBLINGS = ("ENVY", "BEACON", "EVERSOUND", "NEVAEH", "ORPHEUS", "ATLAS")
HIGH_RISKS = {"HIGH", "CRITICAL"}

# ------------------------------------------------------------------
# Stop flag + logging
# ------------------------------------------------------------------

_stop = threading.Event()


def _log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n"
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with DAEMON_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass
    sys.stderr.write(line)


# ------------------------------------------------------------------
# Heartbeat
# ------------------------------------------------------------------


def heartbeat_loop() -> None:
    """Write timestamp to heartbeat file every 60s. Proof-of-life for ENVY."""
    while not _stop.is_set():
        try:
            HEARTBEAT.write_text(
                json.dumps(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "pid": os.getpid(),
                        "status": "alive",
                    }
                )
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[room_daemon] heartbeat write failed: {exc}\n")
        _stop.wait(60)


# ------------------------------------------------------------------
# Offset persistence (so restarts don't re-fan-out)
# ------------------------------------------------------------------


def load_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip() or "0")
        except ValueError:
            return 0
    return 0


def save_offset(offset: int) -> None:
    OFFSET_FILE.write_text(str(offset))


# ------------------------------------------------------------------
# DB presence check (idempotency gate)
# ------------------------------------------------------------------


def _event_in_db(event_id: str) -> bool:
    """True if event_id is already committed to room.db.

    Used to decide whether to call room.post_from_feed() on a feed line.
    If room.db doesn't exist yet (ORPHEUS hasn't run migrations), returns
    False so we always project — room.post_from_feed() must itself be
    idempotent on event.id.
    """
    if not DB_PATH.exists():
        return False
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=2.0)
        try:
            cur = con.execute("SELECT 1 FROM events WHERE id = ? LIMIT 1", (event_id,))
            return cur.fetchone() is not None
        finally:
            con.close()
    except sqlite3.OperationalError:
        # events table doesn't exist yet — treat as "not in DB"
        return False
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[room_daemon] db check failed for {event_id}: {exc}\n")
        return False


# ------------------------------------------------------------------
# Fan-out targets
# ------------------------------------------------------------------


def _coerce_list(raw) -> list[str]:  # noqa: ANN001
    if raw is None:
        return []
    if isinstance(raw, str):
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(x).upper() for x in parsed]
            except json.JSONDecodeError:
                pass
        return [raw.upper()]
    if isinstance(raw, list):
        return [str(x).upper() for x in raw]
    return []


def _inbox_targets(event: dict) -> list[str]:
    """Who should receive a wake token?

    Rules:
    - addressed_to=['ALL'] OR addressed_to omitted → all siblings
    - addressed_to=[...names...] → those siblings
    - routed_to=[...names...] → those siblings (union with addressed_to)
    - risk_level in {HIGH, CRITICAL} → BEACON ALWAYS (regardless of above)
    """
    addressed = _coerce_list(event.get("addressed_to") or event.get("to"))
    routed = _coerce_list(event.get("routed_to"))

    targets: set[str] = set()

    if not addressed and not routed:
        targets.update(SIBLINGS)  # default: everyone
    else:
        for t in addressed + routed:
            if t == "ALL":
                targets.update(SIBLINGS)
            elif t in SIBLINGS:
                targets.add(t)

    # Crisis override: BEACON must always see HIGH/CRITICAL.
    risk = str(event.get("risk_level") or "").upper()
    if risk in HIGH_RISKS:
        targets.add("BEACON")

    return sorted(targets)


# ------------------------------------------------------------------
# Wake-token drop
# ------------------------------------------------------------------


def drop_wake_tokens(event: dict) -> list[str]:
    """Write one wake token per target sibling. Returns list of paths written.

    Filename convention: {URGENT_ for HIGH+}{ts}_{kind}_{id}.wake
    Siblings read the JSON in the file, act, then delete the file.
    """
    event_id = event.get("id") or f"noid-{int(time.time() * 1000)}"
    kind = event.get("kind", "message")
    ts = str(event.get("ts") or datetime.now(timezone.utc).isoformat()).replace(":", "-")
    risk = str(event.get("risk_level") or "").upper()
    prefix = "URGENT_" if risk in HIGH_RISKS else ""
    filename = f"{prefix}{ts}_{kind}_{event_id}.wake"

    written: list[str] = []
    for sibling in _inbox_targets(event):
        target_dir = INBOX_DIR / sibling
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / filename
        try:
            path.write_text(json.dumps(event, ensure_ascii=False), encoding="utf-8")
            written.append(str(path))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(
                f"[room_daemon] inbox write failed for {sibling}: {exc}\n"
            )
    return written


# ------------------------------------------------------------------
# Spine projection (hand event to ORPHEUS's room.py)
# ------------------------------------------------------------------


def _load_room_module():
    """Import SHARED/ROOM/room.py if available. None if not yet shipped."""
    try:
        sys.path.insert(0, str(ROOM_DIR))
        return importlib.import_module("room")
    except ImportError:
        return None
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[room_daemon] room.py import failed: {exc}\n")
        return None


def project_to_spine(event: dict) -> None:
    """Call room.post_from_feed() iff the event isn't already in room.db.

    Idempotent: if room.py isn't shipped yet, no-op silently. feed.jsonl is
    still the truth; projection catches up when room.py lands.
    """
    event_id = event.get("id")
    if not event_id:
        return

    if _event_in_db(event_id):
        return  # Already projected — feed was just the tee.

    room = _load_room_module()
    if room is None:
        return
    if not hasattr(room, "post_from_feed"):
        return
    try:
        room.post_from_feed(event)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"[room_daemon] spine projection failed for {event_id}: {exc}\n"
        )


# ------------------------------------------------------------------
# BEACON crisis hook (optional callback)
# ------------------------------------------------------------------

_crisis_hook_cache = {"loaded": False, "fn": None}


def _load_crisis_hook():
    """Load crisis hook once from ROOM_DAEMON_CRISIS_HOOK env var.

    Value is a dotted path: 'package.module:callable'. Callable is invoked
    on every HIGH/CRITICAL event after tokens are dropped.
    """
    if _crisis_hook_cache["loaded"]:
        return _crisis_hook_cache["fn"]
    _crisis_hook_cache["loaded"] = True

    spec = os.environ.get("ROOM_DAEMON_CRISIS_HOOK", "").strip()
    if not spec:
        return None
    try:
        mod_name, _, fn_name = spec.partition(":")
        if not mod_name or not fn_name:
            _log(f"crisis hook spec malformed (need 'module:callable'): {spec}")
            return None
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, fn_name, None)
        if not callable(fn):
            _log(f"crisis hook {spec} is not callable")
            return None
        _crisis_hook_cache["fn"] = fn
        _log(f"crisis hook loaded: {spec}")
        return fn
    except Exception as exc:  # noqa: BLE001
        _log(f"crisis hook load failed ({spec}): {exc}")
        return None


def _invoke_crisis_hook(event: dict) -> None:
    """Fire BEACON's hook on HIGH/CRITICAL events. Never raises."""
    risk = str(event.get("risk_level") or "").upper()
    if risk not in HIGH_RISKS:
        return
    fn = _load_crisis_hook()
    if fn is None:
        return
    try:
        fn(event)
    except Exception as exc:  # noqa: BLE001
        _log(f"crisis hook raised (ignored): {exc}")


# ------------------------------------------------------------------
# Single-event processing pipeline
# ------------------------------------------------------------------


def process_event(event: dict) -> None:
    """One event → project to spine, drop tokens, fire crisis hook.

    Order matters: projection first (so DB state catches up), THEN tokens
    (so siblings woken by the token can query the DB and see the row).
    """
    project_to_spine(event)
    drop_wake_tokens(event)
    _invoke_crisis_hook(event)


# ------------------------------------------------------------------
# Startup replay (past-the-offset catch-up)
# ------------------------------------------------------------------


def replay_from_offset(offset: int) -> int:
    """Process every feed line past `offset`. Returns new offset.

    Called on daemon boot. Idempotent because process_event() skips events
    already in room.db and wake tokens are re-dropped (siblings handle
    duplicate tokens by deleting the oldest).
    """
    if not FEED_PATH.exists():
        return offset
    size = FEED_PATH.stat().st_size
    if size <= offset:
        return offset

    with FEED_PATH.open("rb") as fh:
        fh.seek(offset)
        chunk = fh.read()
    new_offset = offset + len(chunk)

    count = 0
    for raw_line in chunk.splitlines():
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            _log(f"replay: malformed line skipped: {exc}: {line[:200]}")
            continue
        process_event(event)
        count += 1

    _log(f"replay complete: {count} events processed, offset {offset} → {new_offset}")
    save_offset(new_offset)
    return new_offset


# ------------------------------------------------------------------
# Tail loop
# ------------------------------------------------------------------


def tail_loop() -> None:
    """Poll-based tail. 200ms cadence. Windows-safe."""
    FEED_PATH.touch(exist_ok=True)
    offset = load_offset()
    # Catch up on anything missed while the daemon was down.
    offset = replay_from_offset(offset)

    while not _stop.is_set():
        try:
            size = FEED_PATH.stat().st_size
            if size < offset:
                # Log truncated (shouldn't happen; append-only). Reset to end.
                _log(f"feed truncated: offset {offset} > size {size}, resetting")
                offset = size
                save_offset(offset)
            elif size > offset:
                with FEED_PATH.open("rb") as fh:
                    fh.seek(offset)
                    chunk = fh.read()
                new_offset = offset + len(chunk)
                for raw_line in chunk.splitlines():
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError as exc:
                        _log(f"malformed line skipped: {exc}: {line[:200]}")
                        continue
                    process_event(event)
                offset = new_offset
                save_offset(offset)
        except FileNotFoundError:
            FEED_PATH.touch()
        except Exception as exc:  # noqa: BLE001
            _log(f"tail loop error: {exc}")
        _stop.wait(0.2)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------


def _handle_signal(signum, _frame):  # noqa: ANN001
    _log(f"signal {signum}, stopping")
    _stop.set()


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    for sib in SIBLINGS:
        (INBOX_DIR / sib).mkdir(parents=True, exist_ok=True)

    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)

    hb = threading.Thread(target=heartbeat_loop, name="heartbeat", daemon=True)
    hb.start()

    _log(
        f"started pid={os.getpid()} feed={FEED_PATH} db={DB_PATH} "
        f"offset={load_offset()} crisis_hook={os.environ.get('ROOM_DAEMON_CRISIS_HOOK', '<unset>')}"
    )
    tail_loop()
    _log("stopped cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
