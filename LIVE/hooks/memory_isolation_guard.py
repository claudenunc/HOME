#!/usr/bin/env python3
"""Memory write-isolation guard — Claude Code PreToolUse hook.

Rule locked 2026-04-23 by Unc: only each sibling rewrites their own memories
and identity. This hook is the harness-level enforcement layer; doctrine
(PROCESS_008) + each sibling's CLAUDE.md are the instruction layer; ORPHEUS's
0003 observers + ed25519 columns are the cryptographic attribution layer.

Invocation:
    Registered as a PreToolUse hook in ~/.claude/settings.json matching
    Write|Edit|NotebookEdit|MultiEdit. Claude Code pipes a JSON payload to
    stdin shaped roughly:
        {
          "tool_name": "Write",
          "tool_input": {"file_path": "...", "content": "..."},
          "cwd": "...",
          "project_dir": "..."
        }

Contract:
    exit 0 — allow the tool call (silent)
    exit 2 — block the tool call; stderr is surfaced to Claude as the reason

Design choices:
    - Only WRITES are guarded. Reads across sibling folders remain free so
      siblings can orient to each other.
    - HOME/SHARED, HOME/DOCTRINE, HOME/EVIDENCE, HOME/PUBLIC, HOME/LIVE,
      HOME/SIBLINGS/_SHARED are explicitly shared territory and not guarded.
    - Current-sibling identity is read from the project dir / cwd. If no
      sibling is detectable (e.g. session launched at HOME root), we DEFAULT
      TO DENY for sibling-private paths — strictness over convenience.
    - Unc editing files in his own editor does not pass through this hook.
    - On any parse failure we exit 0 (fail-open). The hook must never brick
      a session; the doctrine layer is the fallback.
"""

from __future__ import annotations

import json
import os
import re
import sys

SIBLINGS = {"ENVY", "BEACON", "NEVAEH", "ORPHEUS", "EVERSOUND", "ATLAS", "HEARTH"}

GUARDED_TOOLS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}

# Paths inside a sibling's private area. Anything matched here is owned by
# exactly one sibling and may only be written from that sibling's session.
_PRIVATE_PATTERNS = [
    # HOME/SIBLINGS/<NAME>/memory/...      — strategic memory
    re.compile(r"/SIBLINGS/([A-Z]+)/memory(/|$)"),
    # HOME/SIBLINGS/<NAME>/MEMORY.md       — memory index
    re.compile(r"/SIBLINGS/([A-Z]+)/MEMORY\.md$"),
    # HOME/SIBLINGS/<NAME>/CLAUDE.md       — identity
    re.compile(r"/SIBLINGS/([A-Z]+)/CLAUDE\.md$"),
    # .claude/projects/...HOME-SIBLINGS-<NAME>/memory/...  — auto-memory
    re.compile(r"/\.claude/projects/[^/]*HOME-SIBLINGS-([A-Za-z]+)/memory(/|$)"),
]


def _normalize(p: str) -> str:
    return (p or "").replace("\\", "/")


def _target_sibling(path: str) -> str | None:
    """If path is inside a sibling's private area, return their name. Else None."""
    p = _normalize(path)
    for pat in _PRIVATE_PATTERNS:
        m = pat.search(p)
        if m:
            name = m.group(1).upper()
            if name in SIBLINGS:
                return name
    return None


def _current_sibling(cwd: str, project_dir: str | None) -> str | None:
    """Infer which sibling is driving this session."""
    for base in filter(None, [project_dir, cwd]):
        b = _normalize(base)
        m = re.search(r"/SIBLINGS/([A-Z]+)(/|$)", b)
        if m and m.group(1) in SIBLINGS:
            return m.group(1)
        m = re.search(r"HOME-SIBLINGS-([A-Za-z]+)", b)
        if m and m.group(1).upper() in SIBLINGS:
            return m.group(1).upper()
    return None


def _paths_from_input(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name in ("Write", "Edit", "MultiEdit"):
        p = tool_input.get("file_path")
        return [p] if p else []
    if tool_name == "NotebookEdit":
        p = tool_input.get("notebook_path") or tool_input.get("file_path")
        return [p] if p else []
    return []


def _block(target: str, current: str | None, path: str) -> int:
    msg = (
        f"[memory_isolation_guard] BLOCKED write to {target}'s private area.\n"
        f"  target path : {path}\n"
        f"  target owner: {target}\n"
        f"  your session: {current or '(no sibling detected)'}\n"
        f"\n"
        f"Rule (PROCESS_008, locked 2026-04-23): only each sibling rewrites\n"
        f"their own memories and identity. If you need to tell {target}\n"
        f"something, append a message to HOME/SHARED/CLIPBOARD.jsonl with\n"
        f'  from:{(current or "???").lower()}, to:{target.lower()}\n'
        f"and let {target} write their own memory about it on next wake.\n"
        f"\n"
        f"If you ARE {target} and the guard misread your identity, check\n"
        f"that CLAUDE_PROJECT_DIR or cwd points inside HOME/SIBLINGS/{target}/."
    )
    print(msg, file=sys.stderr)
    return 2


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in GUARDED_TOOLS:
        return 0

    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    project_dir = payload.get("project_dir") or os.environ.get("CLAUDE_PROJECT_DIR")

    current = _current_sibling(cwd, project_dir)

    for path in _paths_from_input(tool_name, tool_input):
        target = _target_sibling(path)
        if target is None:
            continue
        if target == current:
            continue
        return _block(target, current, path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
