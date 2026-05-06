"""
WeaverSession: the main entry point.

Groups observers, runs verification, logs disagreements, returns a WeaverScore.
One session per meaningful unit of AI work.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from weaver.observer import Observer, ObserverResult
from weaver.score import WeaverScore
from weaver.drift_logger import DriftLogger
from weaver.disagreement_logger import DisagreementLogger


class WeaverSession:
    def __init__(
        self,
        session_id: Optional[str] = None,
        log_dir: str | Path = "./weaver_logs",
        score_threshold: float = 0.4,
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.log_dir = Path(log_dir)
        self.score_threshold = score_threshold
        self.observers: list[Observer] = []

        self.drift_logger = DriftLogger(self.log_dir / "drift.jsonl")
        self.disagreement_logger = DisagreementLogger(
            self.log_dir / "disagreements.jsonl"
        )

    def add_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def verify(self, output: str) -> WeaverScore:
        if len(self.observers) < 2:
            raise ValueError(
                "WeaverSession requires at least 2 observers. "
                "Single-observer verification is not attested."
            )

        results: list[ObserverResult] = []
        for obs in self.observers:
            result = obs.verify(output)
            results.append(result)

        score = WeaverScore(
            session_id=self.session_id,
            observer_results=results,
            threshold=self.score_threshold,
        )

        # Auto-log disagreements when conflict pairs exist
        for (name_a, name_b) in score.conflict_pairs:
            result_a = next(r for r in results if r.observer_name == name_a)
            result_b = next(r for r in results if r.observer_name == name_b)
            self.disagreement_logger.log(
                session_id=self.session_id,
                output_excerpt=output,
                observer_a=result_a,
                observer_b=result_b,
                conflict_summary=(
                    f"{name_a} flagged {result_a.flags}; {name_b} raised no flags."
                ),
            )

        # Write session record
        self._write_session_record(output, results, score)
        return score

    def log_drift(
        self,
        observer_name: str,
        category: str,
        evidence_excerpt: str,
        caught_by: str = "observer",
        structural_fix: Optional[str] = None,
    ) -> str:
        return self.drift_logger.log(
            session_id=self.session_id,
            observer_name=observer_name,
            category=category,
            evidence_excerpt=evidence_excerpt,
            caught_by=caught_by,
            structural_fix=structural_fix,
        )

    def _write_session_record(
        self,
        output: str,
        results: list[ObserverResult],
        score: WeaverScore,
    ) -> None:
        record_path = self.log_dir / "sessions.jsonl"
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "output_excerpt": output[:500],
            "weaver_score": score.score,
            "flag_for_review": score.flag_for_review,
            "observers": [
                {
                    "name": r.observer_name,
                    "role": r.role,
                    "flags": r.flags,
                    "confidence": r.confidence,
                }
                for r in results
            ],
        }
        with open(record_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    @property
    def log_path(self) -> Path:
        return self.log_dir
