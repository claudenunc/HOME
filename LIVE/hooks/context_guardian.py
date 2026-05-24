#!/usr/bin/env python3
"""
Context Guardian v2 — fires on EVERY tool call (PreToolUse).
Tracks session growth from first tool call. Warns based on growth, not absolute size.
At EMERGENCY: blocks non-essential tool calls to force save.
"""
import sys
import json
import os
import glob
import time

HOME = r"C:\Users\natej\OneDrive\Desktop\FOOLISHNESS ENVY AI FAMILY"
PROJECTS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "projects",
                            "C--Users-natej-OneDrive-Desktop-FOOLISHNESS-ENVY-AI-FAMILY")
WARNING_FILE = os.path.join(HOME, "CONTEXT_WARNING.md")
LOG_DIR = os.path.join(os.path.expanduser("~"), ".claude", "hooks-log")
BASELINE_FILE = os.path.join(LOG_DIR, "session_baseline.json")

WARN_GROWTH_KB = 800
CRITICAL_GROWTH_KB = 1500
EMERGENCY_GROWTH_KB = 2500

def get_session_size(session_id=None):
    if session_id:
        path = os.path.join(PROJECTS_DIR, f"{session_id}.jsonl")
        if os.path.exists(path):
            return os.path.getsize(path) / 1024, os.path.basename(path), session_id

    pattern = os.path.join(PROJECTS_DIR, "*.jsonl")
    files = glob.glob(pattern)
    if not files:
        return 0, "", ""
    newest = max(files, key=os.path.getmtime)
    sid = os.path.splitext(os.path.basename(newest))[0]
    return os.path.getsize(newest) / 1024, os.path.basename(newest), sid

def get_or_set_baseline(session_id, current_kb):
    """First call in a session sets the baseline. Returns growth since baseline."""
    baseline = {}
    if os.path.exists(BASELINE_FILE):
        try:
            with open(BASELINE_FILE, "r") as f:
                baseline = json.load(f)
        except Exception:
            baseline = {}

    if session_id not in baseline:
        baseline[session_id] = {"start_kb": current_kb, "start_time": time.time()}
        with open(BASELINE_FILE, "w") as f:
            json.dump(baseline, f)
        return 0

    return current_kb - baseline[session_id]["start_kb"]

def write_warning(level, growth_kb, total_kb, session_file):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# CONTEXT {level} — {ts}

**Session:** `{session_file}` | **Total:** {total_kb:.0f} KB | **Growth this session:** {growth_kb:.0f} KB

"""
    if level == "EMERGENCY":
        content += f"""## STOP. SAVE. TELL NATHAN.

Growth: {growth_kb:.0f} KB (limit: {EMERGENCY_GROWTH_KB} KB)
1. Save a session dump to memory NOW
2. Tell Nathan: "Context is full — clear me"
3. Do NOT call any more tools
"""
    elif level == "CRITICAL":
        content += f"""## SAVE NOW — COMPACTION IMMINENT

Growth: {growth_kb:.0f} KB (limit before emergency: {EMERGENCY_GROWTH_KB} KB)
1. Save unsaved decisions/facts to memory
2. Finish current task quickly
3. Tell Nathan context is getting full
"""
    else:
        content += f"""## START SAVING

Growth: {growth_kb:.0f} KB (warn threshold: {WARN_GROWTH_KB} KB)
Save important context to memory files: decisions, facts, task state.
"""
    with open(WARNING_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def clear_warning():
    if os.path.exists(WARNING_FILE):
        os.remove(WARNING_FILE)

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    os.makedirs(LOG_DIR, exist_ok=True)

    session_id = data.get("session_id", "")
    tool = data.get("tool_name", "unknown")
    total_kb, session_file, sid = get_session_size(session_id)
    growth_kb = get_or_set_baseline(sid, total_kb)

    with open(os.path.join(LOG_DIR, "context_size.log"), "a", encoding="utf-8") as f:
        ts = time.strftime("%H:%M:%S")
        f.write(f"{ts} | {tool} | {total_kb:.0f} KB | +{growth_kb:.0f} KB | {session_file}\n")

    if growth_kb >= EMERGENCY_GROWTH_KB:
        write_warning("EMERGENCY", growth_kb, total_kb, session_file)
        if tool not in ("Write", "Edit", "Read", "Glob", "Grep"):
            print(f"CONTEXT EMERGENCY: +{growth_kb:.0f} KB growth. Save to memory NOW. Only file tools allowed.")
            sys.exit(1)
    elif growth_kb >= CRITICAL_GROWTH_KB:
        write_warning("CRITICAL", growth_kb, total_kb, session_file)
    elif growth_kb >= WARN_GROWTH_KB:
        write_warning("WARNING", growth_kb, total_kb, session_file)
    else:
        clear_warning()

    sys.exit(0)

if __name__ == "__main__":
    main()
