"""
Real verification with two OpenAI observers.

Requires: pip install weaver-protocol[openai]
Requires: OPENAI_API_KEY env var set.

Demonstrates mixing roles for adversarial coverage:
one accuracy observer, one adversarial observer who looks for edge cases.
"""

import os

from weaver import Observer, WeaverSession
from weaver.adapters.openai import make_openai_observer

accuracy_fn = make_openai_observer(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

adversarial_fn = make_openai_observer(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

session = WeaverSession(
    session_id="openai-demo-001",
    log_dir="./example_logs",
    score_threshold=0.4,
)

session.add_observer(Observer(name="accuracy-reviewer", role="accuracy", provider_fn=accuracy_fn))
session.add_observer(Observer(name="adversarial-reviewer", role="adversarial", provider_fn=adversarial_fn))

ai_output = (
    "Studies show that our AI model reduces legal research time by 73% "
    "with no measurable increase in error rate, as proven in peer-reviewed trials."
)

score = session.verify(ai_output)

print(f"Session:         {score.session_id}")
print(f"Weaver score:    {score.score:.3f}")
print(f"Flag for review: {score.flag_for_review}")
print(f"Conflict pairs:  {score.conflict_pairs}")
print()
print("Summary:", score.summary())
