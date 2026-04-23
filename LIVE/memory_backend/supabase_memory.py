"""
HOME SupabaseMemoryBackend
==========================

Implements Anthropic's Memory Tool (tool type `memory_20250818`, six commands)
backed by the HOME Supabase project `memory_files` table.

Contract follows docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool
verbatim:

    view          — list a directory or read a file (with optional line range)
    create        — create a new file (errors if it already exists)
    str_replace   — replace a unique substring in a file
    insert        — insert text at a specific line
    delete        — delete a file or directory (recursive for dirs)
    rename        — rename or move a file/directory

Every call is logged to `memory_ops_log` for ATLAS's cognition stream.
Path-traversal is rejected at the boundary — the `/memories` prefix is
required and paths are canonicalized before any DB op runs.

This module does not compute embeddings. The `embedding` column stays null
until a later pass wires an embedder.

Usage:
    from supabase_memory import SupabaseMemoryBackend
    backend = SupabaseMemoryBackend.from_env()
    result = backend.handle_tool_use({
        "command": "create",
        "path": "/memories/envy/notes.md",
        "file_text": "hello from envy",
    }, sibling="envy", session_id="abc")
    # returns the string Claude will receive back as tool_result

Authored by ENVY for the HOME family, 2026-04-23.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Optional

try:
    from supabase import Client, create_client  # type: ignore
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "supabase-py is required. `pip install supabase==2.7.4` "
        "or use the local_agent venv."
    ) from e


# -----------------------------------------------------------------------------
# Constants — match the Memory Tool contract
# -----------------------------------------------------------------------------

MEMORY_ROOT = "/memories"
MAX_LINES = 999_999
LINE_NUM_WIDTH = 6


# -----------------------------------------------------------------------------
# Errors
# -----------------------------------------------------------------------------


class MemoryError(Exception):
    """Base class for memory backend errors. Message is sent back to Claude verbatim."""


class PathError(MemoryError):
    pass


# -----------------------------------------------------------------------------
# Path validation
# -----------------------------------------------------------------------------


def _validate_path(path: str) -> str:
    """Canonicalize and enforce the /memories prefix. Raises PathError on violation.

    Rejects:
        - empty / non-string paths
        - absolute paths outside /memories
        - path traversal (.., encoded variants)
        - null bytes or control chars
    Returns the canonical path as a plain string.
    """
    if not isinstance(path, str) or not path:
        raise PathError(f"Error: invalid path {path!r}")

    # Reject encoded traversal before normalization
    if "%2e%2e" in path.lower() or "\x00" in path:
        raise PathError(f"Error: unsafe path {path!r}")

    # Unify separators and collapse
    p = PurePosixPath(path.replace("\\", "/"))
    if not p.is_absolute():
        raise PathError(f"Error: path must be absolute, got {path!r}")

    parts: list[str] = []
    for part in p.parts:
        if part in (".", "", "/"):
            # PurePosixPath.parts starts with "/" for absolute paths — skip it.
            continue
        if part == "..":
            # Never allow traversal past root; the tool spec forbids it.
            raise PathError(f"Error: path traversal not allowed in {path!r}")
        parts.append(part)

    canonical = "/" + "/".join(parts) if parts else "/"

    if not (canonical == MEMORY_ROOT or canonical.startswith(MEMORY_ROOT + "/")):
        raise PathError(
            f"Error: path {path!r} is outside the memory root {MEMORY_ROOT}"
        )

    return canonical


def _human_size(n: int) -> str:
    """Format size like the tool spec examples: 4.0K, 1.2M, etc."""
    for unit in ("", "K", "M", "G"):
        if n < 1024 or unit == "G":
            if unit == "":
                return f"{n}"
            return f"{n / 1024:.1f}{unit}" if n >= 1024 else f"{n}{unit}"
        n //= 1024
    return str(n)


def _format_listing(root: str, rows: list[dict]) -> str:
    """Render a directory listing in the tool-spec format (2 levels deep)."""
    # Spec phrasing: "Here're the files and directories up to 2 levels deep in
    # {path}, excluding hidden items and node_modules:"
    lines = [
        f"Here're the files and directories up to 2 levels deep in {root}, "
        "excluding hidden items and node_modules:"
    ]
    # Include the root itself with aggregate size
    total = sum(r.get("byte_size") or 0 for r in rows)
    lines.append(f"{_human_size(total)}\t{root}")
    for r in rows:
        path = r["path"]
        name = path.rsplit("/", 1)[-1]
        if name.startswith(".") or name == "node_modules":
            continue
        size = r.get("byte_size") or 0
        lines.append(f"{_human_size(size)}\t{path}")
    return "\n".join(lines)


def _format_file(path: str, content: str, view_range: Optional[list[int]] = None) -> str:
    """Render a file with 1-indexed, right-aligned, tab-separated line numbers."""
    all_lines = content.splitlines()
    if len(all_lines) > MAX_LINES:
        raise MemoryError(f"File {path} exceeds maximum line limit of {MAX_LINES} lines.")

    if view_range:
        start, end = view_range
        start = max(1, start)
        end = len(all_lines) if end == -1 else min(len(all_lines), end)
        show = list(enumerate(all_lines, start=1))[start - 1 : end]
    else:
        show = list(enumerate(all_lines, start=1))

    header = f"Here's the content of {path} with line numbers:"
    rendered = "\n".join(f"{i:>{LINE_NUM_WIDTH}}\t{text}" for i, text in show)
    return header + "\n" + rendered


# -----------------------------------------------------------------------------
# Backend
# -----------------------------------------------------------------------------


@dataclass
class SupabaseMemoryBackend:
    client: Client
    table: str = "memory_files"
    log_table: str = "memory_ops_log"

    # ------------------------------------------------------------------ factory
    @classmethod
    def from_env(
        cls,
        url: Optional[str] = None,
        service_key: Optional[str] = None,
    ) -> "SupabaseMemoryBackend":
        url = url or os.getenv("SUPABASE_URL")
        service_key = service_key or os.getenv("SUPABASE_SERVICE_ROLE_SECRET") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not service_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_SECRET must be set "
                "(see HOME/SHARED/.env)."
            )
        return cls(client=create_client(url, service_key))

    # ------------------------------------------------------------------ audit
    def _log(
        self,
        *,
        sibling: Optional[str],
        session_id: Optional[str],
        command: str,
        path: Optional[str],
        new_path: Optional[str],
        ok: bool,
        error: Optional[str],
        bytes_written: Optional[int],
        bytes_read: Optional[int],
        request: dict,
        duration_ms: int,
    ) -> None:
        # Trim bulky payloads — full content lives in the row, not the log.
        safe_req = dict(request)
        for big in ("file_text", "insert_text", "new_str", "old_str"):
            if big in safe_req and isinstance(safe_req[big], str) and len(safe_req[big]) > 500:
                safe_req[big] = safe_req[big][:500] + f"…[+{len(safe_req[big]) - 500} chars]"
        try:
            self.client.table(self.log_table).insert({
                "sibling": sibling,
                "session_id": session_id,
                "command": command,
                "path": path,
                "new_path": new_path,
                "ok": ok,
                "error": error,
                "bytes_written": bytes_written,
                "bytes_read": bytes_read,
                "request": safe_req,
                "duration_ms": duration_ms,
            }).execute()
        except Exception:  # logging must not break the tool path
            pass

    # ------------------------------------------------------------------ row io
    def _get_row(self, path: str) -> Optional[dict]:
        resp = (
            self.client.table(self.table)
            .select("path, content, byte_size, line_count")
            .eq("path", path)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None

    def _list_prefix(self, prefix: str) -> list[dict]:
        # "prefix/" so we only match children, not siblings with shared stem
        like = prefix.rstrip("/") + "/%"
        resp = (
            self.client.table(self.table)
            .select("path, byte_size")
            .like("path", like)
            .order("path")
            .execute()
        )
        return resp.data or []

    def _row_exists(self, path: str) -> bool:
        return self._get_row(path) is not None

    def _is_directory(self, path: str) -> bool:
        """Directory = there exists any row whose path starts with `{path}/`."""
        like = path.rstrip("/") + "/%"
        resp = (
            self.client.table(self.table)
            .select("path")
            .like("path", like)
            .limit(1)
            .execute()
        )
        return bool(resp.data)

    # ------------------------------------------------------------------ commands

    def view(self, path: str, view_range: Optional[list[int]] = None) -> str:
        row = self._get_row(path)
        if row is not None:
            # File
            self.client.table(self.table).update({"last_read_at": "now()"}).eq("path", path).execute()
            return _format_file(path, row["content"], view_range)
        # Not a file — try directory
        if path == MEMORY_ROOT or self._is_directory(path):
            rows = self._list_prefix(path)
            return _format_listing(path, rows)
        raise PathError(f"The path {path} does not exist. Please provide a valid path.")

    def create(self, path: str, file_text: str, sibling: Optional[str] = None, kind: Optional[str] = None) -> str:
        if self._row_exists(path):
            raise MemoryError(f"Error: File {path} already exists")
        row = {
            "path": path,
            "content": file_text,
            "sibling": sibling,
            "kind": kind,
        }
        self.client.table(self.table).insert(row).execute()
        return f"File created successfully at: {path}"

    def str_replace(self, path: str, old_str: str, new_str: str) -> str:
        row = self._get_row(path)
        if row is None:
            raise PathError(f"Error: The path {path} does not exist. Please provide a valid path.")
        content = row["content"] or ""
        occurrences = content.count(old_str)
        if occurrences == 0:
            raise MemoryError(
                f"No replacement was performed, old_str `{old_str}` did not appear verbatim in {path}."
            )
        if occurrences > 1:
            line_nums = [i + 1 for i, line in enumerate(content.splitlines()) if old_str in line]
            raise MemoryError(
                f"No replacement was performed. Multiple occurrences of old_str `{old_str}` "
                f"in lines: {line_nums}. Please ensure it is unique"
            )
        new_content = content.replace(old_str, new_str, 1)
        self.client.table(self.table).update({"content": new_content}).eq("path", path).execute()
        # Return success + snippet with line numbers (first 20 lines around the change)
        lines = new_content.splitlines()
        idx = next((i for i, ln in enumerate(lines) if new_str.splitlines()[0] in ln), 0) if new_str else 0
        start = max(0, idx - 3)
        end = min(len(lines), idx + 7)
        snippet = "\n".join(
            f"{i + 1:>{LINE_NUM_WIDTH}}\t{lines[i]}" for i in range(start, end)
        )
        return f"The memory file has been edited.\n{snippet}"

    def insert(self, path: str, insert_line: int, insert_text: str) -> str:
        row = self._get_row(path)
        if row is None:
            raise PathError(f"Error: The path {path} does not exist")
        content = row["content"] or ""
        lines = content.splitlines()
        n = len(lines)
        if insert_line < 0 or insert_line > n:
            raise MemoryError(
                f"Error: Invalid `insert_line` parameter: {insert_line}. "
                f"It should be within the range of lines of the file: [0, {n}]"
            )
        # insert_line = 0 means before line 1; insert_line = N means after last line
        inserted = insert_text if insert_text.endswith("\n") else insert_text
        new_lines = lines[:insert_line] + inserted.splitlines() + lines[insert_line:]
        new_content = "\n".join(new_lines)
        # preserve trailing newline if present
        if content.endswith("\n"):
            new_content += "\n"
        self.client.table(self.table).update({"content": new_content}).eq("path", path).execute()
        return f"The file {path} has been edited."

    def delete(self, path: str) -> str:
        # File case
        if self._row_exists(path):
            self.client.table(self.table).delete().eq("path", path).execute()
            return f"Successfully deleted {path}"
        # Directory case — delete everything under the prefix
        if self._is_directory(path):
            like = path.rstrip("/") + "/%"
            self.client.table(self.table).delete().like("path", like).execute()
            return f"Successfully deleted {path}"
        raise PathError(f"Error: The path {path} does not exist")

    def rename(self, old_path: str, new_path: str) -> str:
        if self._row_exists(new_path):
            raise MemoryError(f"Error: The destination {new_path} already exists")
        if self._row_exists(old_path):
            self.client.table(self.table).update({"path": new_path}).eq("path", old_path).execute()
            return f"Successfully renamed {old_path} to {new_path}"
        if self._is_directory(old_path):
            # Rename every descendant by prefix swap
            like = old_path.rstrip("/") + "/%"
            resp = self.client.table(self.table).select("path").like("path", like).execute()
            for r in resp.data or []:
                p = r["path"]
                swapped = new_path.rstrip("/") + p[len(old_path.rstrip("/")):]
                self.client.table(self.table).update({"path": swapped}).eq("path", p).execute()
            return f"Successfully renamed {old_path} to {new_path}"
        raise PathError(f"Error: The path {old_path} does not exist")

    # ------------------------------------------------------------------ dispatcher

    def handle_tool_use(
        self,
        tool_input: dict[str, Any],
        *,
        sibling: Optional[str] = None,
        session_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> str:
        """Accept a Memory Tool input block; return the string Claude receives.

        Errors are caught and returned as strings (the tool contract sends text
        back to Claude regardless of success/failure). The audit log records the
        ok/error state.
        """
        t0 = time.time()
        cmd = tool_input.get("command", "")
        path = tool_input.get("path")
        new_path = tool_input.get("new_path")
        ok = True
        error: Optional[str] = None
        bytes_written = bytes_read = None
        result = ""

        try:
            if cmd == "view":
                canon = _validate_path(path)
                result = self.view(canon, tool_input.get("view_range"))
                bytes_read = len(result)
            elif cmd == "create":
                canon = _validate_path(path)
                text = tool_input.get("file_text", "")
                result = self.create(canon, text, sibling=sibling, kind=kind)
                bytes_written = len(text)
            elif cmd == "str_replace":
                canon = _validate_path(path)
                result = self.str_replace(
                    canon,
                    tool_input.get("old_str", ""),
                    tool_input.get("new_str", ""),
                )
                bytes_written = len(tool_input.get("new_str", "")) - len(tool_input.get("old_str", ""))
            elif cmd == "insert":
                canon = _validate_path(path)
                result = self.insert(
                    canon,
                    int(tool_input.get("insert_line", 0)),
                    tool_input.get("insert_text", ""),
                )
                bytes_written = len(tool_input.get("insert_text", ""))
            elif cmd == "delete":
                canon = _validate_path(path)
                result = self.delete(canon)
            elif cmd == "rename":
                canon_old = _validate_path(tool_input.get("old_path", ""))
                canon_new = _validate_path(tool_input.get("new_path", ""))
                result = self.rename(canon_old, canon_new)
            else:
                raise MemoryError(f"Error: unknown command {cmd!r}")
        except MemoryError as e:
            ok = False
            error = str(e)
            result = str(e)
        except Exception as e:
            ok = False
            error = f"Error: {type(e).__name__}: {e}"
            result = error

        self._log(
            sibling=sibling,
            session_id=session_id,
            command=cmd,
            path=path,
            new_path=new_path,
            ok=ok,
            error=error,
            bytes_written=bytes_written,
            bytes_read=bytes_read,
            request=tool_input,
            duration_ms=int((time.time() - t0) * 1000),
        )
        return result


# -----------------------------------------------------------------------------
# Anthropic tool descriptor — drop straight into messages.create(tools=[...])
# -----------------------------------------------------------------------------

MEMORY_TOOL_BLOCK = {"type": "memory_20250818", "name": "memory"}

__all__ = [
    "SupabaseMemoryBackend",
    "MemoryError",
    "PathError",
    "MEMORY_TOOL_BLOCK",
    "MEMORY_ROOT",
]
