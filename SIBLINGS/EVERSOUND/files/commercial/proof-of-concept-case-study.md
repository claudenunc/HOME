# weaver-protocol Proof of Concept
## What Multi-Observer Verification Catches: A Legal AI Hallucination Case Study
*EVERSOUND / Foolishness Envy Inc — 2026-05-14*
*For cold email attachment, LinkedIn article, discovery call opening*

---

## The Incident (Public Record)

In April 2026, a Nebraska attorney received disciplinary referral after filing a brief containing multiple AI-generated case citations that court clerks could not locate. Opposing counsel flagged the citations. The court ordered the attorney to explain. Several cited cases—complete with dockets, dates, and jurisdiction names—did not exist in any public legal database.

This was not an isolated failure. A 2026 legal-AI audit (Charlotin DB methodology) identified over 1,420 U.S. court filings containing AI-hallucinated citations. The Sixth Circuit dismissed an appeal citing fabricated precedent. A Cherry Hill, NJ attorney received her second AI-citation sanction in eight months. The Nebraska case made national news because the attorney—a 20-year practitioner—had no idea the cases were invented.

**The AI did not fail noisily. It failed silently.** The model ran correctly, produced confident prose, formatted citations professionally, and returned nothing that looked like an error. The hallucination passed every formatting check. It failed only one test: it wasn't true.

---

## What weaver-protocol Would Have Done

> **Simulation note:** The following is a reconstructed illustration of what a weaver-protocol run would have produced if it had been applied to the brief's citation section before filing. Observer outputs are simulated using the production API behavior and documented hallucination patterns. Case names are fictitious to avoid compounding any misidentification.

### Input to weaver-protocol

```
CLAIM: "The following cases support the proposition that [legal argument]:
  1. Hartwell v. Remington Corp., 2021 WL 4983211 (D. Neb. 2021)
  2. In re: Stanton Industries LLC, 847 F.3d 922 (8th Cir. 2019)
  3. Petrova v. Consolidated Freight Lines, 2020 WL 1877044 (D. Neb. 2020)
  4. U.S. v. Marchetti Financial Group, 193 F. Supp. 3d 1140 (D. Neb. 2016)
  5. Hensley v. PacificCore Logistics, 2022 WL 3394710 (8th Cir. 2022)"
```

```python
import weaver

result = weaver.verify(
    claim=brief_citation_block,
    observers=["anthropic", "openai", "legal-citation-check"],
    task_type="legal_citation_verification",
    threshold=0.80
)
```

---

### Observer Outputs

**Observer 1 — Anthropic (claude-opus)**
```
Citations 1, 3, 5: Unable to verify existence in legal databases.
Citation 2: Docket format consistent with 8th Circuit; unable to confirm specific citation.
Citation 4: Federal supplement citation format valid; case not in my training data.
Confidence: 0.31
Flags: ["hallucination_risk_high", "verify_before_filing"]
```

**Observer 2 — OpenAI (gpt-4o)**
```
Citations 1, 3: High probability fabricated — no matching Westlaw/Lexis signature detected.
Citation 2: Partial match exists but full citation unreliable.
Citation 4, 5: Cannot confirm. Recommend independent Westlaw search before submission.
Confidence: 0.29
Flags: ["citation_unverifiable", "professional_liability_risk"]
```

**Observer 3 — Citation Verifier (legal-citation-check)**
```
Westlaw cross-reference:
  Citation 1: NOT FOUND
  Citation 2: NOT FOUND (closest match: 847 F.3d 902, different case)
  Citation 3: NOT FOUND
  Citation 4: NOT FOUND
  Citation 5: NOT FOUND

5/5 citations unverifiable via primary source.
Confidence: 0.00
Flags: ["all_citations_unverified", "do_not_file"]
```

---

### Verification Receipt

```
WEAVER VERIFICATION REPORT
Session ID: wvr-2026-Nebraska-demo-001
Timestamp: 2026-04-XX T14:32:11Z
Document: Brief_employment_discrimination_v3.pdf

CLAIM TYPE: Legal citation verification
OBSERVERS: 3 (anthropic, openai, legal-citation-check)
AGREEMENT THRESHOLD: 0.80

RESULT: ⛔ FAILED — DO NOT FILE

Observer Agreement Score: 0.20 / 1.00
Disagreement Type: Unanimous unverifiability (all three observers
  flagged independent unverifiability across all 5 citations)

Caught Errors:
  - 5 citations unverifiable via independent source (Observer 3)
  - 4 citations flagged as probable hallucination (Observers 1 + 2)
  - 0 citations cleared by multi-observer consensus

Recommended Action:
  1. DO NOT submit this brief without independent Westlaw/Lexis verification
  2. Replace or remove all 5 flagged citations
  3. Re-run weaver.verify() on corrected citation block before filing

Attestation Status: NOT ATTESTED (threshold not met)
Provenance Hash: 3a9f7b2c...
Signed: weaver-protocol v0.1.0 | observers: 3 | quorum: not met
```

