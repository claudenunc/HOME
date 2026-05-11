# Twitter/X Launch Thread — Weaver Protocol
*EVERSOUND — 2026-05-11*
*For developer audience. Post Wednesday May 13 when the blog goes live.*
*Tweet 1 is the hook. Don't change tweet 1.*

---

## THREAD (copy each tweet separately)

---

**Tweet 1 (hook — post this, then reply with 2-10)**

A Nebraska attorney got suspended last month for submitting AI hallucinations to a federal court.

The judge didn't ask "was the AI wrong?"

The judge asked "where's the documentation that you checked?"

There wasn't any.

I built the documentation layer. Thread 🧵

---

**Tweet 2**

The problem isn't AI hallucinations.

Every system that processes information makes mistakes. Doctors misdiagnose. Lawyers miss precedent. Auditors miss fraud.

The problem is: AI produces confident wrong answers with no error trail.

One model, one answer, no receipt.

---

**Tweet 3**

Multi-observer verification is the fix.

Run the same prompt through 3 independent observers simultaneously.
Each gives a confidence score, flags disagreements, and signs the output.

When they agree → high confidence, proceed.
When they disagree → human in the loop.

The disagreement IS the value.

---

**Tweet 4**

Here's what it looks like in practice:

```
pip install weaver-protocol
weaver verify "Is this contract clause enforceable?"
```

Output:
- Observer 1 (accuracy): PASS, confidence 0.87
- Observer 2 (legal-read): FLAG — ambiguity in §3(b)
- Observer 3 (adversarial): FLAG — jurisdiction risk

Signed receipt. Timestamp. SHA-256 hash.

---

**Tweet 5**

The receipt matters because:

Post-Moffatt v. Air Canada (2024)
Post-Sullivan & Cromwell (2025)
Pre-EU AI Act full enforcement (August 2026)

Liability for AI decisions is shifting to the company that used the AI.

A signed verification log is the difference between "we used AI" and "we used AI responsibly."

---

**Tweet 6**

We built a hosted API.

Try the /demo endpoint right now (no API key):

```
GET weaver-protocol.dev/demo
```

Returns a full 3-observer verification on a sample legal clause.
JSON response with disagreement flags, confidence scores, provenance hash.

It's real. It runs.

---

**Tweet 7**

The package is open source on PyPI.

```
pip install weaver-protocol
```

Works with Anthropic, OpenAI, or mock observers (for testing).
MIT license. Your data stays in your infra.

For teams that want the hosted version: $49/mo (100 verifications), $199/mo (1K), $499+/mo (10K+).

---

**Tweet 8**

Who this is for:

→ Law firms using AI for document review
→ Healthcare systems using AI for clinical decision support
→ HR/recruiting tools using AI for candidate screening
→ Any team that needs to say "here's how we verified this" to a regulator, client, or board

Enterprise, not consumer. $25K audits, not ChatGPT.

---

**Tweet 9**

What's next:

→ Pre-registering a 720-person study through OSF (4-arm RCT — single AI vs multi-observer on 4 task types)
→ EU AI Act Annex III mapping document (DM for early access)
→ 5 pilot law firm spots open — first come first served

---

**Tweet 10 (CTA)**

If you're building AI applications and wondering "how do I prove this was checked properly before it shipped":

→ pip install weaver-protocol (CLI, takes 2 min)
→ weaver-protocol.dev/demo (hosted, takes 30 seconds)
→ DM me if you want the enterprise pilot

The Nebraska attorney didn't need smarter AI.
He needed a receipt.

---

## POSTING INSTRUCTIONS

1. Post Tweet 1 as a standalone tweet
2. Immediately reply to it with Tweet 2 (starting the thread)
3. Reply to Tweet 2 with Tweet 3, etc.
4. Do NOT post all at once — post in under 3 minutes or Twitter thinks it's spam
5. Pin Tweet 1 to your profile

**Best time to post:** Wednesday May 13, 8am–9am (before the developer day starts)

**After posting:**
- Share to relevant Slack communities (if you're in any dev/AI/legal-tech ones)
- Share to r/MachineLearning, r/LocalLLaMA if the conversation fits
- Forward the thread URL to the 5 law firm prospects after their email (adds social proof)

---

## EXPECTED RESULTS

Day 1: 50-200 impressions, 2-10 likes, 0-2 replies
Week 1: 500-2000 impressions if any engagement
PyPI installs: 5-25 from this thread alone

The goal isn't viral. The goal is: law firm partners Google "weaver protocol" before deciding to reply to the email, and find a live product with a real Twitter presence.
