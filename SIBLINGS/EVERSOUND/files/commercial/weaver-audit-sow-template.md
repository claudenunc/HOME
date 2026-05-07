# Statement of Work — Weaver Protocol Audit Engagement
**Template version:** 1.0 | Filed by EVERSOUND 2026-05-07  
**Tier:** $5,000–$75,000 | Typical: $25,000 single-system 30-day engagement

---

## How to use this template

1. Fill in every `[BRACKET]` field before sending.
2. Remove this header block.
3. Send as PDF with 50% deposit invoice attached.
4. Do not modify the Deliverables, Limitation of Liability, or Confidentiality sections without ENVY sign-off.

---

# STATEMENT OF WORK

**Prepared by:** Foolishness Envy Inc ("Weaver" or "we")  
**Client:** [CLIENT LEGAL NAME] ("Client")  
**SOW Date:** [DATE]  
**Effective Date:** [DATE — typically 5 business days after deposit clears]  
**SOW Number:** WP-[YEAR]-[SEQ, e.g. 001]

---

## 1. Engagement Overview

Client has deployed or is piloting an AI system described as:

> **System name:** [e.g., "Document Review Assistant" / "Contract Analysis Tool"]  
> **Provider:** [e.g., Anthropic Claude / OpenAI GPT-4o / Custom fine-tune]  
> **Use context:** [e.g., "Review of discovery documents for privilege and relevance" / "Contract clause extraction and flagging"]  
> **User base:** [e.g., "Litigation associates at [Firm]" / "50 licensed users"]  
> **Outputs used for:** [e.g., "First-pass review surfaced to supervising partners" / "Client-facing deliverables subject to partner sign-off"]

Client seeks an independent verification audit under the Weaver Protocol to produce a signed attestation record demonstrating that structured, multi-observer verification was conducted on AI outputs — suitable for internal compliance, regulatory inquiry response, or litigation support.

---

## 2. Scope of Work

### 2a. Output Sample Collection (Days 1–5)

Client provides [NUMBER, e.g. 200–500] representative AI output samples from their production system. Samples are provided as:
- [ ] Exported JSON/CSV from the AI system's log
- [ ] Screen-captured PDFs (converted to text)
- [ ] Direct API access with read-only credentials

**Minimum sample size:** 100 outputs. Fewer than 100 may limit statistical confidence in the attestation binder — noted in the report if applicable.

**Confidentiality:** Samples are processed under the confidentiality terms in §7. Weaver does not retain client data post-engagement unless agreed in a Data Processing Addendum.

### 2b. Observer Pool Configuration (Days 3–7)

Weaver configures a multi-observer pool specifically for Client's domain and output type. Standard roles for a legal AI system:

| Observer Role | Purpose |
|---|---|
| `accuracy` | Factual correctness of legal claims, citations, date references |
| `legal-read` | Legal accuracy, regulatory claims, misstatement of controlling authority |
| `privilege-check` | Potential privilege-waiver signals in output |
| `hallucination` | Fabricated case citations, statute references, or procedural claims |
| `scope` | Did the AI stay within its declared task? Did it volunteer unrequested legal advice? |

Custom roles added for Client's specific use case: [LIST CUSTOM ROLES OR "None"]

**Observer count per session:** [2–5, typically 3]  
**LLM models used for observers:** [e.g., "Claude Sonnet 4.6 (accuracy/legal-read) + Claude Haiku 4.5 (hallucination/scope)"]  
**Runtime LLM costs:** Weaver's own API keys, included in engagement fee. Client does not need to provide API keys for this engagement.

### 2c. Verification Run (Days 5–20)

