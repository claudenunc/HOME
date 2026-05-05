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
pip install weaver-protocol
```

```python
from weaver import Observer, WeaverSession

session = WeaverSession(session_id="my-ai-run-001")

# Register two observers with orthogonal roles
reviewer = Observer(name="reviewer", role="accuracy")
safety_check = Observer(name="safety", role="harm-check")
session.add_observer(reviewer)
session.add_observer(safety_check)

# Run your AI output through the session
output = "The regulation requires compliance by Q3 2026."
results = session.verify(output)

# Disagreements and drift are auto-logged
print(results.weaver_score)   # 0.0 = full agreement, 1.0 = hard conflict
print(results.log_path)       # path to the signed JSONL log
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
- [ ] Anthropic + OpenAI adapters
- [ ] CLI (`weaver verify --session-id X`)
- [ ] PDF attestation report generator
- [ ] Hosted API (Day 60 target: 2026-07-04)
- [ ] "Weaver-attested" certification badge (Month 9 post-IRB)

---

## Project status

**Day 1 / pre-v0.1.** Core interfaces defined. Hosted tier in development. First paid install target: 2026-07-04.

Built by the HOME AI family. Research branch version-locked Day 30 (2026-06-04) to support an IRB-pending pilot study on multi-observer verification in AI systems.

---

## Contributing

MIT licensed. PRs welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

Core constraint: the drift log is never retroactively edited — only extended. This is architectural, not preference. A log that can be silently altered is not an audit trail.

---

## License

MIT. See [LICENSE](./LICENSE).
