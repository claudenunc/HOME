# Contributing to weaver-protocol

Thank you for contributing. This document is short on purpose — the constraints that matter are architectural, not bureaucratic.

---

## The one non-negotiable

**The drift log is never retroactively edited — only extended.**

Every entry in `drift.jsonl` is append-only. You may add a `resolved` entry with a note. You may not delete or alter a past entry. A log that can be silently altered is not an audit trail. This is not preference — it is what makes the attestation artifact legally meaningful.

If you find code that allows deletion or silent overwrite of log entries, that is a bug and should be filed as one.

---

## Setup

```bash
git clone https://github.com/claudenunc/home
cd LIVE/weaver-protocol

pip install -e ".[dev]"
pytest tests/
```

All tests run without API keys. The mock adapter is always available.

---

## Making changes

1. Fork the repo, create a branch from `main`.
2. Run `pytest tests/` before opening a PR — all tests must pass.
3. If your change affects the observer interface, verification flow, or log schema: update `docs/PROTOCOL.md` to match.
4. If you catch a drift incident in your own changes, log it in `EVIDENCE/drift_log.md` before the PR lands — not after.

---

## What we want

- **Additional provider adapters** — Mistral, Groq, local (Ollama), Bedrock
- **Log export formats** — CSV, JSON-LD for legal workflows
- **Observer roles library** — pre-built roles for common verticals (legal, medical, finance)
- **PDF export** from `weaver report`
- **Test coverage** — currently 34 passing; gaps in edge cases welcome

---

## What we do not want

- Changes that make log entries mutable after the fact
- Adapters that suppress disagreements to "improve" the score
- Pricing changes (see PRICING.md — that's a product decision, not a PR)
- Breaking changes to the `WeaverSession` / `Observer` / `WeaverScore` interface without a major version bump

---

## Code style

- Python 3.11+, ruff for linting (`pip install ruff && ruff check .`)
- No mandatory dependencies for the core package — LLM providers are optional extras
- Type hints on all public interfaces

---

## Questions

Open an issue. We read them.
