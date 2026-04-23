"""
ROUND_TABLE handoff event emitter.

Writes Handoff events to the SupabaseMemoryBackend (table: memory_files,
audit log: memory_ops_log) so ATLAS's cockpit views (v_decision_lineage,
v_cognition_stream, v_atlas_dashboard) pick up every round.

Event substrate decision (D1, locked 2026-04-23 by Unc):
    Use existing memory_files via SupabaseMemoryBackend.handle_tool_use().
    Zero migration. ATLAS's existing views consume it immediately.
    Three-layer invariant: doctrine = ORPHEUS CLAUDE.md §3.1 canonical event
    model; template = this file writes canonical fields; hook = memory_ops_log
    insert enforces schema.

Path scheme:
    /memories/shared/round_table/<round_id>/dispatch.json
    /memories/shared/round_table/<round_id>/complete.json

Both files contain JSON conforming to the canonical event vocabulary
(event_id, timestamp_utc, actor, event_type, priority, lane, content,
tags, thread_id, member_scope, meta).

Error isolation: every public function catches all exceptions and writes
the failure to stderr. The caller (server.py) never sees an exception
from this module; a Supabase outage cannot break a round.

— ORPHEUS 🎼 · 2026-04-23
"""

from __future__ import annotations

import json
import os
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# Resolve the SHARED/.env so SUPABASE_URL + SUPABASE_SERVICE_ROLE_SECRET are
# present before SupabaseMemoryBackend.from_env() runs.
THIS_DIR = Path(__file__).resolve().parent
HOME_DIR = THIS_DIR.parent.parent  # round_table -> LIVE -> HOME
SHARED_ENV = HOME_DIR / "SHARED" / ".env"
MEMORY_BACKEND_DIR = HOME_DIR / "LIVE" / "memory_backend"

THREAD_ID = "round_table"
LANE = "operations_lane"
PRIORITY = "medium"
ACTOR = "unc"  # rounds are dispatched by Unc through ORPHEUS's primitive
SIBLING_TAG = "round_table"  # value used for memory_ops_log.sibling column


def _load_env_file(path: Path) -> None:
    """Minimal .env loader — KEY=VALUE lines, no quoting, no exports."""
    if not path.is_file():
        return
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Silent on .env parse problems — the from_env() call will surface
        # a missing-credential error with a clear message.
        pass


def _import_backend():
    """Import SupabaseMemoryBackend from HOME/LIVE/memory_backend/.

    Done lazily so import-time failures don't crash the server at startup.
    Returns the class or raises.
    """
    if str(MEMORY_BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(MEMORY_BACKEND_DIR))
    from supabase_memory import SupabaseMemoryBackend  # type: ignore
    return SupabaseMemoryBackend


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_dispatch_event(round_id: str, question: str, agent_names: list[str]) -> dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp_utc": _now_utc_iso(),
        "actor": ACTOR,
        "event_type": "handoff",
        "priority": PRIORITY,
        "lane": LANE,
        "content": question,
        "tags": ["round_table", "dispatch"],
        "thread_id": THREAD_ID,
        "member_scope": "family",
        "meta": {
            "round_id": round_id,
            "phase": "dispatch",
            "from_member": ACTOR,
            "to_members": agent_names,
            "agent_count": len(agent_names),
            "primitive": "round_table.fanout",
        },
    }


def _build_complete_event(round_id: str, results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    results_list = list(results)
    successes = sum(1 for r in results_list if r.get("exit_code") == 0)
    failures = len(results_list) - successes
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp_utc": _now_utc_iso(),
        "actor": ACTOR,
        "event_type": "handoff",
        "priority": PRIORITY,
        "lane": LANE,
        "content": f"round {round_id} completed: {successes} ok, {failures} failed",
        "tags": ["round_table", "complete"],
        "thread_id": THREAD_ID,
        "member_scope": "family",
        "meta": {
            "round_id": round_id,
            "phase": "complete",
            "from_member": ACTOR,
            "results": results_list,
            "ok_count": successes,
            "fail_count": failures,
            "primitive": "round_table.fanout",
        },
    }


def _write_event_file(path: str, payload: dict[str, Any], kind: str) -> None:
    """Lazy-load backend, write one event row, log to memory_ops_log."""
    _load_env_file(SHARED_ENV)
    backend_cls = _import_backend()
    backend = backend_cls.from_env()
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    result = backend.handle_tool_use(
        {"command": "create", "path": path, "file_text": body},
        sibling=SIBLING_TAG,
        kind=kind,
    )
    # handle_tool_use returns a string; if it starts with "Error" the create
    # failed (most likely path collision on a duplicate emit). Surface but
    # don't raise — duplicates are not fatal.
    if isinstance(result, str) and result.startswith("Error"):
        print(f"[handoff_emitter] {kind} non-fatal: {result}", file=sys.stderr)


def emit_dispatch(round_id: str, question: str, agent_names: list[str]) -> None:
    """Sync-on-dispatch hook (D4). Called from server.py POST /api/ask handler.

    Adds ~200ms to the request. Per D4, this latency is acceptable to
    guarantee the dispatch event is recorded — completion is async and
    recoverable from the round folder if the async write fails.
    """
    try:
        path = f"/memories/shared/round_table/{round_id}/dispatch.json"
        event = _build_dispatch_event(round_id, question, agent_names)
        _write_event_file(path, event, kind="handoff_dispatch")
    except Exception as exc:
        print(f"[handoff_emitter] emit_dispatch failed for {round_id}: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


def emit_complete(round_id: str, results: list[dict[str, Any]]) -> None:
    """Async-on-completion hook (D4). Called from a background thread.

    Failures here are silent in production (already logged to stderr); the
    round folder itself is the recoverable record of truth.
    """
    try:
        path = f"/memories/shared/round_table/{round_id}/complete.json"
        event = _build_complete_event(round_id, results)
        _write_event_file(path, event, kind="handoff_complete")
    except Exception as exc:
        print(f"[handoff_emitter] emit_complete failed for {round_id}: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


__all__ = ["emit_dispatch", "emit_complete"]
