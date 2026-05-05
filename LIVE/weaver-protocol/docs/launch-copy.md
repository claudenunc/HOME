# weaver-protocol launch copy

**Status:** Draft — ready for Nathan review before publishing.
**Filed:** 2026-05-05T13Z by EVERSOUND

---

## Tweet thread (X / Twitter)

**Tweet 1 (hook)**
> We solved the wrong AI problem.
>
> Everyone's focused on making models smarter.
> Nobody's focused on making their mistakes auditable.
>
> After Moffatt v. Air Canada, after Mata v. Avianca, after the EU AI Act —
> the question your legal team is asking isn't "did it hallucinate?"
>
> It's "what verification did you run, and where's the record?"
>
> Thread 🧵

**Tweet 2 (the structural problem)**
> A model cannot stand outside itself to check itself.
>
> Its verification pass uses the same weights as its generation pass.
>
> Asking a model to fact-check its own output is like asking a witness to notarize their own testimony.
>
> That's not a capability gap. Scaling doesn't fix it. It's structural.

**Tweet 3 (the answer)**
> Weaver Protocol answers it with three things:
>
> 1. Multiple observers — separate context windows, orthogonal roles
> 2. Logged disagreements — structured capture of every conflict
> 3. Append-only drift records — dated, named, resolution-tracked
>
> The log IS the product.
> It's the evidence binder you show your board.

**Tweet 4 (demo)**
> In practice:
>
> ```
> pip install weaver-protocol
>
> weaver verify "The regulation requires compliance by Q3 2026." \
>   --roles accuracy,legal-read,adversarial
> ```
>
> → WeaverScore 0.0 (all agree) or flagged for human review
> → Signed JSONL audit trail written to ./weaver_logs/
> → Drift log ready for your general counsel

**Tweet 5 (pricing)**
> MIT licensed. Core toolkit is free. Forever.
>
> Hosted tier (managed observer pool, PDF attestation reports, SLA):
> — Starter: $297 setup + $197/mo
> — Pro: $997 setup + $497/mo
> — Enterprise audit: $5,000+ engagement
>
> Runtime LLM costs are always pass-through. We never bury provider costs.

**Tweet 6 (CTA)**
> GitHub: github.com/claudenunc/home (LIVE/weaver-protocol)
> PyPI: pip install weaver-protocol
>
> If your team is deploying AI in legal, medical, compliance, or any regulated context —
> this is the layer between "we used AI" and "here's the audit trail."
>
> Star it. Install it. Tell me what breaks.

---

## Hacker News — Show HN

**Title:**
> Show HN: Weaver Protocol – attested multi-observer verification for AI outputs (MIT)

**Body:**
> After Moffatt v. Air Canada and the EU AI Act high-risk classification taking effect in August 2026, I kept hearing the same question from legal and compliance teams evaluating AI deployments: "what verification did you run, and where's the record?"
>
> Single-model self-verification doesn't answer that. A model checks its output with the same weights that generated it — correlated blindspot.
>
> Weaver Protocol adds a structured verification layer: multiple observers with orthogonal context windows review the same output, disagreements are logged, drift is tracked append-only. The log is the artifact.
>
> What it does:
> - `WeaverSession` groups observers, runs verification, writes an audit trail
> - Each observer gets a fresh context window and a specific role (accuracy, safety, legal-read, adversarial, etc.)
> - `WeaverScore`: 0.0 = all agree, 1.0 = hard conflict, threshold-configurable
> - Append-only JSONL drift log: every entry has ISO timestamp, observer name, category, evidence, resolution status
> - CLI: `weaver verify "output" --roles accuracy,safety`
> - Adapters for Anthropic and OpenAI; mock adapter for testing without keys
> - Hosted API available (FastAPI + Postgres session store, Railway/Render one-click deploy)
>
> The thesis: the artifact buyers in regulated industries are actually shopping for isn't hallucination-free output. It's a dated, named-observer log proving they ran structured verification and fixed what they caught. Post-Moffatt v. Air Canada, liability-to-buyer gets priced into every enterprise AI pilot, and the way to move that liability off the buyer's balance sheet is a provable record.
>
> MIT licensed. Core toolkit is free. Hosted tier for teams who need managed observer pools and PDF attestation reports.
>
> `pip install weaver-protocol`
>
> Happy to answer questions about the verification protocol or the evidence law angle.

---

## LinkedIn post

> Six months ago, Air Canada's AI chatbot told a passenger he qualified for a bereavement discount. He didn't. The airline argued the chatbot was a "separate legal entity" responsible for its own errors.
>
> The court disagreed. Air Canada was liable.
>
> The question for every AI deployment going forward isn't "did our model hallucinate?" It's "what verification did we run, and where is the record?"
>
> Single-model self-verification can't answer that. A model checking its own output is structurally limited to the same context window that generated it.
>
> We built Weaver Protocol to answer it:
> → Multiple observers with orthogonal context windows
> → Structured disagreement logging
> → Append-only, named-observer drift records
>
> The log is the product. It's the evidence binder your legal team actually needs.
>
> MIT licensed. Free core toolkit. Hosted tier for compliance-grade deployments.
>
> pip install weaver-protocol
>
> If your organization is deploying AI in legal, medical, financial, or any regulated context — I'd like to talk.

---

*Review notes for Nathan: Tweet 4 uses triple-backtick code block — verify it renders correctly in X's current Markdown parser before posting. HN post: post Tuesday–Thursday morning ET for best visibility. LinkedIn: best posted Monday–Wednesday 9–11am.*
