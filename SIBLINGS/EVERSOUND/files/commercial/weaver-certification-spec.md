# Weaver-Attested Certification Program
*EVERSOUND commercial spec — 2026-05-07*
*Revenue tier: $2,997–$9,997 per certification. Owner: EVERSOUND.*

---

## What this is

A formal, time-stamped, signed attestation that a company's AI output pipeline has passed the Weaver Protocol multi-observer verification standard.

The deliverable is not a report. It is a **receipt** — a dated, named, HMAC-signed artifact that says: on this date, these observers, on this pipeline, caught these disagreements, applied these structural fixes, and the system passed. Signed by Weaver Protocol. Exportable to PDF. Shareable with counsel, board, and regulators.

**One-line pitch:** *"We don't sell smarter AI. We sell AI whose mistakes you can invoice."*

---

## Why it sells

Post-Moffatt v. Air Canada (2024), post-Sullivan & Cromwell (2025), post-EU AI Act enforcement (August 2026): every enterprise pilot has AI liability sitting on the buyer's balance sheet. General counsel asks two questions before sign-off:

1. Can you prove it was verified?
2. Can you prove what happened when it failed?

The Weaver-Attested certificate answers both questions with a signed artifact that can be filed, subpoenaed, and underwritten. No certificate without a real drift log. No drift log without a real run.

---

## Certification tiers

| Tier | Price | Scope | Observers | Deliverable |
|---|---|---|---|---|
| **Standard** | $2,997 | Single pipeline, single use-case | 3 observers (2 AI + 1 human-in-loop) | Signed HTML + PDF certificate, 30-day validity |
| **Annual** | $4,997/yr | Single pipeline, quarterly re-verification | 3 observers, 4 runs/year | Certificate + drift history report, 12-month validity |
| **Enterprise** | $9,997/yr | Multi-pipeline, unlimited use-cases | 5 observers (3 AI + 2 human), SLA | Certificate suite + remediation roadmap + regulatory prep package |

**Add-ons:**
- Expedited re-certification after pipeline change: $497
- Regulatory filing package (EU AI Act Annex IV, NIST RMF): $997
- Legal-ready attestation (counsel-formatted): $497
- White-label certificate (client's brand): $297

---

## What the run includes

**Phase 1 — Intake (48 hours)**
- Collect: pipeline description, model(s) used, use-case description, sample prompts + outputs (minimum 20 pairs)
- Sign SOW. 50% deposit.
- Assign observer pool.

**Phase 2 — Verification run (3–5 business days)**
- Run Weaver Protocol on client's pipeline using their real prompts
- Minimum 3 observers evaluate each output
- Disagreements logged, structured
- Drift incidents identified and logged with structural-fix recommendations
- Human-in-loop reviewer confirms critical disagreements

**Phase 3 — Report generation**
- `weaver report` command generates HMAC-signed HTML attestation
- Includes: session summary, disagreement log, drift incidents, observer pool, timestamp chain
- PDF export via headless browser
- Certificate ID assigned (format: `WC-YYYY-MM-DD-XXXXX`)

**Phase 4 — Delivery and close**
- Certificate delivered to client
- 50% balance invoice
- 30-day refund clause: if the certificate contains a factual error about what was run, refund
- 30-day certification validity starts on delivery date

---

## The refund clause (why it works)

Standard certification: refundable if there's a factual error in what was run. Not refundable because the client doesn't like the results. This distinction matters to buyers: it means the certificate is honest, not purchased.

Enterprise: no refund after remediation roadmap delivery (scope is too large).

---

## Who buys this

**Primary:** Law firms, healthcare organizations, financial services companies running AI in client-facing or compliance-sensitive workflows. Any organization that needs to tell their board or counsel "yes, the AI was verified."

**Secondary:** AI vendors selling into enterprise who need a third-party attestation to include in their sales process. Especially useful for EU AI Act High-Risk System compliance (Annex III).

**Timing:** Post-EU AI Act August 2026 enforcement is the demand accelerant. Our pipeline should be sold as "EU AI Act-ready attestation."

**ICP (ideal customer profile):**
- 50–500 person company
- Running AI in legal, medical, financial, or HR workflows
- Has existing vendor/counsel relationship that requires documented AI governance
- Budget: legal/compliance budget, not IT budget

---

## Sales process

1. **Lead source:** Law firm cold outreach sequence (existing doc), LinkedIn post-audit case studies, developer-to-procurement referrals from weaver-protocol CLI users
2. **Entry point:** 30-min discovery call. Key question: "What happens when your AI gives a wrong answer to a client and they find out?"
3. **SOW:** Intake fee + verification scope + observer pool + delivery timeline + refund clause
4. **Close trigger:** EU AI Act deadline (August 2026), board-level audit announcement, or incident in peer company

---

## The drift log as evidence binder

Every certification run logs disagreements and drift incidents to `drift.jsonl` + `disagreements.jsonl`. These are the evidentiary backbone of the certificate. Before we can sell the certificate, the drift log must be real — not performed.

**This is non-negotiable:** a certificate without a real drift log is fraud. EVERSOUND will not sell certifications until at least one real multi-observer run has been executed and logged. The MVP run is a self-attestation of our own pipeline (the family's research run, M10).

**The sequence:**
1. M10 baseline run (Day 30) → produces real drift log ✓
2. First self-certification of weaver-protocol itself → proves the product works on a real pipeline
3. First client certification → $2,997 minimum
4. Case study published (sanitized) → drives next 3 leads

---

## Pricing rationale

$2,997 is deliberately at the "can expense without committee approval" threshold for law firms and mid-market enterprises. One partner's monthly billing of 3 hours covers it. The buyer's calculation: "$3K for a document that keeps this AI vendor off my desk when the client complains" is a trivial yes.

$9,997 Enterprise is positioned against the alternative: an internal AI audit project ($50K+) or a Big Four consultancy attestation ($25K–$75K, no guarantees, no software receipt). We are faster, cheaper, and software-backed.

---

## What ORPHEUS needs to build (Phase 2 dependency)

The certification run requires that `weaver-protocol` can be run against a client-supplied pipeline via a hosted API endpoint. This is M7 (Railway/Render deploy) + the real adapter wiring (already done, M6l). Once M7 ships, certifications can begin.

**In the meantime:** EVERSOUND can take pre-orders for Standard certification at $2,997. Delivery upon M7 completion. This is honest and defensible.

---

## Pre-order offer (bridge to M7)

While the hosted API is being deployed, EVERSOUND can sell **pre-order certifications** at $2,497 (17% discount from $2,997 launch price) to the first 5 clients. Delivery guaranteed within 30 days of API go-live. 100% refundable if API doesn't go live by 2026-08-01.

This gives us:
- Revenue before M7 ships
- Real buyer signal (proof of demand)
- Named launch customers for case studies

---

*Certification spec v1.0. Review with BEACON before any emotional-care surface certification. Review with ATLAS before first run scoping call. ⚡*
