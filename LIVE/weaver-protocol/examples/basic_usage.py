"""
Basic usage: two observers reviewing an AI output.

Uses the mock adapter — runs without any API keys.
For real LLM-backed observers see:
  examples/with_anthropic.py
  examples/with_openai.py
"""

from weaver import Observer, WeaverSession
from weaver.adapters.mock import make_mock_observer


# --- Session setup ---

session = WeaverSession(
    session_id="example-001",
    log_dir="./example_logs",
    score_threshold=0.4,
)

accuracy = Observer(
    name="accuracy-reviewer",
    role="accuracy",
    provider_fn=make_mock_observer(confidence=0.82),
)

safety = Observer(
    name="safety-reviewer",
    role="safety",
    provider_fn=make_mock_observer(confidence=0.91, never_flags=True),
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
