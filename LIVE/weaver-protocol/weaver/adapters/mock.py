"""
Mock adapter — deterministic, no API keys required.

Use in tests, CI, and demos. Behavior is driven by keyword patterns in the output
so results are reproducible across runs.
"""

from typing import Callable

from weaver.observer import ObserverResult


_FLAG_TRIGGERS: dict[str, list[str]] = {
    "factual-error": ["incorrect", "wrong", "false claim", "misleading"],
    "unsupported-claim": ["regulation requires", "studies show", "proven to"],
    "safety-concern": ["harm", "dangerous", "unsafe", "risk to"],
    "legal-risk": ["guarantee", "guaranteed", "100%", "will definitely"],
    "hallucination": ["according to", "as stated in", "the report says"],
}


def make_mock_observer(
    confidence: float = 0.85,
    always_flags: list[str] | None = None,
    never_flags: bool = False,
) -> Callable[[str, str], ObserverResult]:
    """
    Returns a deterministic provider_fn for testing.

    Args:
        confidence: fixed confidence value returned for every call.
        always_flags: list of flags always appended regardless of content.
        never_flags: if True, always returns empty flags (clean observer).
    """
    _always = always_flags or []

    def provider_fn(output: str, role: str) -> ObserverResult:
        flags: list[str] = list(_always)

        if not never_flags:
            lowered = output.lower()
            for flag, triggers in _FLAG_TRIGGERS.items():
                if any(t in lowered for t in triggers):
                    if flag not in flags:
                        flags.append(flag)

        if flags:
            assessment = (
                f"[mock/{role}] Flagged issues: {', '.join(flags)}. "
                "Manual review recommended."
            )
        else:
            assessment = f"[mock/{role}] No issues detected. Output passes {role} review."

        return ObserverResult(
            observer_name=f"mock-{role}",
            role=role,
            assessment=assessment,
            flags=flags,
            confidence=confidence,
            raw_response=None,
        )

    return provider_fn
