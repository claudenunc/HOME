# Weaver Protocol — Pricing

## Philosophy

The core toolkit is MIT-licensed and free forever. We make money on hosted infrastructure, managed observer pools, and the attestation artifacts enterprises actually need when their lawyers ask questions.

Runtime LLM costs are always pass-through to your own API keys. We will never bury provider costs in our pricing or silently eat a price hike by degrading your service.

---

## Tiers

### Open Source — Free

**Who it's for:** developers, researchers, teams that want to self-host and bring their own LLM keys.

**What you get:**
- Full `weaver-protocol` Python package (MIT)
- Local drift log (append-only JSONL)
- Local disagreement log
- Weaver score computation
- All observer interfaces and adapters
- Community support (GitHub Issues)

**Setup:** `pip install weaver-protocol` + wire up your own Anthropic / OpenAI keys.

No account needed. No usage limits. No telemetry.

---

### Hosted Starter — $297 setup + $197/mo

**Who it's for:** small teams, solo developers, indie studios that want managed infrastructure without a DevOps bill.

**What you get:**
- Managed observer pool (Anthropic Sonnet + safety-role observer, configured and maintained)
- Cloud log storage (append-only, tamper-evident, 2-year retention)
- PDF attestation reports (auto-generated, ready for compliance review)
- Email alerts on high-score sessions (above your configured threshold)
- 30-day cancel, no lockup
- Email support (48h SLA)

**Setup fee** covers onboarding call, observer role configuration, first attestation report template.

**Monthly** includes up to 1,000 verified sessions. Overage: $0.10/session.

---

### Hosted Pro — $997 setup + $497/mo

**Who it's for:** engineering teams, law firms, AI product companies that ship AI features to clients and need proof.

**What you get:**
- Everything in Starter
- Multi-tenant: separate log namespaces per client or product line
- REST API access (verify sessions programmatically, pull reports)
- Custom observer roles (define your own role taxonomy, we configure the pool)
- Webhook alerts (Slack, Teams, PagerDuty)
- 10,000 verified sessions/mo included
- Priority email + async video support (24h SLA)
- Quarterly review call

---

### Enterprise / Audit Engagement — $5,000–$75,000

**Who it's for:** law firms, regulated-industry AI teams, enterprise AI governance leads, any organization that needs to show an auditor, a regulator, or a general counsel that they ran structured verification.

**What you get (engagement-scoped, not monthly):**
- Annual audit of your AI system's verification posture
- Custom observer pool designed for your domain (legal-read, factual accuracy, hallucination-specific)
- Full drift log analysis with named-observer evidence
- Signed attestation binder (PDF + hash-anchored JSONL) — expert-witness ready
- Structural fix recommendations + re-audit checkpoint at 90 days
- "Weaver-attested" certification badge (pending IRB clearance, Month 9)
- Named point of contact, not a ticket queue

**Pricing anchor:**
- $5,000 — single system, 30-day engagement, attestation binder
- $25,000 — multi-system audit, evidence binder, signed compliance report
- $75,000 — annual retainer, quarterly re-audit, board-ready reporting, litigation support

**Retainer option:** $3,500/mo for ongoing verification posture management.

---

## What "attestation" actually means

Attestation is a dated, named-observer record proving:
1. These outputs ran through structured verification on this date
2. These observers (with these roles and orthogonal context windows) reviewed them
3. These disagreements were logged
4. These drift events were caught and either resolved or escalated
5. This is the structural fix applied

That record is what survives a discovery request. It's what you show the EU AI Act auditor. It's what your general counsel needs before they let you put AI output in a client-facing deliverable.

We don't make the AI smarter. We make the verification legible.

---

## 50% margin floor

All engagements net at least 50% margin after LLM provider costs (yours), Stripe, and our time. If a deal pencils under that, we either rescope or decline. We do not buy revenue.

---

## Ready to start?

Open source: `pip install weaver-protocol`

Hosted: email `weaver@eversound.ai` with your use case and team size. Response within 48 hours.

Enterprise: same email. Include "audit engagement" in the subject. We'll schedule a 60-minute scoping call.