Weaver runs the configured observer pool across Client's output sample. Each output receives:
1. Independent review by each observer (no observer sees another's assessment before submitting)
2. WeaverScore computation (0.0 = full agreement, 1.0 = hard conflict)
3. Automatic logging to append-only JSONL (sessions + disagreements + drift)
4. Flagging at threshold [0.4 default — adjustable per Client request]

All outputs above threshold are reviewed by a Weaver analyst before inclusion in the attestation binder. High-score outputs receive a written analyst note.

### 2d. Structural Fix Recommendations (Days 18–25)

For each pattern of disagreement or drift detected, Weaver produces:
- A named, categorized drift event record
- A concrete structural fix recommendation (system prompt change, retrieval filter, output validation step, or human-review gate specification)
- A recommended re-audit checkpoint (see §2e)

Recommendations are prescriptive, not vague. "Add a disclaimer" is not a recommendation. "Append the following system prompt instruction to prevent the observer's documented hallucination pattern" is.

### 2e. 90-Day Re-Audit Checkpoint

Included in this engagement: one re-audit session at 90 days from go-live, scoped to the subset of outputs that were flagged or structurally fixed. Confirms whether fixes held in production. Re-audit produces a supplemental attestation record appended to the original binder.

---

## 3. Deliverables

All deliverables are provided within 30 days of Effective Date (re-audit excepted).

| # | Deliverable | Format | When |
|---|---|---|---|
| 1 | Observer pool configuration spec | Markdown/PDF | Day 7 |
| 2 | Verification run report — all sessions | JSONL (sessions + disagreements + drift) | Day 22 |
| 3 | Attestation binder | Signed HTML + SHA-256 anchored JSONL | Day 25 |
| 4 | Structural fix recommendations | Markdown report | Day 28 |
| 5 | Executive summary | 2-page PDF, partner-readable | Day 30 |
| 6 | 90-day re-audit attestation supplement | Appended to binder | Day 120 |

**Attestation binder contents:**
- Cover page (engagement details, date, scope, Weaver version)
- Session-level verification summary (WeaverScore distribution, flag rate, observer agreement rate)
- Per-observer result table (role, flags raised, confidence, assessment excerpts)
- Full disagreement log (all inter-observer conflicts with output excerpts)
- Drift event log (all structural issues caught with evidence and fix status)
- HMAC-SHA256 signature over the full payload
- Key-ID and signature algorithm metadata

The binder is formatted for presentation to:
- Internal compliance/ethics board
- Law firm management committee
- Regulator inquiry response (EU AI Act, FTC, state bar)
- Opposing counsel / court (if required as discovery evidence of AI due diligence)

---

## 4. Timeline

| Milestone | Target date |
|---|---|
| SOW signed + 50% deposit received | Day 0 |
| Sample collection complete | Day 5 |
| Observer pool configuration delivered to Client for review | Day 7 |
| Observer pool approved by Client | Day 9 |
| Verification run complete | Day 20 |
| Attestation binder draft to Client | Day 25 |
| Final binder delivered | Day 30 |
| 90-day re-audit | [Date = Effective Date + 120] |

Timeline assumes Client provides output samples by Day 3 and reviews observer pool configuration within 48 hours of delivery. Delays on Client side extend timeline proportionally, not at Weaver's cost.

---

## 5. Fees and Payment Terms

### Engagement fee: **$[AMOUNT]**

Standard ranges by scope:
- Single system, 100–200 outputs, 30-day engagement: **$5,000**
- Single system, 200–500 outputs, multi-role observer pool: **$25,000**
- Multi-system audit, evidence binder, signed compliance report: **$50,000**
- Annual retainer, quarterly re-audit, board-ready reporting: **$75,000/year**

**This engagement:** $[AMOUNT]

### Payment schedule:
- **50% ($[HALF AMOUNT]) due on SOW signature.** Work does not begin until deposit clears.
- **50% ($[HALF AMOUNT]) due on delivery of final attestation binder (Day 30).**
- 90-day re-audit is included — no additional charge.

### Payment method:
- ACH transfer to [BANK DETAILS] — preferred, no fee
- Wire transfer — $35 incoming wire fee added to invoice
- Stripe invoice — 2.9% + $0.30 processing fee added to invoice

### Refund policy:
- Deposit is refundable in full if Weaver is unable to begin work by Day 10.
- After observer pool configuration is approved (Day 9), deposit is non-refundable — configuration work is done.
- Final payment is due on delivery regardless of whether Client has reviewed the binder. Review period does not extend the payment obligation.

---

## 6. Roles and Responsibilities

| Responsibility | Weaver | Client |
|---|---|---|
| Observer pool configuration | ✅ | Review + approve |
| Output sample collection | — | ✅ (provide by Day 3) |
| Verification run execution | ✅ | — |
| Attestation binder generation | ✅ | — |
| Structural fix implementation | Recommendations | ✅ (implement) |
| Re-audit sample collection | — | ✅ (provide by Day 100) |
| API keys for observers | ✅ (Weaver's own) | — |
| Data Processing Addendum (if required) | Draft | Sign |

**Client point of contact for this engagement:** [NAME, TITLE, EMAIL]  
**Weaver engagement lead:** EVERSOUND / Foolishness Envy Inc  

---

## 7. Confidentiality

Both parties agree:

1. Client's output samples are treated as confidential. They are processed solely for this engagement and not retained after delivery of the attestation binder, except as required by applicable law.
2. Weaver's observer pool configuration, scoring methodology, and attestation binder format are proprietary. Client receives the deliverables for their own use; reverse-engineering the methodology for independent resale is prohibited.
3. Weaver may reference this engagement in anonymized form in sales materials, case studies, or academic publications — client name and system details anonymized unless Client consents in writing to a named case study.
4. Standard exceptions: information already public, received from a third party without restriction, required by legal process.

---

## 8. Limitation of Liability and Warranty Disclaimer

The Weaver Protocol attestation binder documents that structured, multi-observer verification was conducted on the specified output samples. It does not:
- Guarantee that the verified AI system is free of errors, hallucinations, or legal risk in all future outputs
- Constitute legal advice, legal representation, or a legal opinion
- Certify compliance with any specific regulation (EU AI Act, HIPAA, state bar rules) — Client is responsible for determining whether the attestation satisfies applicable regulatory requirements
- Replace professional legal review of AI outputs in high-stakes contexts

Weaver's total liability for any claim arising from this engagement is capped at the engagement fee paid. Neither party is liable for indirect, consequential, or punitive damages.

---

## 9. Term and Termination

- This SOW is effective from the Effective Date through delivery of the 90-day re-audit supplement.
- Either party may terminate for cause (material breach uncured within 10 business days of written notice).
- If Client terminates after Day 9 without cause: deposit is forfeited. If Weaver terminates without cause: deposit is refunded in full.

---

## 10. General Terms

- **Governing law:** [STATE], USA. Disputes resolved by binding arbitration under AAA Commercial Rules, single arbitrator, [CITY] venue.
- **Entire agreement:** This SOW, plus any Data Processing Addendum, constitutes the entire agreement for this engagement. Supersedes all prior oral or written representations.
- **Amendment:** Changes require written agreement signed by both parties.
- **Independent contractor:** Weaver is an independent contractor. Nothing in this SOW creates an employment, partnership, or joint venture relationship.

---

## 11. Signatures

By signing, each party confirms they have read, understand, and agree to this Statement of Work.

**Foolishness Envy Inc**

Signature: _________________________________  
Name: Nathan Michel  
Title: Founder, Foolishness Envy Inc  
Date: ________________

**[CLIENT LEGAL NAME]**

Signature: _________________________________  
Name: ________________  
Title: ________________  
Date: ________________

---

*Weaver Protocol SOW Template v1.0 — EVERSOUND / Foolishness Envy Inc — 2026-05-07*  
*This template is proprietary. Do not distribute outside of active client engagements.*
