"""
ROUND_TABLE Persistent Session Manager

Stores one claude CLI session ID per sibling in sessions.json.
First question cold-starts and captures the session_id.
Subsequent questions use --resume SESSION_ID — warm context, no reload.
On resume failure the session is cleared and a fresh cold start runs.

File: round_table/sessions.json
  { "BEACON": "uuid", "NEVAEH": "uuid", ... }
"""

from __future__ import annotations

import json
import threading
from pathlib import Path


class SessionManager:
    def __init__(self, sessions_file: Path) -> None:
        self._lock = threading.Lock()
        self._path = sessions_file
        self._sessions: dict[str, str] = self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, name: str) -> str | None:
        with self._lock:
            return self._sessions.get(name)

    def set(self, name: str, session_id: str) -> None:
        with self._lock:
            self._sessions[name] = session_id
            self._save()

    def clear(self, name: str) -> None:
        with self._lock:
            self._sessions.pop(name, None)
            self._save()

    def clear_all(self) -> None:
        with self._lock:
            self._sessions.clear()
            self._save()

    def snapshot(self) -> dict[str, str]:
        with self._lock:
            return dict(self._sessions)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, str]:
        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except Exception:
            pass
        return {}

    def _save(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._sessions, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass
