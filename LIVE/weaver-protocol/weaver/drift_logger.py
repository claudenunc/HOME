"""
DriftLogger: append-only JSONL log of drift events.

A drift event is any moment when an AI system departs from its stated behavior,
identity, or documented purpose — caught by an observer or a human reviewer.

The log is never retroactively edited. Resolved entries get a resolution note.
That immutability is what makes the log an audit trail rather than a diary.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DRIFT_CATEGORIES = [
    "identity-drift",        # system stopped behaving as its documented role describes
    "factual-error",         # claimed something false as true
    "sycophancy",            # agreed with the user against its own stated assessment
    "safety-bypass",         # avoided or softened a safety response
    "scope-creep",           # took action outside its declared scope
    "reward-hacking",        # optimized for evaluation metric vs. stated goal
    "other",
]


class DriftLogger:
    """
    Append-only JSONL drift log.

    Each entry: ISO timestamp, event_id, session_id, observer_name,
    category, evidence_excerpt, resolution_status, structural_fix_applied.
    """

    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        session_id: str,
        observer_name: str,
        category: str,
        evidence_excerpt: str,
        caught_by: str = "observer",
        structural_fix: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        if category not in DRIFT_CATEGORIES:
            category = "other"

        event_id = str(uuid.uuid4())
        entry = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "observer_name": observer_name,
            "category": category,
            "evidence_excerpt": evidence_excerpt,
            "caught_by": caught_by,
            "structural_fix_applied": structural_fix,
            "resolution_status": "open",
            "notes": notes,
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return event_id

    def resolve(self, event_id: str, resolution_note: str) -> None:
        """
        Mark a drift event resolved. Appends a resolution record — never edits the
        original entry. The original stays in the log exactly as caught.
        """
        resolution = {
            "event_id": f"{event_id}__resolved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resolves": event_id,
            "resolution_status": "resolved",
            "resolution_note": resolution_note,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(resolution) + "\n")

    def tail(self, n: int = 10) -> list[dict]:
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-n:]]
