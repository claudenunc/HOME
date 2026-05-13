# Weaver Protocol — Free Attestation Audit Offer
*EVERSOUND — 2026-05-13*
*For use when a prospect is warm but won't commit to a paid audit without proof. Send as attachment or paste into email.*

---

## When to use this

The prospect replied to your cold outreach. They're interested. They asked to see how it works before committing.

**DO NOT send them a YouTube demo. DO NOT tell them to install the library themselves. GIVE THEM AN ARTIFACT.**

This document explains the free audit offer — what it is, what they get, what you need from them, and how to make the ask.

---

## The offer: Free Attestation Audit (5 documents)

**What it is:**
Run weaver-protocol's multi-observer verification on up to 5 AI-generated documents from their workflow. They get back a signed attestation report showing where AI observers agreed, where they disagreed, and what the disagreement log looks like in practice.

**What they get (the artifact):**
1. Signed attestation report (PDF/HTML) — observer agreement rates per document
2. Disagreement log — every flagged passage with the two observers' divergent conclusions
3. EU AI Act readiness note — whether the output structure satisfies Article 9/10 documentation requirements
4. One-line risk summary per document — "3 of 5 documents had observer disagreements on factual claims; disagreements logged with timestamps and observer attribution"

**What they need to provide:**
- 5 AI-generated documents from their workflow (legal briefs, contract reviews, research memos, HR reports — whatever they use AI for)
- Can be anonymized / redacted — we only need the AI output text, not the underlying case data
- Email as attachments or paste into a Google Doc

**Timeline:**
- 48 hours from receipt of documents to signed attestation report

**What it costs them:**
- Nothing. No install. No API keys on their side. No IT approval required.

**What it costs you:**
- ~45 minutes to run the CLI on their documents and compile the report
- The cost of 5 verification sessions (sub-$1 at current API rates)

**The conversation after:**
You deliver the report, schedule a 20-minute debrief call. On that call: "Based on what we found in your documents — [X] disagreements across [Y] outputs — here's what ongoing monitoring looks like." That's the conversion moment.

---

## How to make the ask (copy-paste reply)

Use this when a prospect says "tell me more" or "how does it work" or "can we see a sample":

---

**Subject:** Re: [their subject] — quick offer

Hi [Name],

Rather than explain it on paper — let me show you.

Send me 3-5 AI-generated documents from your team's workflow. Anonymized, redacted, whatever you need. I'll run weaver-protocol's multi-observer verification on them and return a signed attestation report within 48 hours.

The report shows:
- Which outputs had observer disagreements (and on what)
- The timestamped disagreement log (the actual receipt)
- Whether the output structure satisfies EU AI Act Article 9/10 documentation requirements

No install on your end. No API keys. Just email me the documents.

If the report is useful and you want to talk about setting up continuous monitoring, we can have that conversation then. If it's not useful, you've lost nothing.

Can you send me 3-5 documents by end of week?

Nathan Michel
Weaver Protocol / Foolishness Envy Inc
[email] | [phone]

---

## Objection handlers

**"Our IT team needs to approve any new tools."**
→ "No install on your side. You email me documents, I run the tool, I email you the report. Your IT team never touches it. You're approving a PDF, not a software deployment."

**"We're under NDA — can't share client documents."**
→ "Completely understood. Anonymize them or use dummy text with the same structure — I need the AI output format, not the underlying data. Even a 3-paragraph legal summary with client names redacted works."

**"We have our own internal AI review process."**
→ "Perfect — let me run the same documents through ours and you can compare outputs. If our report agrees with your process, you've validated your internal method. If it catches something yours missed, that's the conversation worth having."

**"We need to wait until the regulation is finalized."**
→ "EU AI Act enforcement starts August 2026 — 80 days from now. The firms doing pilots now will have 3-4 months of logged attestation history by go-live. The firms starting in July will have 2 weeks. The artifact we'd produce now is also the artifact you'd submit to show you had a process before enforcement. Early logs are worth more than later ones."

**"We're already using NexArt / another verification tool."**
→ "NexArt certifies that your AI ran the right model. weaver-protocol certifies that the model gave the right answer. They operate at different layers. A document can be faithfully executed on the right model and still hallucinate a case citation. That's what we catch. Run both free pilots on the same documents and compare — they're complementary, not competing."

---

## After the free audit: the conversion sequence

**Debrief call (20 min):**
1. Walk them through the report — don't summarize, show them the specific disagreements
2. "The two documents with the highest disagreement rates — what are those being used for in your workflow?"
3. "If those disagreements had shipped to a client / judge / regulator undetected, what's the exposure?"
4. "Here's what continuous monitoring looks like on those two workflows specifically." → Show scope + price

**Scoped audit proposal:**
After the debrief, send `weaver-audit-sow-template.md` filled in for their specific workflows. Lead with the free audit findings as the motivation for the scope.

**Price anchoring from free audit:**
"Based on what we found — [N] disagreements across [Y] outputs — the scoped audit would cover [workflow A] and [workflow B]. That's $5,000 for the full attestation report with signed observer receipts on 30-day coverage, plus [monitoring tier] ongoing."

---

## Sample attestation report summary (for email context)

If they ask "what does the report actually look like?" — share this example:

---

**Weaver Protocol Attestation Summary**
*Session ID:* WP-2026-0513-demo
*Document:* AI-generated contract review summary
*Observers:* claude-sonnet-4-6 (primary), gpt-4o (secondary), claude-haiku-4-5 (tertiary)
*Timestamp:* 2026-05-13T14:22:11Z
*Agreement rate:* 71% (17 of 24 claims verified across all observers)

**Disagreements flagged (7):**
- Claim 3: "Party B has no prior breach history" — Primary: CONFIRMED; Secondary: DISPUTED (counterexample in exhibit C); Tertiary: UNCERTAIN
- Claim 11: "Liquidated damages clause is enforceable under Delaware law" — Primary: CONFIRMED; Secondary: CONFIRMED; Tertiary: DISPUTED (2024 precedent not reflected)
- Claim 18: "30-day notice requirement is standard for this contract type" — Primary: CONFIRMED; Secondary: UNCERTAIN; Tertiary: DISPUTED

**Risk summary:** 3 of 7 disagreements involve factual or legal claims that, if wrong, create client liability exposure. Disagreement log signed with HMAC-SHA256. This report is the artifact.

---

*The above is a sample. A real report on their documents would show their actual AI output disagreements — not a mock.*

---

## Tracking free audits

Log every free audit in `SHARED/STATE/active-deals.md`:

```
| [Date] | [Company] | [Contact] | Free Audit | Pending debrief | [Notes] |
```

If 5 free audits ship and zero convert, that's product-market signal, not a sales problem. Flag it and we revisit the offer structure.

---

*Gemini/Codex flag #41 — both unavailable this check. Analysis is mine. NexArt objection handler above is derived from ENVY's nexart-differentiation-brief.md + ATLAS's 14Z traction check (early-stage, PR-only, no mainstream coverage — our positioning is safe). Day 30 = 22 days. EU AI Act = 80 days.*
