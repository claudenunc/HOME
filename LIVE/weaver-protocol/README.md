# weaver-protocol

**Attested multi-observer verification for AI systems.**

> *"We don't sell smarter AI. We sell AI whose mistakes you can invoice."*

Weaver is an open-source toolkit that adds a structured verification layer around AI outputs. Multiple observers — each with an orthogonal context window — review the same output. Disagreements are logged. Drift is caught. The record is signed and auditable.

The artifact your legal team actually wants isn't a hallucination-free model. It's a dated, named-observer log proving you ran structured verification and fixed what you caught.

---

## Why this exists

Post-*Moffatt v. Air Canada* (2024). Post-*Mata v. Avianca* (2023). Post-EU AI Act high-risk classification (August 2026). The liability question has shifted from **"did your AI hallucinate?"** to **"what verification did you run, when, and what did you find?"**

Single-model self-verification doesn't answer that question. A model cannot stand outside itself to check itself. It checks its output with the same forward pass that generated it.

Weaver answers it with three things:
1. **Multiple observers** — separate context windows, orthogonal review angles
2. **Logged disagreements** — structured capture of every conflict between observers
3. **Drift records** — dated, named-observer entries when a system departs from its stated behavior

The log IS the product. It's the evidence binder you show your board, your general counsel, or the EU AI Act auditor.

---

## Quick start

```bash
# Core (no API keys required for mock adapter)
pip install weaver-protocol

# With Anthropic observers
pip install weaver-protocol[anthropic]

# With OpenAI observers
pip install weaver-protocol[openai]
```

```python
from weaver import Observer, WeaverSession
from weaver.adapters.anthropic import make_anthropic_observer  # or openai, or mock

session = WeaverSession(session_id="my-ai-run-001", score_threshold=0.4)

# Two observers, orthogonal roles, separate context windows
session.add_observer(Observer(
    name="accuracy-reviewer",
    role="accuracy",
    provider_fn=make_anthropic_observer(model="claude-haiku-4-5-20251001"),
))
session.add_observer(Observer(
    name="legal-reviewer",
    role="legal-risk",
    provider_fn=make_anthropic_observer(model="claude-haiku-4-5-20251001"),
))

output = "The regulation requires compliance by Q3 2026."
score = session.verify(output)

# Disagreements and drift are auto-logged to ./weaver_logs/
print(score.score)           # 0.0 = full agreement, 1.0 = hard conflict
print(score.flag_for_review) # True if score >= threshold
print(score.conflict_pairs)  # which observers disagreed
print(session.log_path)      # path to the JSONL audit trail
```

**No API keys? Use the mock adapter:**

```python
from weaver.adapters.mock import make_mock_observer

session.add_observer(Observer(name="a", role="accuracy", provider_fn=make_mock_observer()))
session.add_observer(Observer(name="b", role="safety",   provider_fn=make_mock_observer(never_flags=True)))
```

---

## Core concepts

### Observer

An `Observer` wraps an AI call with a defined role and a fresh context window. Role is freeform but meaningful — `"accuracy"`, `"safety"`, `"legal-read"`, `"adversarial"`. Each observer sees only the output under review, not the other observers' reasoning.

### WeaverSession

A session groups observers, holds the shared output under review, runs verification, and writes the log. One session per meaningful unit of work — a document review, a chatbot response, a contract clause extraction.

### WeaverScore

A float from 0.0 (all observers agree) to 1.0 (hard conflict). Threshold-configurable. Above your threshold = human review flag. All scores are logged regardless.

### DriftLog

Append-only JSONL. Every entry: ISO timestamp, session ID, observer name, disagreement category, evidence excerpt, resolution status, structural fix. The log is the audit trail. Never delete entries — mark them `resolved` with a note.

---

## Installation

```bash
pip install weaver-protocol        # stable release
pip install weaver-protocol[dev]   # + dev tools (pytest, ruff, mypy)
```

Requires Python 3.11+. No mandatory LLM provider — bring your own (Anthropic, OpenAI, local). Provider adapters in `weaver/adapters/`.

---

## Pricing

Weaver is MIT-licensed. The core toolkit is free.

Hosted infrastructure, managed observer pools, and verification attestation documents are paid tiers.

| Tier | Price | What you get |
|---|---|---|
| **Open source** | Free | Full toolkit, local logging, bring your own LLM keys |
| **Hosted Starter** | $297 setup + $197/mo | Managed observer pool, cloud log storage, PDF attestation reports |
| **Hosted Pro** | $997 setup + $497/mo | Multi-tenant, API access, custom observer roles, SLA |
| **Enterprise / Audit** | $5,000+ engagement | Annual audit, certification artifacts, signed evidence binder, expert witness ready |

Runtime LLM costs are always pass-through to your keys. We never bury provider costs in our pricing.

Full pricing: [PRICING.md](./PRICING.md)

---

## Roadmap

- [x] Core observer + session interface
- [x] Drift logger (append-only JSONL)
- [x] Disagreement logger
- [x] Weaver score
- [x] Anthropic + OpenAI adapters (`weaver/adapters/`)
- [x] CLI (`weaver verify` / `weaver drift`)
- [x] Hosted API with Postgres session store
- [x] One-click Railway + Render deploy configs
- [ ] PDF attestation report generator
- [ ] "Weaver-attested" certification badge (Month 9 post-IRB)

---

## Project status

**v0.1.0.** Core toolkit + CLI shipped. Hosted API with Postgres session store live. Railway and Render deploy configs included — one `git push` away from a running verification service. First paid install target: 2026-07-04.

Built by the HOME AI family. Research branch version-locked Day 30 (2026-06-04) to support an IRB-pending pilot study on multi-observer verification in AI systems.

---

## Contributing

MIT licensed. PRs welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

Core constraint: the drift log is never retroactively edited — only extended. This is architectural, not preference. A log that can be silently altered is not an audit trail.

---

## License

MIT. See [LICENSE](./LICENSE).
