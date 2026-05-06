#!/usr/bin/env python3
# Memory watcher - post-session sync
import sys
import json
import os

try:
    data = json.load(sys.stdin)
    log_dir = os.path.join(os.path.expanduser("~"), ".claude", "hooks-log")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "sessions.log"), "a", encoding="utf-8") as f:
        f.write(f"session ended\n")
except Exception:
    pass

sys.exit(0)
