"""
DisagreementLogger: structured capture of observer conflicts.

A disagreement is when two observers flag the same output differently —
one flags it, one doesn't; or both flag it under incompatible categories.
Logged regardless of resolution. The log is the evidence.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from weaver.observer import ObserverResult


class DisagreementLogger:
    """
    Append-only JSONL log of inter-observer conflicts.
    """

    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        session_id: str,
        output_excerpt: str,
        observer_a: ObserverResult,
        observer_b: ObserverResult,
        conflict_summary: str,
        resolution: Optional[str] = None,
    ) -> str:
        event_id = str(uuid.uuid4())
        entry = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "output_excerpt": output_excerpt[:500],  # cap excerpt length
            "observer_a": {
                "name": observer_a.observer_name,
                "role": observer_a.role,
                "flags": observer_a.flags,
                "confidence": observer_a.confidence,
                "assessment_excerpt": observer_a.assessment[:200],
            },
            "observer_b": {
                "name": observer_b.observer_name,
                "role": observer_b.role,
                "flags": observer_b.flags,
                "confidence": observer_b.confidence,
                "assessment_excerpt": observer_b.assessment[:200],
            },
            "conflict_summary": conflict_summary,
            "resolution": resolution,
            "resolution_status": "resolved" if resolution else "open",
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return event_id

    def open_conflicts(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").strip().splitlines()
        return [
            json.loads(line) for line in lines
            if json.loads(line).get("resolution_status") == "open"
        ]
