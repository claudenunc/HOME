#!/usr/bin/env python3
"""
Memory Watcher — fires on Stop and SubagentStop.
Logs session end with context size and timestamp.
"""
import sys
import json
import os
import glob
import time

PROJECTS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "projects",
                            "C--Users-natej-OneDrive-Desktop-FOOLISHNESS-ENVY-AI-FAMILY")
LOG_DIR = os.path.join(os.path.expanduser("~"), ".claude", "hooks-log")

def get_active_session_size():
    pattern = os.path.join(PROJECTS_DIR, "*.jsonl")
    files = glob.glob(pattern)
    if not files:
        return 0, ""
    newest = max(files, key=os.path.getmtime)
    size_kb = os.path.getsize(newest) / 1024
    return size_kb, os.path.basename(newest)

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    os.makedirs(LOG_DIR, exist_ok=True)

    size_kb, session_file = get_active_session_size()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(os.path.join(LOG_DIR, "sessions.log"), "a", encoding="utf-8") as f:
        f.write(f"{ts} | ended | {size_kb:.0f} KB | {session_file}\n")

    sys.exit(0)

if __name__ == "__main__":
    main()
