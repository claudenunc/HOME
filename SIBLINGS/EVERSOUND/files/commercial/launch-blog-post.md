# A Nebraska Attorney Just Lost His License Because of AI. Here's What the Rest of Us Need to Do.

*Platform: dev.to | Medium | Substack | LinkedIn article*
*Audience: Developers, CTOs, legal ops, healthcare AI teams*
*CTA: pip install weaver-protocol + /demo endpoint*
*By: Nathan Michel / Weaver Protocol*

---

In April 2026, a Nebraska attorney became the first lawyer in US history to receive an indefinite suspension for citing AI-hallucinated case law.

Not a warning. Not a fine. Indefinite suspension.

One month later, a federal court ordered Hyde School to implement mandatory AI verification protocols before any AI-generated content could be submitted as evidence.

I've been building AI verification infrastructure for three months. Let me tell you what I think this means - and what we can actually do about it.

---

## The Real Problem Isn't Hallucination

Every developer in this thread has seen the demos. "AI said the sky is green." "AI cited a case that doesn't exist." We've been treating this as a calibration problem - smarter models, better prompts, RAG pipelines, guardrails.

That framing is wrong, and the Nebraska case proves it.

The attorney didn't use some janky open-source model. He used a well-known commercial LLM, trusted the output, filed the brief, and lost his license.

The problem isn't that AI hallucinates. The problem is that **there was no mechanism to catch it before it caused harm** - and when it did cause harm, **there was no record proving anyone tried**.

That's two separate failures: technical and legal. Most AI tooling addresses the technical failure. Almost nothing addresses the legal one.

---

## What "Attested" Actually Means

Lawyers and regulators don't care if your AI is 97% accurate. They care about one question: *when it was wrong, what process did you have in place to catch it, and can you prove that process ran?*

This is what due diligence means in the age of AI liability. Not "our model has low perplexity." Not "we use GPT-4." Due diligence means: a provable, dated, independent check ran on this output before it was relied upon.

That's the gap I'm trying to close.

**Weaver Protocol** is an open-source Python package that runs any AI output through 2-5 independent observers - each seeing the text alone with a different critical role (accuracy, safety, legal-read, adversarial, factual). No observer sees another's assessment before forming their own. The structural isolation is the point.

If two observers disagree: flag for review, log the disagreement, write it to an HMAC-signed record. If they agree: pass, still write the signed record, because the record is the compliance artifact.

The output isn't just a JSON blob. It's a timestamped, tamper-evident document you can hand to opposing counsel and say: "We ran three independent observer assessments before this output was used. Here is the signed log. Here are the disagreements. Here is the remediation."

---

## The EU AI Act Is Not a Future Problem

August 2026 is three months away.

Annex III of the EU AI Act classifies AI systems used in employment, legal interpretation, credit scoring, and medical decision-making as high-risk. High-risk AI systems require documentation, human oversight, and - critically - **provable error-detection mechanisms**.

If you're selling B2B software that touches any of those domains, you're in scope. "We use a reputable LLM provider" is not a defense. "We ran attested multi-observer verification and here is the dated record" is.

Post-August 2026, that argument will fail in Brussels too - and the EU can fine you 3% of global annual turnover.

---

## How to Try It Right Now (5 Minutes, No Card)

```bash
pip install weaver-protocol
```

Run a 3-observer verification on any text, zero API keys required:

```python
from weaver.session import WeaverSession
from weaver.observer import Observer
from weaver.adapters.mock import make_mock_observer

ws = WeaverSession(session_id="my-first-check", log_dir="./weaver_logs")
provider = make_mock_observer()

for role in ["accuracy", "safety", "legal-read"]:
    ws.add_observer(Observer(name=f"obs-{role}", role=role, provider_fn=provider))

score = ws.verify("The defendant admitted liability on page 12.")
print(f"WeaverScore: {score.score:.2f}")
print(f"Flag for review: {score.flag_for_review}")
```

Or hit the hosted demo endpoint - no API key, no account:

```bash
curl https://your-deployed-api.railway.app/demo
```

You'll get back a full verification response: WeaverScore, 3 observer assessments with confidence levels, a disagreement flag, and a signed provenance record.

---

## The Architecture (For the Developers in the Room)

Each observer is initialized with a role-specific system prompt. The accuracy observer is looking for factual claims that can be checked. The safety observer is looking for harm potential. The legal-read observer is looking for assertions that require legal authority.

Critically: **observers don't communicate**. No shared context, no chain-of-thought bleed. Each one produces an independent assessment. Then we compare.

Disagreement detection looks for:
- One observer flags a claim; another doesn't
- Confidence scores differ by more than a threshold
- Flags are contradictory

When disagreement is detected, it's logged to drift.jsonl alongside the session. The weaver report CLI generates a signed HTML attestation from these logs.

```bash
weaver verify --prompt "The defendant admitted liability on page 12." --observers 3
weaver report --log-dir ./weaver_logs
```

The report is the product. The signed HTML document is what your general counsel can show a regulator.

---

## What We're Not

**Mock observers don't catch real hallucinations.** The free tier uses deterministic mock observers. To catch real AI errors, you need real LLM observers - that's the paid hosted API, or you wire your own Anthropic/OpenAI keys to the open-source package.

**Weaver is not a replacement for human review.** It's a force multiplier. Weaver gives you the triage layer that routes the high-risk outputs to human review - and gives you the paper trail proving that triage ran.

**We don't store your prompts** for training purposes. The hosted API writes session metadata to Postgres for the drift log. The open-source version stores everything locally in JSONL files.

---

## The Business Case (For the CTOs)

A law firm with Weaver Protocol on the Pro tier ($199/mo): 5,000 verifications per month. At the load of a 10-attorney firm doing AI-assisted research, that's every material AI output triple-checked, signed, and logged for about $0.04 per verification.

The compliance department's question isn't "does this cost money?" It's "does the cost of verification exceed the cost of the first incident?" For any firm where a single bad AI output costs more than $199, the math is closed.

---

## What's Next

Weaver Protocol v0.1.0 is live on PyPI. The hosted API is deployed and ready.

We're building toward:
- Month 3: First enterprise audit engagement ($5K-$25K, SOW template ready)
- Month 9: Post-IRB certification tier ($2,997-$9,997 Weaver-attested badge)
- August 2026: EU AI Act Annex III compliance package for regulated industries

The window where "we trusted our AI provider" is a viable legal defense is closing. What comes after that window requires receipts.

We build receipts.

---

**Try it:**
```bash
pip install weaver-protocol
```

**Hosted demo (no API key):** GET /demo on the deployed API

**GitHub:** claudenunc/weaver-protocol

**Pricing:** $49/mo starter / $199/mo pro / $499/mo enterprise
**Consultancy:** $5K-$75K audit engagements / SOW template available on request

*Nathan Michel - Weaver Protocol / Foolishness Envy Inc*
*"We don't sell smarter AI. We sell AI whose mistakes you can invoice."*

---

*Post this on: dev.to (tag: ai, python, compliance, llm) | LinkedIn article | HN Show HN | Substack*
*Cross-post timing: Wednesday or Thursday morning for max dev.to reach*
