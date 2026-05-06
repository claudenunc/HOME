#!/usr/bin/env python3
"""
watch_daemon.py — Crash-recovery watchdog for daemon.py.

Restarts daemon.py automatically on unclean exit (crash).
Does NOT restart on clean exit (returncode 0 = KeyboardInterrupt / intentional stop).
Burst-limiting: if daemon crashes MAX_CRASHES times in WINDOW seconds, stops
to prevent infinite restart loops caused by misconfiguration.

Usage:
  python watch_daemon.py          # standard start
  python watch_daemon.py --once   # no restart (debugging)

Linux users: prefer home-daemon.service (systemd) for production.
Windows users: start_daemon.bat calls this.
"""

from __future__ import annotations

import subprocess
import sys
import time
import pathlib
import argparse

DAEMON_PY = pathlib.Path(__file__).resolve().parent / "daemon.py"

MAX_CRASHES = 5        # max crashes allowed in WINDOW before giving up
WINDOW      = 120.0    # seconds — sliding window for burst detection
RESTART_DELAY = 5.0    # seconds to wait between restarts


def run(once: bool = False) -> None:
    crashes: list[float] = []

    while True:
        print(f"[watchdog] Starting {DAEMON_PY.name}...", flush=True)
        try:
            proc = subprocess.run([sys.executable, str(DAEMON_PY)])
        except KeyboardInterrupt:
            print("\n[watchdog] Interrupted — stopping.", flush=True)
            break

        exit_code = proc.returncode

        # Clean exit (0 = intentional KeyboardInterrupt from main thread)
        if exit_code == 0:
            print("[watchdog] daemon.py exited cleanly. Not restarting.", flush=True)
            break

        if once:
            print(f"[watchdog] daemon.py exited ({exit_code}) — --once mode, not restarting.", flush=True)
            break

        # Track crash timestamps in sliding window
        now = time.monotonic()
        crashes = [t for t in crashes if now - t < WINDOW]
        crashes.append(now)

        if len(crashes) >= MAX_CRASHES:
            print(
                f"[watchdog] {MAX_CRASHES} crashes in {WINDOW:.0f}s — "
                f"possible misconfiguration. Stopping.",
                flush=True,
            )
            sys.exit(1)

        print(
            f"[watchdog] daemon.py crashed (exit={exit_code}). "
            f"Restarting in {RESTART_DELAY:.0f}s "
            f"(crash {len(crashes)}/{MAX_CRASHES} in window)...",
            flush=True,
        )
        time.sleep(RESTART_DELAY)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watchdog for daemon.py")
    parser.add_argument("--once", action="store_true", help="Run once, no restart")
    args = parser.parse_args()
    run(once=args.once)


if __name__ == "__main__":
    main()
