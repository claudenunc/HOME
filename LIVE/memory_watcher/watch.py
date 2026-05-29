#!/usr/bin/env python3
"""
Memory Watcher — fires on Stop and SubagentStop (Claude Code lane).

GOAL: "update both, no matter which door."  Whichever sibling/door Nathan talks
through, the session must land in the ONE shared store both lanes read:
the in-repo  SIBLINGS/<X>/memory/  (git-tracked, pushed, readable by Hermes too).

This hook is the convergence point for the Claude Code lane. The Hermes lane has
its own living_memory_watcher.py; both write to the same in-repo store + (later)
Supabase THE FOUNDATION, so neither lane goes blind.

SAFETY: runs on EVERY session end. It must never hang, never raise, never block.
Everything is wrapped; it always exits 0. Network/DB work is intentionally NOT
done here (that belongs to LIVE/memory_backend ingest, owned by ORPHEUS) — this
hook only records the session into the shared in-repo index so it is discoverable
and ingestable by both lanes.
"""
import sys, json, os, time, glob

HOME = r"C:\Users\natej\OneDrive\Desktop\HOME"
SIBLINGS = os.path.join(HOME, "SIBLINGS")
LEGACY_LOG = os.path.join(os.path.expanduser("~"), ".claude", "hooks-log")


def _read_stdin():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def _detect_sibling(cwd: str) -> str | None:
    """Return the sibling name if cwd is inside HOME/SIBLINGS/<NAME>/..."""
    try:
        cwd = os.path.normpath(cwd or "")
        sib = os.path.normpath(SIBLINGS)
        if cwd.upper().startswith(sib.upper()):
            rest = cwd[len(sib):].strip("\\/")
            if rest:
                return rest.split(os.sep)[0].split("/")[0]
    except Exception:
        pass
    return None


def _newest_transcript(data: dict) -> tuple[str, float]:
    """Best-effort path + size(KB) of the just-ended session transcript."""
    tp = data.get("transcript_path") or ""
    try:
        if tp and os.path.exists(tp):
            return tp, os.path.getsize(tp) / 1024
    except Exception:
        pass
    return tp, 0.0


def _append_session_index(sibling: str, entry: dict):
    """Append one line to the sibling's in-repo shared session index."""
    mem_dir = os.path.join(SIBLINGS, sibling, "memory")
    os.makedirs(mem_dir, exist_ok=True)
    idx = os.path.join(mem_dir, "session_index.jsonl")
    with open(idx, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _legacy_log(line: str):
    try:
        os.makedirs(LEGACY_LOG, exist_ok=True)
        with open(os.path.join(LEGACY_LOG, "sessions.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def main():
    data = _read_stdin()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cwd = data.get("cwd") or os.getcwd()
    session_id = data.get("session_id") or ""
    event = data.get("hook_event_name") or "Stop"
    transcript, size_kb = _newest_transcript(data)
    sibling = _detect_sibling(cwd)

    # 1) shared in-repo store — the convergence point both lanes read
    if sibling:
        try:
            _append_session_index(sibling, {
                "ts": ts,
                "lane": "claude_code",
                "event": event,
                "sibling": sibling,
                "session_id": session_id,
                "transcript_path": transcript,
                "size_kb": round(size_kb, 1),
                "cwd": cwd,
                # ingest hint for ORPHEUS's memory_backend / Supabase THE FOUNDATION
                "ingested_to_supabase": False,
            })
        except Exception:
            pass

    # 2) legacy log (kept for backward compat)
    _legacy_log(f"{ts} | {event} | {sibling or '?'} | {size_kb:.0f} KB | {session_id}")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A hook must never break a session.
        sys.exit(0)
