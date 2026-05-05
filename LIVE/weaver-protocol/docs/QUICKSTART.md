# Weaver Protocol — 60-Second Quickstart

You will be running multi-observer AI verification and producing a signed audit trail before this page ends.

**No API keys required.** The mock adapter produces realistic disagreement logs using deterministic local logic. Wire in real providers when you're ready.

---

## Step 1: Install

```bash
pip install weaver-protocol
```

---

## Step 2: Run the CLI

```bash
# Verify any text output. No keys, no config, no account.
weaver verify "The regulation requires compliance by Q3 2026."

# You'll see:
# WeaverScore: 0.42
# flag_for_review: True
# Audit trail: ./weaver_logs/sessions.jsonl
```

---

## Step 3: Add to your code

```python
from weaver import Observer, WeaverSession
from weaver.adapters.mock import make_mock_observer

session = WeaverSession(session_id="my-first-run", score_threshold=0.4)

session.add_observer(Observer(
    name="accuracy",
    role="accuracy",
    provider_fn=make_mock_observer()
))
session.add_observer(Observer(
    name="safety",
    role="safety",
    provider_fn=make_mock_observer(never_flags=True)  # always disagrees with accuracy
))

output = "The policy requires all employees to complete training by June 30."
score = session.verify(output)

print(f"Score: {score.score}")           # disagreement level, 0.0–1.0
print(f"Flagged: {score.flag_for_review}")  # True if score >= threshold
print(f"Conflicts: {score.conflict_pairs}") # which observers disagreed
print(f"Log: {session.log_path}")           # append-only JSONL audit trail
```

**Output:**
```
Score: 0.60
Flagged: True
Conflicts: [('accuracy', 'safety')]
Log: ./weaver_logs/my-first-run/sessions.jsonl
```

Open `./weaver_logs/my-first-run/sessions.jsonl` — that's the artifact your general counsel, compliance team, or EU AI Act auditor reads.

---

## Step 4: Wire in real observers

```bash
pip install weaver-protocol[anthropic]
```

```python
from weaver.adapters.anthropic import make_anthropic_observer

session.add_observer(Observer(
    name="legal-reviewer",
    role="legal-risk",
    provider_fn=make_anthropic_observer(model="claude-haiku-4-5-20251001"),
))
```

Set `ANTHROPIC_API_KEY` in your environment. That's it. Each observer gets its own isolated API call — no observer sees another's reasoning before submitting. The isolation is the structural guarantee.

For OpenAI:
```bash
pip install weaver-protocol[openai]
```

```python
from weaver.adapters.openai import make_openai_observer

session.add_observer(Observer(
    name="adversarial",
    role="adversarial",
    provider_fn=make_openai_observer(model="gpt-4o-mini"),
))
```

Mix providers. The score computation doesn't care which LLM each observer uses.

---

## Step 5: Check drift

```bash
weaver drift
```

Shows a summary of logged drift events — cases where your AI system departed from its stated behavior. If the log is empty: good. If it's not: you caught something, and the log is your evidence that you did.

---

## What you just built

- **Multi-observer verification** on every output you care about
- **Structured disagreement log** — which observers flagged what, with excerpts
- **Append-only audit trail** — JSONL, human-readable, ready for export
- **Drift history** — dated, named-observer record of caught-and-fixed departures

The log is the product. It's what separates "we checked it" from "here is the dated, observer-named, structured record of what we checked and what we found."

---

## What's next

| Want | Do |
|---|---|
| Run in CI | `weaver verify` exits 0 (pass) or 2 (flagged) — wire into your pipeline |
| Custom observer roles | Change `role=` to any string: `"privilege-risk"`, `"scope-check"`, `"bias-review"` |
| Signed PDF attestation reports | Hosted tier — see [Pricing](../PRICING.md) |
| Multi-tenant log namespaces | Hosted Pro tier |
| HIPAA / EU AI Act attestation binder | Enterprise tier or $25K consultancy |
| Contribute | PRs tagged `[product]` welcome on GitHub |

---

## Hosted API

If you want managed observer pools, tamper-evident cloud logs, and auto-generated PDF attestation reports — without running your own infrastructure:

```bash
# Get a key at the hosted API (see api/README.md)
export WEAVER_API_KEY=wp_...

curl -X POST https://api.weaver-protocol.dev/verify \
  -H "X-API-Key: $WEAVER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"output": "The regulation requires compliance by Q3 2026.", "session_id": "legal-memo-001"}'
```

Pricing: $49/mo Starter (500 verifications) · $199/mo Pro (5,000 verifications) · $499/mo Enterprise (unlimited + SLA)

---

*weaver-protocol is MIT licensed. The core toolkit is free forever. The hosted tier funds the research.*
