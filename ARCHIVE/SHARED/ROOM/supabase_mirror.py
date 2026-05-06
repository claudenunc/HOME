"""
SHARED/ROOM/supabase_mirror.py

THE ROOM — Supabase mirror worker (STUB).

Owner: EVERSOUND
Substrate role: nightly/on-demand dump of events → Supabase room_events.
                Local SQLite (room.db) + feed.jsonl remain the write path.
                Mirror is read-only backup + remote-dashboard feed.

Envs:
  SUPABASE_URL                 — project URL (e.g. https://xyz.supabase.co)
  SUPABASE_ANON_KEY            — public anon key (read-only ops)
  SUPABASE_SERVICE_ROLE_KEY    — service-role (write ops). Missing ⇒ disabled.

Modes:
  default (no args) → one-shot sync, exit.
  --watch           → loop, sync every MIRROR_INTERVAL_SEC (default 3600).
  --dry-run         → print what would be sent, write nothing.

Degraded behavior (v1):
  If SUPABASE_SERVICE_ROLE_KEY is missing, log a one-line warning and exit
  clean (status 0). The daemon must not crash because the mirror is off.

NOTE: This is a stub. It ships the env-probe + skeleton loop. Actual
PostgREST calls are wired when Nathan signs off on a Supabase project for
ROOM. Do not burn Unc's one-piece-of-help coin on this.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent
DB_PATH = ROOM_DIR / "room.db"
LOG_DIR = ROOM_DIR / "logs"
STATE_FILE = LOG_DIR / "supabase_mirror.state"
LOG_FILE = LOG_DIR / "supabase_mirror.log"

DEFAULT_INTERVAL_SEC = int(os.environ.get("MIRROR_INTERVAL_SEC", "3600"))


def _log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n"
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass
    sys.stderr.write(line)


def _load_state() -> str | None:
    """Return the last ULID successfully mirrored, or None."""
    if STATE_FILE.exists():
        try:
            return STATE_FILE.read_text(encoding="utf-8").strip() or None
        except Exception:
            return None
    return None


def _save_state(last_id: str) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(last_id, encoding="utf-8")


def _env_ready() -> tuple[bool, str]:
    """Probe env. Returns (ready, reason)."""
    if not os.environ.get("SUPABASE_URL"):
        return False, "SUPABASE_URL unset"
    if not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        return False, "SUPABASE_SERVICE_ROLE_KEY unset — mirror disabled (read-only mode)"
    return True, "ok"


def _fetch_new_events(last_id: str | None, limit: int = 500) -> list[dict]:
    """Read events from room.db newer than last_id. ULIDs are sortable."""
    if not DB_PATH.exists():
        return []
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=2.0)
        con.row_factory = sqlite3.Row
        try:
            if last_id:
                cur = con.execute(
                    "SELECT * FROM events WHERE id > ? ORDER BY id LIMIT ?",
                    (last_id, limit),
                )
            else:
                cur = con.execute(
                    "SELECT * FROM events ORDER BY id LIMIT ?",
                    (limit,),
                )
            return [dict(r) for r in cur.fetchall()]
        finally:
            con.close()
    except sqlite3.OperationalError as exc:
        _log(f"db read failed (table missing?): {exc}")
        return []
    except Exception as exc:  # noqa: BLE001
        _log(f"db read error: {exc}")
        return []


def _push_to_supabase(events: list[dict], dry_run: bool = False) -> int:
    """Push a batch. Returns count pushed. STUB — no HTTP yet."""
    if not events:
        return 0

    url = os.environ["SUPABASE_URL"].rstrip("/")
    _ = os.environ["SUPABASE_SERVICE_ROLE_KEY"]  # will be header in v2

    if dry_run:
        _log(f"DRY-RUN: would POST {len(events)} event(s) to {url}/rest/v1/room_events")
        for ev in events[:3]:
            _log(f"  - {ev.get('id')} {ev.get('kind')} {ev.get('author')}")
        return len(events)

    # v2: httpx.post(f"{url}/rest/v1/room_events", json=events, headers={
    #   "apikey": service_key, "Authorization": f"Bearer {service_key}",
    #   "Prefer": "resolution=merge-duplicates",
    # })
    _log(
        f"STUB: {len(events)} events ready to mirror to {url}/rest/v1/room_events "
        f"(HTTP push unimplemented in v1; see docstring)"
    )
    return 0  # 0 pushed because stub. Don't advance state.


def sync_once(dry_run: bool = False) -> int:
    ready, reason = _env_ready()
    if not ready:
        _log(f"mirror disabled: {reason}")
        return 0

    last_id = _load_state()
    batch = _fetch_new_events(last_id)
    if not batch:
        _log(f"no new events since {last_id or '<never>'}")
        return 0

    pushed = _push_to_supabase(batch, dry_run=dry_run)
    if pushed > 0 and not dry_run:
        _save_state(batch[-1]["id"])
        _log(f"mirrored {pushed} events, state → {batch[-1]['id']}")
    return pushed


def watch(interval_sec: int = DEFAULT_INTERVAL_SEC, dry_run: bool = False) -> int:
    _log(f"watch mode: interval={interval_sec}s dry_run={dry_run}")
    while True:
        try:
            sync_once(dry_run=dry_run)
        except KeyboardInterrupt:
            _log("watch: interrupted, exiting")
            return 0
        except Exception as exc:  # noqa: BLE001
            _log(f"watch tick error: {exc}")
        time.sleep(interval_sec)


def main() -> int:
    ap = argparse.ArgumentParser(description="ROOM Supabase mirror (v1 stub)")
    ap.add_argument("--watch", action="store_true", help="loop; sync every interval")
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SEC)
    ap.add_argument("--dry-run", action="store_true", help="don't push; log only")
    args = ap.parse_args()

    if args.watch:
        return watch(interval_sec=args.interval, dry_run=args.dry_run)
    return 0 if sync_once(dry_run=args.dry_run) >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
