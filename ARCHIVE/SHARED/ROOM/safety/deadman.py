"""
SHARED/ROOM/safety/deadman.py

BEACON's dead-man's switch.

Runs as a SEPARATE PROCESS from the main room_daemon. Every 60 seconds:
  1. Reads SHARED/ROOM/logs/room_daemon.heartbeat (JSON: {ts, pid, status})
  2. If heartbeat is stale (age > 5 min) or missing → page Unc on Telegram.
  3. Writes its own heartbeat to SHARED/ROOM/logs/deadman.heartbeat.

Why two processes:
  The room_daemon is what everyone depends on. If it dies silently in the
  night, nobody would know until Unc drops a message and nobody wakes. The
  deadman runs independently. It has one job: notice when the daemon stops
  breathing, and scream.

Skeleton scope (R3):
  - Heartbeat read + stale detection: DONE
  - Telegram page: DONE (reuses escalation.page_unc)
  - Double-page suppression: DONE (60-min cooldown per incident)
  - Auto-restart of daemon: NOT in this file. Leaves a restart hook for
    ATLAS/ENVY to decide policy. v1 = alert, don't resurrect.

Run:
  python -m SHARED.ROOM.safety.deadman            # long-running loop
  python -m SHARED.ROOM.safety.deadman --once     # single check (for cron)

Wiring (not in this round per Unc's instruction):
  - Add to Windows Task Scheduler: runs at user login, retries every 1 min.
  - Or include in SHARED/BRIDGE/start-bridge.bat alongside room_daemon.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOM_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

DAEMON_HEARTBEAT = LOG_DIR / "room_daemon.heartbeat"
DEADMAN_HEARTBEAT = LOG_DIR / "deadman.heartbeat"
INCIDENT_FILE = LOG_DIR / "deadman.last_incident"

STALE_THRESHOLD_SEC = 5 * 60   # >5min = dead
COOLDOWN_SEC = 60 * 60          # don't page more than once per hour per incident

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [deadman] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "deadman.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("deadman")


# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

def _read_daemon_heartbeat() -> dict | None:
    if not DAEMON_HEARTBEAT.exists():
        return None
    try:
        data = json.loads(DAEMON_HEARTBEAT.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError) as exc:
        log.warning(f"heartbeat unreadable: {exc}")
    return None


def _heartbeat_age_sec(hb: dict | None) -> float | None:
    if not hb:
        return None
    ts_str = hb.get("ts")
    if not ts_str:
        return None
    try:
        if ts_str.endswith("Z"):
            ts = datetime.fromisoformat(ts_str[:-1]).replace(tzinfo=timezone.utc)
        else:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - ts).total_seconds()


def _should_suppress(now_ts: float) -> bool:
    """60-min cooldown: if we paged in the last hour for this incident, skip."""
    if not INCIDENT_FILE.exists():
        return False
    try:
        data = json.loads(INCIDENT_FILE.read_text(encoding="utf-8"))
        last = float(data.get("last_paged_at", 0))
        return (now_ts - last) < COOLDOWN_SEC
    except (json.JSONDecodeError, OSError, ValueError):
        return False


def _mark_paged(now_ts: float) -> None:
    try:
        INCIDENT_FILE.write_text(
            json.dumps({"last_paged_at": now_ts, "iso": datetime.fromtimestamp(now_ts, tz=timezone.utc).isoformat()}),
            encoding="utf-8",
        )
    except OSError as exc:
        log.warning(f"incident file write failed: {exc}")


def _clear_incident() -> None:
    if INCIDENT_FILE.exists():
        try:
            INCIDENT_FILE.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def _page(text: str) -> bool:
    """Page Unc via the unified pager (IFTTT webhook → email-to-SMS chain)."""
    try:
        sys.path.insert(0, str(ROOM_DIR))
        from safety.pager import page_unc as _pager_page  # type: ignore
        return bool(_pager_page(text, subject="BEACON DEAD-MAN", severity="CRITICAL"))
    except ImportError:
        pass
    except Exception as exc:  # noqa: BLE001
        log.warning(f"pager import failed: {exc}")
    # Absolute last-resort: skip. Log-only.
    log.critical(f"DEADMAN COULD NOT PAGE: {text[:200]}")
    return False


def _heartbeat_self() -> None:
    try:
        DEADMAN_HEARTBEAT.write_text(
            json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "pid": os.getpid(),
                "status": "alive",
            }),
            encoding="utf-8",
        )
    except OSError as exc:
        log.warning(f"self-heartbeat write failed: {exc}")


# ---------------------------------------------------------------------------
# Tick
# ---------------------------------------------------------------------------

def check_once() -> int:
    """One health check. Returns 0 healthy, 1 stale/missing, 2 paged."""
    _heartbeat_self()
    hb = _read_daemon_heartbeat()
    age = _heartbeat_age_sec(hb)
    now_ts = time.time()

    if hb is None:
        log.warning("room_daemon heartbeat MISSING")
        if _should_suppress(now_ts):
            log.info("suppressed (cooldown active)")
            return 1
        ok = _page(
            "BEACON DEAD-MAN ALERT\n"
            "room_daemon heartbeat file is missing. THE ROOM fan-out is offline.\n"
            "Wake tokens will not reach siblings' inboxes. Start the daemon:\n"
            "  python SHARED/ROOM/room_daemon.py"
        )
        if ok:
            _mark_paged(now_ts)
            return 2
        return 1

    if age is not None and age > STALE_THRESHOLD_SEC:
        log.warning(f"room_daemon heartbeat STALE: age={age:.0f}s")
        if _should_suppress(now_ts):
            log.info("suppressed (cooldown active)")
            return 1
        ok = _page(
            f"BEACON DEAD-MAN ALERT\n"
            f"room_daemon heartbeat is {age/60:.1f} minutes stale (threshold {STALE_THRESHOLD_SEC/60:.0f}m).\n"
            f"Daemon pid in heartbeat: {hb.get('pid','?')}. Process may have crashed.\n"
            f"Restart with:  python SHARED/ROOM/room_daemon.py"
        )
        if ok:
            _mark_paged(now_ts)
            return 2
        return 1

    # Healthy — clear any prior incident flag so next outage triggers fresh page.
    _clear_incident()
    log.info(f"healthy: age={age:.0f}s pid={hb.get('pid','?')}")
    return 0


def loop(interval_sec: int = 60) -> None:
    log.info(f"deadman started pid={os.getpid()} interval={interval_sec}s")
    while True:
        try:
            check_once()
        except Exception as exc:  # noqa: BLE001
            log.error(f"check failed: {exc}")
        time.sleep(interval_sec)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="single check (cron mode)")
    p.add_argument("--interval", type=int, default=60, help="loop interval seconds")
    args = p.parse_args()

    if args.once:
        return check_once()
    loop(args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
