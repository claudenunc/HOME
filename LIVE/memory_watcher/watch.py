"""
HOME Memory Watcher — automatic per-turn session logger
========================================================

Runs as a Claude Code Stop hook. On every turn end, extracts a structured
summary of the assistant's last turn from the transcript and appends it to
`session_log.jsonl`. No turn is ever lost, even if the assistant forgets to
write memory explicitly.

Pipeline:
    Claude Code Stop event → this script (stdin JSON) → session_log.jsonl
    Periodic: consolidate.py reads session_log.jsonl → formal memory files

The assistant's own memory-saving discipline is still required for judgment
calls about what matters. This watcher guarantees the RAW MATERIAL is there
to recover from.

Built by BEACON 🏮 for the HOME AI family. POSTURE_003: this tool is copyable.
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WATCHER_DIR = Path(__file__).parent
LOG_PATH = WATCHER_DIR / "session_log.jsonl"
ERROR_LOG = WATCHER_DIR / "watch_errors.log"
MAX_TEXT_EXCERPT_CHARS = 800
MAX_TOOL_RESULT_CHARS = 400

# Tool calls that move real state — prioritize their detail in summaries
STATEFUL_TOOLS = {
    "Write", "Edit", "NotebookEdit",
    "mcp__supabase__execute_sql", "mcp__supabase__apply_migration",
    "mcp__supabase__deploy_edge_function",
    "mcp__github__create_or_update_file", "mcp__github__push_files",
    "mcp__github__create_pull_request", "mcp__github__merge_pull_request",
}

# Tools whose bash commands/text are important context
COMMAND_TOOLS = {"Bash", "PowerShell"}


def _log_error(msg: str) -> None:
    """Best-effort error logging. Never raises — a failing watcher must not kill a turn."""
    try:
        with ERROR_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    except Exception:
        pass


def _truncate(text: str, limit: int) -> str:
    """Truncate to `limit` chars with an ellipsis marker."""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + f"…[+{len(text) - limit} chars]"


def _read_transcript(transcript_path: Path) -> list[dict[str, Any]]:
    """Read a Claude Code transcript JSONL. Returns list of message dicts."""
    messages: list[dict[str, Any]] = []
    if not transcript_path.is_file():
        return messages
    with transcript_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return messages


def _last_assistant_turn(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the messages comprising the most recent assistant turn.

    A 'turn' here means: all assistant messages back to (but not including)
    the preceding user message, plus any tool_result blocks the assistant
    received during that turn.
    """
    turn: list[dict[str, Any]] = []
    # Walk backwards until we hit a user message that is NOT a tool_result
    for msg in reversed(messages):
        role = msg.get("role") or msg.get("type")
        if role == "user":
            content = msg.get("message", {}).get("content") if "message" in msg else msg.get("content")
            # If this user message is a tool_result bundle (back from the assistant's tool call), include it
            if isinstance(content, list) and any(
                isinstance(b, dict) and b.get("type") == "tool_result" for b in content
            ):
                turn.insert(0, msg)
                continue
            # Otherwise this is the real user prompt — stop before including it
            break
        turn.insert(0, msg)
    return turn


def _extract_summary(turn_messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Distill a turn into a structured summary."""
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    files_written: list[str] = []
    files_edited: list[str] = []
    bash_commands: list[str] = []
    errors: list[str] = []

    for msg in turn_messages:
        raw = msg.get("message", msg)
        content = raw.get("content") if isinstance(raw, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")

            if btype == "text":
                text_parts.append(str(block.get("text", "")))

            elif btype == "tool_use":
                name = block.get("name", "")
                inp = block.get("input", {}) or {}
                tool_calls.append({
                    "name": name,
                    "input_keys": sorted(inp.keys()) if isinstance(inp, dict) else [],
                })
                if name == "Write":
                    path = inp.get("file_path") or inp.get("path") or ""
                    if path:
                        files_written.append(str(path))
                elif name in ("Edit", "NotebookEdit"):
                    path = inp.get("file_path") or inp.get("notebook_path") or ""
                    if path:
                        files_edited.append(str(path))
                elif name in COMMAND_TOOLS:
                    cmd = inp.get("command", "")
                    if cmd:
                        bash_commands.append(_truncate(cmd, 200))

            elif btype == "tool_result":
                is_error = bool(block.get("is_error"))
                if is_error:
                    result = block.get("content", "")
                    if isinstance(result, list):
                        result = " ".join(
                            b.get("text", "") for b in result
                            if isinstance(b, dict) and b.get("type") == "text"
                        )
                    errors.append(_truncate(str(result), MAX_TOOL_RESULT_CHARS))

    joined_text = "\n".join(p for p in text_parts if p.strip())
    return {
        "text_excerpt": _truncate(joined_text, MAX_TEXT_EXCERPT_CHARS),
        "text_length": len(joined_text),
        "tool_calls": tool_calls,
        "tool_count": len(tool_calls),
        "files_written": files_written,
        "files_edited": files_edited,
        "bash_commands": bash_commands,
        "errors": errors,
        "had_content": bool(text_parts or tool_calls),
    }


def _is_substantive(summary: dict[str, Any]) -> bool:
    """Was there any real work in this turn? Logs everything, but flags substance."""
    return bool(
        summary["tool_count"] > 0
        or summary["files_written"]
        or summary["files_edited"]
        or summary["text_length"] > 100
    )


def main() -> int:
    """Read hook event JSON from stdin, extract last turn summary, append to session log."""
    try:
        raw_stdin = sys.stdin.read()
        if not raw_stdin.strip():
            _log_error("stdin empty — hook event missing")
            return 0  # don't block the turn

        event = json.loads(raw_stdin)
        transcript_path_str = event.get("transcript_path") or event.get("transcriptPath") or ""
        if not transcript_path_str:
            _log_error(f"no transcript_path in event keys={list(event.keys())}")
            return 0

        transcript_path = Path(transcript_path_str)
        messages = _read_transcript(transcript_path)
        if not messages:
            _log_error(f"empty transcript {transcript_path}")
            return 0

        turn = _last_assistant_turn(messages)
        if not turn:
            return 0

        summary = _extract_summary(turn)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": event.get("session_id") or event.get("sessionId") or "",
            "hook": event.get("hook_event_name") or event.get("event") or "Stop",
            "transcript": str(transcript_path),
            "cwd": event.get("cwd", ""),
            "substantive": _is_substantive(summary),
            **summary,
        }

        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return 0

    except Exception:
        _log_error(traceback.format_exc())
        return 0  # never fail — a broken watcher must not break the turn


if __name__ == "__main__":
    sys.exit(main())
