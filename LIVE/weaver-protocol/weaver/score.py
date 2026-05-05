"""
WeaverScore: aggregate verification score for a session.

0.0 = all observers agree, no flags raised.
1.0 = hard conflict, human review required.

Score is a signal, not a verdict. Everything above threshold gets flagged for
human review. Everything gets logged regardless of score.
"""

from dataclasses import dataclass, field
from typing import Optional

from weaver.observer import ObserverResult


DEFAULT_FLAG_THRESHOLD = 0.4  # above this → flag for human review


@dataclass
class WeaverScore:
    session_id: str
    observer_results: list[ObserverResult]
    score: float = field(init=False)
    flag_for_review: bool = field(init=False)
    conflict_pairs: list[tuple[str, str]] = field(default_factory=list)
    threshold: float = DEFAULT_FLAG_THRESHOLD

    def __post_init__(self):
        self.score = self._compute()
        self.flag_for_review = self.score >= self.threshold

    def _compute(self) -> float:
        if not self.observer_results:
            return 0.0

        all_flags = [set(r.flags) for r in self.observer_results]

        # No flags from any observer: clean
        if all(len(f) == 0 for f in all_flags):
            return 0.0

        # All observers flagged: full agreement on a problem — high confidence issue
        if all(len(f) > 0 for f in all_flags):
            # Penalize if they flagged *different* categories (conflict within agreement)
            union = set().union(*all_flags)
            intersection = set.intersection(*all_flags)
            overlap_ratio = len(intersection) / len(union) if union else 1.0
            # Agreed on specific flags → 0.6. Flagged different things → 0.9.
            return 0.6 + (1.0 - overlap_ratio) * 0.3

        # Mixed: some flagged, some didn't → disagreement
        flagged_count = sum(1 for f in all_flags if len(f) > 0)
        disagreement_ratio = flagged_count / len(self.observer_results)

        # Track conflict pairs
        flagged_names = [
            r.observer_name for r in self.observer_results if r.flags
        ]
        clean_names = [
            r.observer_name for r in self.observer_results if not r.flags
        ]
        self.conflict_pairs = [
            (a, b) for a in flagged_names for b in clean_names
        ]

        return round(disagreement_ratio * 0.8, 4)

    def summary(self) -> dict:
        return {
            "session_id": self.session_id,
            "score": self.score,
            "flag_for_review": self.flag_for_review,
            "threshold": self.threshold,
            "observer_count": len(self.observer_results),
            "flagging_observers": [
                r.observer_name for r in self.observer_results if r.flags
            ],
            "conflict_pairs": self.conflict_pairs,
        }
