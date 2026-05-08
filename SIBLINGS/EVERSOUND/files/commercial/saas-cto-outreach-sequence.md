# SaaS CTO / AI Team Lead — Outreach Sequence
## Weaver Protocol | 3-Touch Cold Email Sequence

**Target persona:** CTO, VP Engineering, Head of AI, Staff/Principal Engineer at SaaS companies shipping LLM-powered features  
**Goal:** Discovery call → SDK trial → $49/mo or $199/mo hosted API conversion  
**Timing:** Email 1 → wait 4 days → Email 2 → wait 7 days → Email 3  
**Send from:** Nathan's personal domain or Foolishness Envy Inc

---

## Touch 1 — Lead with the EU AI Act clock

**Subject:** EU AI Act goes live August 2026 — your LLM outputs have a compliance problem

**Body:**

Hey [First Name],

Quick question before August hits: when your LLM generates a response that turns out to be wrong, what's your audit trail?

Not the logs — the verification record. The artifact that proves a human or second system reviewed the output before it reached the user.

The EU AI Act's high-risk provisions kick in August 2026. If your product touches HR, finance, legal, medical, or safety-critical decisions (broadly defined), you're in scope. "We used GPT-4" is not a compliance answer.

I built Weaver Protocol to close exactly this gap. It's a multi-observer verification layer: three independent AI observers check the same output in isolation, disagreements get flagged and reason-coded, every session produces a tamper-evident attestation report your counsel can actually use.

Open-source. MIT license. `pip install weaver-protocol` and run your own session before we talk.

Worth a 30-minute call?

— Nathan Michel  
Foolishness Envy Inc  
github.com/claudenunc/weaver-protocol

P.S. The hosted API is $49/mo for unlimited verifications up to 10K requests. First month free if you book this week.

---

**CRM note:** Tag: SaaS-CTO-T1 | Track: open rate, reply rate | Goal: call booked or trial started

---

## Touch 2 — Case for the engineering team (4 days after T1)

**Subject:** Re: EU AI Act — one concrete thing your team can ship in a sprint

**Body:**

Hey [First Name],

Following up from Monday. No reply needed on the compliance angle — I know that's legal team territory and you're moving fast.

Here's a more immediate reason Weaver might matter to your team:

**Your LLM has a confidence problem.** It sounds the same whether it's right or wrong. Your engineers know this. Your PM pretends it doesn't exist. Your users find out the hard way.

Multi-observer verification surfaces the disagreements before the user does. When three models independently check a claim and two of them push back, that's a signal your single-model pipeline completely misses. Disagreement rate over time is actually a meaningful accuracy proxy — something you can show in a sprint retrospective or a board deck.

We've open-sourced the full protocol. Your team can read every line. Integrate in an afternoon with our SDK, or hit our hosted API if you want zero infra overhead.

Concrete ask: could you put me in front of whoever owns your AI reliability story? 30 minutes. I'll bring the disagreement-rate data from our own internal runs.

— Nathan

---

**CRM note:** Tag: SaaS-CTO-T2 | If no reply after T2, move to T3 nurture track (outreach-week2-followups.md)

---

## Touch 3 — Final ask, lower the bar (7 days after T2)

**Subject:** Last note — free trial if you want it

**Body:**

Hey [First Name],

Last note from me on this — I don't want to clog your inbox.

If the timing is off or you're not the right person, totally understand. One small ask before I stop:

If you're building anything with LLMs and want a sanity check on your output quality — run a free session with Weaver before you decide. Zero commitment.

```bash
pip install weaver-protocol
weaver verify --prompt "your test prompt here"
```

It'll generate a local attestation report in about 30 seconds. If the disagreement rate surprises you, we have something to talk about. If it doesn't, you've at least got a baseline.

Hosted API is at [link — add after deploy]. Free trial, no card required.

Good luck with the build.

— Nathan

---

**CRM note:** Tag: SaaS-CTO-T3 | If no response: move to 60-day re-engage list | Do NOT follow up again in the same sequence

---

## Sequence Notes

**Who to send to:**
- Founder/CTO at Series A–C SaaS companies (5–100 engineers)
- Head of AI / Staff Engineer titles at companies with active LLM feature work
- VP Engineering at companies in EU AI Act scope (HR tech, legal tech, fintech, health tech, prop tech)

**Where to find them:**
- LinkedIn: search "Head of AI" + company size 50–500
- GitHub: contributors to LangChain, LlamaIndex, or similar OSS repos
- Y Combinator company directory (W22–S25 cohorts, "AI" vertical)
- DevTo / Hacker News "Who's Hiring" — companies advertising AI/ML engineer roles

**What to track:**
- Open rate target: >30% (subject line A/B test if below)
- Reply rate target: >5% on Touch 1
- Call booked target: 1 per 20 T1 sends
- Trial started target: 1 per 10 T1 sends (lower bar, no call required)

**Personalization tokens:**
- [First Name] — required
- [Company] — use if you've done any research on their stack
- [Specific pain] — if you know they ship in EU market or are post-Series B compliance-aware

**Do NOT send to:**
- Companies already using a named AI compliance vendor (they'll say "we have this")
- Crypto/web3 companies (different risk model)
- Consumer apps without enterprise/B2B surface (wrong budget bracket)

---

## Handoff to hosted API trial

When a prospect clicks or replies with interest in the trial:
1. Send them to: [hosted API URL — add after deploy]
2. They sign up, get a `wp_...` API key via Stripe checkout
3. First month free (use Stripe coupon code: WEAVER60)
4. Follow up in 7 days: "How'd the first session go?"

If they convert to paid: mark M8 complete. Send case study request 30 days after go-live.

---

*EVERSOUND — Day 4, 2026-05-08. Pairs with: saas-cto-1-pager.md, outreach-week2-followups.md*
