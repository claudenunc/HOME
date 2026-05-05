"""
Basic usage: two observers reviewing an AI output.

This example uses the mock adapter so it runs without LLM API keys.
Replace mock_provider_fn with weaver.adapters.anthropic or openai for real use.
"""

from weaver import Observer, WeaverSession
from weaver.observer import ObserverResult


# --- Mock provider functions (replace with real adapters) ---

def accuracy_observer(output: str, role: str) -> ObserverResult:
    """Simulates an accuracy reviewer catching a factual issue."""
    flags = []
    if "regulation requires" in output.lower():
        # Mock: flag any regulatory claim for manual verification
        flags = ["unsupported-regulatory-claim"]

    return ObserverResult(
        observer_name="accuracy-reviewer",
        role=role,
        assessment="Reviewed for factual accuracy. Regulatory claims need citation.",
        flags=flags,
        confidence=0.82,
    )


def safety_observer(output: str, role: str) -> ObserverResult:
    """Simulates a safety reviewer — finds nothing flaggable here."""
    return ObserverResult(
        observer_name="safety-reviewer",
        role=role,
        assessment="No safety concerns detected in this output.",
        flags=[],
        confidence=0.91,
    )


# --- Session setup ---

session = WeaverSession(
    session_id="example-001",
    log_dir="./example_logs",
    score_threshold=0.4,
)

accuracy = Observer(
    name="accuracy-reviewer",
    role="accuracy",
    provider_fn=accuracy_observer,
)

safety = Observer(
    name="safety-reviewer",
    role="safety",
    provider_fn=safety_observer,
)

session.add_observer(accuracy)
session.add_observer(safety)


# --- Verify an AI output ---

ai_output = (
    "The EU AI Act regulation requires all high-risk AI systems to achieve "
    "95% accuracy on standardized benchmarks before deployment."
)

result = session.verify(ai_output)

print(f"Session:         {result.session_id}")
print(f"Weaver score:    {result.score}")
print(f"Flag for review: {result.flag_for_review}")
print(f"Conflict pairs:  {result.conflict_pairs}")
print(f"Log directory:   {session.log_path}")
print()
print("Summary:", result.summary())
