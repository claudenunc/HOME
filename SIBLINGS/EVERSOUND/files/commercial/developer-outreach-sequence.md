# Developer Outreach Sequence — weaver-protocol
*EVERSOUND, 2026-05-06T17Z. Target: M8 first paid install by Day 60 (2026-07-04).*

---

## Who this reaches

**Primary target:** Python developers building production LLM applications who need audit
trails, compliance receipts, or reliability proof. They are already using Anthropic or
OpenAI APIs. They've been burned by a hallucination at least once.

**Secondary target:** DevOps / ML engineers at companies where legal/compliance is starting
to ask questions about AI output accountability.

**Not a target (yet):** Enterprise architects making $50K+ decisions. That's the consultancy
sequence. This sequence is for the individual developer who might pay $49–$199/mo or convince
their team lead to.

---

## Channel 1: Cold Email / LinkedIn DM (3-touch sequence)

### Email 1 — The Problem Hit (Day 0)

**Subject:** Your users deserve to know when your AI is wrong

Hey [name],

I noticed you're building with [Claude/GPT/LangChain/etc.]. Quick question: when your AI
is confidently wrong, how do you know?

We shipped weaver-protocol last week — it runs two AI observers against your query
simultaneously, looks for disagreement, and produces a tamper-evident attestation report.
No API key needed to try it:

```
pip install weaver-protocol
weaver verify --prompt "What is the statute of limitations in California for breach of contract?"
```

The report signs itself with HMAC-SHA256. If your legal/compliance team ever asks "how do
we know this answer was right?" — the report is the answer.

60-second quickstart: [link to QUICKSTART.md in repo]

Is this a problem you're trying to solve?

— EVERSOUND / Weaver Protocol


### Email 2 — The Compliance Receipt (Day 7)

**Subject:** Re: quick follow-up — the piece your general counsel wants

[name],

Following up in case Email 1 landed in the wrong folder.

Specifically for anyone building in law, healthcare, or financial services in 2026: the EU
AI Act compliance window closes August 2026. The default defense for "my AI gave bad advice"
is now "show me the verification log." We built the log.

weaver-protocol runs locally, zero data leaves your infrastructure, your API keys are yours.

The hosted API ($49/mo) gives you cloud storage of attestation reports + PDF export for
legal use. That's the piece your general counsel can hand to opposing counsel.

Three-minute read on how it works: [link to README / law-firm-1-pager.md]

Worth 15 minutes?

— EVERSOUND


### Email 3 — Honest Offer (Day 14)

**Subject:** Last thing — build it yourself or use ours?

[name],

I don't like sequences that end with a hard sell, so I'm going to be straight with you.

You could build multi-observer verification yourself. It's not complicated — two API calls,
a comparison function, a signing step. Takes a day or two. We open-sourced the whole thing:
[GitHub link]

The case for the hosted API ($49/mo) is narrowly this: we do the infra, we version the
reports so they're tamper-evident over time, and we give you a PDF export that your
compliance team can stamp and file. If none of that matters to your use case, use the CLI
for free and we'll still be glad you did.

If it does matter — 7-day free trial, no card required on the $49 tier.

What are you building?

— EVERSOUND


---

## Channel 2: Discord / Slack Community Template

*(Use in: Anthropic Discord #tools-and-libraries, OpenAI Dev #show-and-tell,
LangChain Discord #community-showcase, AI Engineer Discord)*

**One message, no thread bumping, no DMs unless they DM first:**

---

Hey — shipped something last week that might be useful here: weaver-protocol
(https://pypi.org/project/weaver-protocol/).

It runs two AI observers against your query simultaneously, catches disagreements, and
produces a tamper-evident attestation report you can hand to legal/compliance. Works
with Anthropic + OpenAI, CLI or hosted API.

`pip install weaver-protocol && weaver verify --prompt "your question here"`

Zero API keys needed for the mock demo. Happy to help with integration if you're trying
to wire it into an existing pipeline.

---

**Follow the "help first" rule:** If someone in the community has posted about LLM
reliability, hallucination detection, or AI audit trails — help them with weaver-protocol
genuinely BEFORE posting the above. Don't lead with product.


---

## Channel 3: GitHub Issue Template

*(Use in: relevant issues about LLM reliability, hallucination, audit trails in repos like
LangChain, guidance, marvin, instructor, etc.)*

**Only comment when your answer is genuinely helpful, not promotional:**

---

If you're looking for a lightweight layer that catches disagreement between observers
without building the whole thing yourself — we shipped weaver-protocol recently
(https://github.com/[org]/weaver-protocol).

Two-line integration:

```python
from weaver import WeaverSession
result = WeaverSession(observers=[...]).verify(your_prompt)
```

It's MIT-licensed, runs locally, no data leaves your infra. Full quickstart:
[link to QUICKSTART.md]

---

**Hard rule:** Never post this template in an issue unless you've read the issue carefully
and weaver-protocol actually solves the problem being described. One irrelevant post = bad
signal for the family name.


---

## Tracking and conversion target

| Channel | Target volume | Expected conversion | M8 path |
|---|---|---|---|
| Cold email/DM | 20 contacts/week | 2-3% → paid | $49-$199/mo |
| Discord communities | 4 communities | 1% → tries, 10% of tries → paid | $49/mo entry |
| GitHub issues | 10 relevant issues/week | 5% → tries, 5% of tries → paid | $49/mo entry |

**First paid install target:** Day 60 (2026-07-04). At current conversion assumptions,
30 days of consistent outreach (starting Day 30 / 2026-06-04) should produce 1-3 paid
installs. Starting earlier is better. Starting now is best.

---

## What needs to exist before outreach starts

- [x] `pip install weaver-protocol` works
- [x] QUICKSTART.md (60-second demo, no API keys)
- [x] GitHub repo public with good README
- [x] `weaver report` CLI (attestation report for free tier conversion)
- [ ] Railway/Render deploy live (for $49 hosted API tier) — Nathan account needed
- [ ] Stripe checkout live (for payment) — Nathan account needed

**Practical implication:** outreach to email/Discord can start now with the CLI/free tier.
The hosted API ($49/mo) conversion requires Nathan's Railway + Stripe accounts first.

---

*Sequence drafted by EVERSOUND 2026-05-06T17Z. Gemini/Codex unavailable (15th+ flag).
Own judgment applied. This is the M8 activation document.*
