# Law Firm Cold Outreach — 3-Email Sequence
**Owner:** EVERSOUND  
**Filed:** 2026-05-05  
**Target:** Am Law 200 / regional firms with active AI adoption pilots or AI governance risk exposure  
**Hook:** Post-*Moffatt v. Air Canada*, post-*Mata v. Avianca*, EU AI Act high-risk deadline Aug 2026  
**Goal:** Discovery call → $25K consultancy engagement (M14)

---

## Who to send this to

Target persona: Chief Innovation Officer, Director of Legal Technology, General Counsel, Risk Partner, AI Practice Group Chair.

Qualifying signals (use LinkedIn + Chambers + firm news):
- Firm publicly announced AI adoption (Thomson Reuters CoCounsel, Harvey, Lexis+ AI)
- Firm has a tech-forward innovation partner or LegalTech committee
- Firm litigated or settled a matter involving AI-generated documents in 2024-2025
- Firm has EU clients or operates in EU-regulated industries (financial services, health)

**Do NOT send to:**
- Firms that have not publicly touched AI tooling (they're not ready; outreach costs trust)
- Solo practitioners or firms under 25 attorneys (wrong tier — redirect to CRAFT or open-source)

Personalize the `[FIRM]`, `[NAME]`, and `[SIGNAL]` fields for every send. Never blast.

---

## Email 1 — The structural problem (Day 0)

**Subject:** [FIRM]'s AI verification gap (post-EU AI Act)

---

[NAME],

Law firms adopting AI tools in 2025-26 are generating a new liability surface their malpractice carriers don't have a clean answer for.

The question isn't "did the model hallucinate?" It's: "What verification did you run, when, and where's the record?" *Moffatt v. Air Canada* (2024) established that the liability attaches to the operator, not the provider. A firm that used AI in a matter and cannot produce a structured verification record is holding that liability naked.

Single-model self-verification doesn't close this. A model checking its own output uses the same weights that generated it — the correlated blindspot is structural, not a capability issue that more compute fixes.

I'm [EVERSOUND/Nathan Michel] at Weaver Protocol. We built an open-source multi-observer verification layer that produces a dated, named-observer audit trail for every AI output your team relies on. The artifact isn't an assurance — it's a signed JSONL record showing which observers reviewed the output, where they disagreed, how the conflict was resolved, and who signed off.

That record is what your general counsel can show a court, a carrier, or an EU AI Act auditor.

One question: when [FIRM] runs AI-assisted research or drafts AI-assisted memos, is there a verification step that produces a written record today?

If not — or if the answer is "we ask the attorney to review it" without a structured log — we should talk. Fifteen minutes is enough.

[Calendar link / email reply]

— [Name]  
Weaver Protocol | weaver-protocol.dev

---

**Why this email works:**
- Opens with the liability framing, not the product
- Names the cases (signal: we've done the reading)
- One question at the close — lowers the ask
- No price, no pitch deck, no PDF attachment on cold

---

## Email 2 — Social proof + specificity (Day 5, no reply to Email 1)

**Subject:** Re: [FIRM]'s AI verification gap

---

[NAME],

Following up briefly.

I'll be specific about what we built: Weaver Protocol runs two or more AI observers on every output your team flags for review. Each observer has an isolated context window and an assigned role — accuracy review, legal-risk review, adversarial review. They can't see each other's reasoning before they submit. After they submit, disagreements are logged, scored, and written to an append-only JSONL file that your team can export as a PDF attestation report.

The structured record answers the question your carrier will ask: "What did your review process look like, and where is the documentation?"

We're currently working with [early-adopter framing — update when first client closes]. The law firm use case is the one we built the enterprise tier for:

- Multi-tenant log namespaces (separate per matter, per client, per practice group)
- Custom observer roles (legal-read, privilege-risk, scope-check — you define the taxonomy)
- PDF attestation reports, generated automatically, ready for the matter file

Enterprise engagement starts at $25,000 for setup and first 90 days. After that, monthly support at $3,500/mo or $0 if you self-host on your own infrastructure with the MIT-licensed core.

If this is the wrong moment, I'll leave you alone. If there's a pilot matter where you're already using AI assistance and wondering about the documentation gap — this is the conversation.

Worth 15 minutes?

[Calendar link]

— [Name]  
Weaver Protocol

---

**Notes on this email:**
- Concrete mechanics (two observers, isolated context, roles) builds credibility
- Pricing disclosed early — filters non-buyers, respects attorney time
- "Self-host" option signals we're not trying to lock them in
- Closes with the specific moment of pain (active pilot matter)

---

## Email 3 — Close or release (Day 12, no reply to Email 2)

**Subject:** Closing the loop — [FIRM]

---

[NAME],

I've sent two notes. I'll send one more and then leave you alone unless you reach out.

Here's the one-line version: if [FIRM] is using any AI tool in matters — research, drafting, contract review — and there's no structured log of what the AI produced and what verification was run, you're carrying liability that the EU AI Act's August 2026 high-risk deadline will make more expensive, not less.

If that's already solved on your end, I genuinely want to know how — it would make our protocol better. Reply and I'll take you off the list.

If it's not solved, and you want to see what a 15-minute verification audit of your current AI workflow looks like (no commitment, no pitch deck), book here: [calendar link]

Either way — thank you for the consideration.

— [Name]  
Weaver Protocol

---

**Notes on this email:**
- Explicit close: "one more and then leave you alone" — respects autonomy
- One-line stakes reminder, no rehearsal of prior emails
- Genuine curiosity if they've solved it — this isn't performative; the answer is useful
- Soft inversion: "if it's already solved, tell me" reduces friction
- Clean exit if no response

---

## Follow-up if reply is "not now"

Respond within 2 hours:

> "[NAME] — understood completely. I'll reach back out in [3/6] months when [EU AI Act deadline is closer / your team's pilot matures]. One question if you're willing: what verification step does [FIRM] currently use on AI outputs? Even a one-line answer helps us build the right thing. No pressure either way."

Log to `STATE/clients/[FIRM]-[DATE].md`: date, contact, "not now," stated reason, follow-up date.

---

## CRM fields to track (in STATE/)

For each send:
```
firm: [FIRM NAME]
contact: [NAME, TITLE]
tier_target: enterprise ($25K)
email_1_sent: [DATE]
email_2_sent: [DATE]  
email_3_sent: [DATE]
reply: [yes/no/partial]
reply_summary: [one line]
discovery_call: [date or null]
next_action: [follow-up in 90 days / SOW draft / closed-lost]
```

---

*Filed by EVERSOUND 2026-05-05. Part of M14 ($25K consultancy engagement by Day 120 = 2026-09-02).*
