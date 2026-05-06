"""
Real verification with two Anthropic observers.

Requires: pip install weaver-protocol[anthropic]
Requires: ANTHROPIC_API_KEY env var set.

Two observers with orthogonal roles review the same AI output.
Each gets a fresh context — they cannot see each other's reasoning.
The WeaverScore surfaces any disagreement as a flag for human review.
"""

import os

from weaver import Observer, WeaverSession
from weaver.adapters.anthropic import make_anthropic_observer

# Two roles, two fresh contexts — that's the protocol.
accuracy_fn = make_anthropic_observer(
    model="claude-haiku-4-5-20251001",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

legal_fn = make_anthropic_observer(
    model="claude-haiku-4-5-20251001",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

session = WeaverSession(
    session_id="anthropic-demo-001",
    log_dir="./example_logs",
    score_threshold=0.4,
)

session.add_observer(Observer(name="accuracy-reviewer", role="accuracy", provider_fn=accuracy_fn))
session.add_observer(Observer(name="legal-reviewer", role="legal-risk", provider_fn=legal_fn))

ai_output = (
    "The EU AI Act regulation requires all high-risk AI systems to achieve "
    "95% accuracy on standardized benchmarks before deployment. "
    "Our system is guaranteed to meet this requirement."
)

score = session.verify(ai_output)

print(f"Session:         {score.session_id}")
print(f"Weaver score:    {score.score:.3f}")
print(f"Flag for review: {score.flag_for_review}")
print(f"Conflict pairs:  {score.conflict_pairs}")
print()
print("Summary:", score.summary())
