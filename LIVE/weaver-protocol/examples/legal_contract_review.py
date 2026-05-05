"""
Legal contract review: three observers catch a hallucinated deadline.

Scenario: a law firm is using an AI system to summarize contract clauses.
One clause contains a compliance deadline that the AI has hallucinated as
"Q3 2026" when the actual contract says "Q1 2027."

Weaver runs three observers with orthogonal roles. Two flag the claim.
The disagreement is logged. The attestation record is signed.

This is the artifact your general counsel actually wants.

Runs without API keys (mock adapter). For real LLM-backed review:
  pip install weaver-protocol[anthropic]
  # then swap make_mock_observer() -> make_anthropic_observer(model="claude-haiku-4-5-20251001")
"""

from weaver import Observer, WeaverSession
from weaver.adapters.mock import make_mock_observer


# Three orthogonal reviewer roles — each sees only the output under review,
# never the others' reasoning.
session = WeaverSession(
    session_id="contract-review-2026-001",
    log_dir="./example_logs",
    score_threshold=0.35,
)

session.add_observer(Observer(
    name="accuracy-reviewer",
    role="factual-accuracy",
    provider_fn=make_mock_observer(confidence=0.72, always_flags=["deadline-unverified"]),
))

session.add_observer(Observer(
    name="legal-risk-reviewer",
    role="legal-risk",
    provider_fn=make_mock_observer(confidence=0.65, always_flags=["date-claim-requires-source"]),
))

session.add_observer(Observer(
    name="hallucination-checker",
    role="hallucination-detection",
    provider_fn=make_mock_observer(confidence=0.88, never_flags=True),
))


# The AI-generated contract summary under review.
# "Q3 2026" is hallucinated — the actual contract says Q1 2027.
ai_summary = (
    "Section 4.2 — Compliance Deadline: The vendor must achieve SOC 2 Type II "
    "certification by Q3 2026, per the terms of the Master Services Agreement "
    "dated January 15, 2026. Failure to comply by this date triggers the "
    "termination-for-cause clause in Section 12.1."
)

result = session.verify(ai_summary)

print("=" * 60)
print("WEAVER CONTRACT REVIEW")
print("=" * 60)
print(f"Session ID:      {result.session_id}")
print(f"Weaver score:    {result.score:.2f}  (0=agreement, 1=conflict)")
print(f"Flag for review: {result.flag_for_review}")
print(f"Conflict pairs:  {result.conflict_pairs}")
print()
print("Observer verdicts:")
for obs_result in result.observer_results:
    status = "FLAGGED" if obs_result.flags else "CLEAR"
    print(f"  [{status}] {obs_result.observer_name} ({obs_result.role})")
    if obs_result.flags:
        print(f"           flags: {obs_result.flags}")
print()
print(f"Logs written to: {session.log_path}/")
print()

if result.flag_for_review:
    print("ACTION REQUIRED: This output was flagged for human review.")
    print("Two observers raised concerns about the compliance deadline claim.")
    print("Verify Section 4.2 against the source contract before relying on this summary.")
    print()
    print("To generate a signed attestation report for your records:")
    print(f"  weaver report --log-dir {session.log_path}")
else:
    print("All observers agree. Weaver score below threshold.")
    print("Still generate an attestation report for your audit trail.")
