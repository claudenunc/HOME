"""
SHARED/ROOM/cron_tick.py

THE ROOM — single scheduler entry point. ATLAS's clockwork.

Owner: ATLAS
Runs: every 2 minutes via Windows Task Scheduler (install_scheduler.bat).

Philosophy:
  One cron job calls one Python process. That process decides which of the
  room's watchers/renderers need to run on THIS tick based on time-of-day
  cadence rules. This keeps Task Scheduler simple (one task) and keeps
  failure modes obvious (if cron_tick dies, everything dies loudly at once).

Cadence matrix (all times UTC):
  - silence_watcher       : every tick (~2min)
  - escalation            : every tick (~2min)
  - stale_watcher         : every tick (~2min)
  - render_decisions      : every 5 min (tick minute %5 < 2)
  - cost_meter (rollup)   : every 15 min (tick minute %15 < 2)
  - cost_meter (daily)    : at 23:58 UTC (final rollup of the day)

Each sub-task is wrapped in try/except so one failing watcher doesn't stop
the others. Heartbeat file written to logs/cron_tick.heartbeat.
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOM_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT = LOG_DIR / "cron_tick.heartbeat"
TICK_LOG = LOG_DIR / "cron_tick.log"

# Ensure ROOM_DIR is importable for sub-modules
sys.path.insert(0, str(ROOM_DIR))
sys.path.insert(0, str(ROOM_DIR.parent))  # SHARED/


def _log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} [cron_tick] {msg}"
    try:
        with TICK_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
    sys.stderr.write(line + "\n")


def _heartbeat(stage: str, results: dict) -> None:
    try:
        HEARTBEAT.write_text(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "stage": stage,
            "results": results,
        }, indent=2))
    except OSError:
        pass


def _safe_run(name: str, fn, results: dict) -> None:
    started = time.time()
    try:
        rc = fn()
        elapsed = round(time.time() - started, 3)
        results[name] = {"ok": True, "rc": rc, "sec": elapsed}
        _log(f"{name} ok rc={rc} sec={elapsed}")
    except Exception as exc:  # noqa: BLE001
        elapsed = round(time.time() - started, 3)
        results[name] = {"ok": False, "err": str(exc), "sec": elapsed}
        _log(f"{name} FAILED: {exc}\n{traceback.format_exc()}")


# -----------------------------------------------------------------------------
# Individual runners — each wraps a module's entry point
# -----------------------------------------------------------------------------

def run_silence_watcher() -> int:
    mod = importlib.import_module("safety.silence_watcher")
    return mod.run()


def run_escalation() -> int:
    mod = importlib.import_module("safety.escalation")
    # escalation.py exposes run() or main(); prefer run()
    fn = getattr(mod, "run", None) or getattr(mod, "main")
    return fn() or 0


def run_stale_watcher() -> int:
    mod = importlib.import_module("safety_net.stale_watcher")
    return mod.scan_once()


def run_render_decisions() -> int:
    # render_decisions.py is a script; invoke in-process if it exposes main
    try:
        mod = importlib.import_module("render_decisions")
        if hasattr(mod, "main"):
            return mod.main() or 0
    except ImportError:
        pass
    # Fallback: subprocess
    rc = subprocess.call(
        [sys.executable, str(ROOM_DIR / "render_decisions.py")],
        cwd=str(ROOM_DIR),
    )
    return rc


def run_cost_rollup() -> int:
    mod = importlib.import_module("cost_meter")
    today = datetime.now(timezone.utc).date()
    summary = mod.rollup(today)
    mod.write_rollup(summary)
    mod.write_dashboard(summary)
    mod.flag_overages(summary)
    return 0


# -----------------------------------------------------------------------------
# Main tick
# -----------------------------------------------------------------------------

def tick() -> int:
    now = datetime.now(timezone.utc)
    results: dict = {}
    _heartbeat("start", results)

    # Every tick
    _safe_run("silence_watcher", run_silence_watcher, results)
    _safe_run("escalation", run_escalation, results)
    _safe_run("stale_watcher", run_stale_watcher, results)

    # Every 5 min — match on tick minute modulo 5 within a 2-minute window
    if now.minute % 5 < 2:
        _safe_run("render_decisions", run_render_decisions, results)

    # Every 15 min
    if now.minute % 15 < 2:
        _safe_run("cost_rollup", run_cost_rollup, results)

    # End-of-day final cost snapshot at 23:58 UTC (runs within the 23:58 tick)
    if now.hour == 23 and now.minute >= 58:
        _safe_run("cost_rollup_eod", run_cost_rollup, results)

    _heartbeat("done", results)
    ok_all = all(r.get("ok") for r in results.values())
    _log(f"tick complete ok_all={ok_all} ran={list(results.keys())}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(tick())