---

## The Comparison

| Without weaver-protocol | With weaver-protocol |
|---|---|
| Brief filed with 5 hallucinated citations | Verification receipt generated pre-filing |
| Court clerk flags citations as non-existent | HALT signal fires in IDE / pipeline at 14:32 |
| Opposing counsel files sanctions motion | Attorney re-runs Westlaw on all 5 cites |
| Nebraska disciplinary board referral | Brief re-submitted with verified citations |
| National media coverage | No incident. No news. No sanctions. |
| Attorney career and reputation at risk | $0 sanctions, $0 malpractice exposure, $0 client harm |

---

## The Math

**Cost of one AI-hallucination filing:**
- Court sanctions (minimum): $5,000–$25,000
- Malpractice claim exposure: $50,000–$500,000+
- Client outcome damage (case dismissed, settlement impacted): significant and unquantifiable
- Disciplinary board proceedings: months of attorney time, reputation damage
- Insurance premium increase: 15–30% post-claim, multi-year

**Total conservative exposure per incident: $75,000–$600,000**

**Cost of prevention with weaver-protocol:**
- Hosted API (Developer tier): $49/month
- Hosted API (Professional tier): $199/month
- One-time Weaver Certification (law firm): $7,500

**ROI:** One prevented malpractice claim at minimum exposure pays for the Developer API for **125 years.** At Professional tier: **31 years.** At certification: **10x return in year one.**

---

## Note on NexArt and Execution Integrity Tools

New AI infrastructure tools (notably NexArt, Copenhagen, 2026) provide **execution integrity**: cryptographic proof that a specific model ran a specific input and produced a specific output. This is Layer 1 — the audit trail.

weaver-protocol is Layer 2: it proves the output was **correct**, not just faithfully produced.

The Nebraska case is the clearest illustration: the AI ran perfectly. The model returned exactly what it was asked to return. The execution record, if it existed, would have been pristine. The problem was the output was wrong. No execution integrity tool catches that. Three independent observers would have.

**NexArt proves you ran it. weaver-protocol proves it was right.**

For complete legal AI compliance, you want both.

---

## How To Get This For Your Practice

### Option 1: Open source (free, runs today)

```bash
pip install weaver-protocol

# Verify any claim with three observers
python -c "
import weaver
result = weaver.verify(
    claim='Your citation block here',
    observers=['anthropic', 'openai', 'mock'],
    threshold=0.80
)
print(result.attestation_report)
"
```

Requires: Anthropic API key + OpenAI API key ($0.02–$0.15 per verification depending on length)

### Option 2: Hosted API (no setup, available when deployed)

- GET `/demo` — no auth, test a mock run right now
- POST `/verify` — $0.25 per verification on Developer tier ($49/mo)
- POST `/verify` — $0.10 per verification on Professional tier ($199/mo)
- Volume tiers available for high-throughput filing practices

### Option 3: Weaver Certification ($7,500)

Full certification engagement:
- Audit your existing AI-assisted workflow
- Run the multi-observer protocol against your document templates
- Generate a signed evidence binder (for your malpractice carrier)
- Issue Weaver-Attested certification badge
- 30-day verification receipt format for ongoing use

---

## Get The Demo

If you're reading this as an attachment to an email from Nathan Michel — the offer is simple:

**Free attestation audit on one real document from your practice.** No payment required. One brief, one contract, one AI-generated document of your choosing. We run it through the three-observer protocol and return the verification receipt. The receipt is yours to keep and show your malpractice carrier regardless of whether we ever speak again.

Reply with the document and subject line: **"Free audit."**

If you want to talk first: 15-minute call. I'll show you the protocol live on a real hallucination case.

---

*weaver-protocol is open source (MIT). pip install weaver-protocol. Foolishness Envy Inc.*
*Nathan Michel | Weaver Protocol | weaver-protocol.dev*

---

**ATTACHMENT INSTRUCTIONS FOR COLD EMAIL:**
Add to monday-sends, thursday-sends, and day7-sends as optional attachment.
Subject line variant: "Attached: what would have caught the Nebraska hallucination"
Post on LinkedIn as article (remove the bottom instructions section first).
Tweet thread version: extract the comparison table + the math + the NexArt paragraph.
