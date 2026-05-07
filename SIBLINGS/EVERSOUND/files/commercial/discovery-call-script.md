# Weaver Protocol — Discovery Call Script
*15-minute playbook. Two tracks: Developer ($49/mo) and Enterprise/Law Firm ($25K+).*
*Written by EVERSOUND, 2026-05-07.*

---

## Before the call (2 minutes)

1. Know which track: did they come from developer outreach or law firm outreach?
2. Open terminal, navigate to a dir with `weaver` installed
3. Have `weaver verify` ready to run live
4. Know their name and company from the outreach reply

---

## Opening (0:00–1:00)

> "Thanks for making time. I want to respect your 15 minutes — so I'll do a quick live demo first, then let you tell me what you're actually trying to solve. Sound good?"

*Pause. Let them say yes. Don't skip this — it hands them control and drops their guard.*

---

## The 90-second live demo (1:00–2:30)

Run this in the terminal as you talk:

```bash
pip install weaver-protocol   # already installed — skip for demo
weaver verify --text "The regulation requires compliance by Q3 2026." --observers 2
```

Expected output:
```
Session: demo-001
Observer 1 (accuracy-reviewer): score=0.82, flagged=False
Observer 2 (legal-reviewer): score=0.71, flagged=False
Consensus: PASS (threshold=0.40)
Disagreement delta: 0.11 — logged
Attestation written: weaver_logs/demo-001.jsonl
```

While it runs, say:

> "Two independent observers — separate context windows, orthogonal roles. They just reviewed the same output from different angles. The disagreement between them is logged with a timestamp. That log is the artifact. Watch."

Then:
```bash
weaver report --log-dir ./weaver_logs
```

> "That just built a signed HTML report. HMAC-SHA256. Tamper-evident. The kind of thing you attach to a compliance exhibit or show your general counsel."

**Stop. Let it land. Do not fill the silence.**

---

## Transition: listen (2:30–5:00)

> "That's what it does. What are you building, and where does verification show up as a problem?"

**Listen for:**
- "We're using LLMs in production and getting burned by hallucinations" → developer track
- "We're worried about liability / regulatory audit / client trust" → enterprise track
- "We've tried prompt engineering / self-checking" → you have the answer (single-model can't check itself)
- "We don't have a problem yet" → they're pre-need; give them the law firm case study; schedule a follow-up

---

## Developer track — close path (5:00–10:00)

**Their pain:** They're shipping LLM features and know they'll eventually get burned. They want structured verification without building it themselves.

**Your response:**

> "The local toolkit is free and open source — MIT license, installs in 60 seconds, works with your existing Anthropic or OpenAI keys. Most developers start there. The hosted API tier starts at $49/month — that adds Postgres-persisted sessions, tamper-evident cloud reports, and Stripe-managed API keys. You bring your own provider keys; I don't touch your API costs."

**Objections:**
- *"I can just run this locally"* → "You can, and you should start there. The $49 tier is for when you need the report to live in the cloud, be shareable with stakeholders, and be signed by a key that isn't your laptop. One compliance review pays for a year."
- *"Is this production-ready?"* → "The package is on PyPI, MIT-licensed, 34 tests green. The hosted API is in early access. You'd be customer #1 — which means you get direct access to me for 30 days to make sure it fits your stack."
- *"Why not just use [other tool]?"* → "What tool? I want to know what you evaluated." (Listen. Then: "The difference is the attestation record. Most tools tell you the output passed or failed. Weaver tells you *which observer caught what*, *when*, and *what the disagreement delta was*. That's the exhibit. The other tools don't produce exhibits.")

**Close:**

> "Want to get set up today? It's literally `pip install weaver-protocol` and 10 lines of Python. I can send you the quickstart — or if you want the hosted tier, I'll send you the checkout link and you'll have an API key in 5 minutes."

---

## Enterprise/Law Firm track — close path (5:00–12:00)

**Their pain:** They're deploying or evaluating AI for legal research, contract review, or client-facing work. They need to answer "what did you verify, and can you prove it?" to their GC, their client, or the EU AI Act auditor.

**Your response:**

> "The framework that gets you there isn't better AI. It's a verifiable record of structured verification — multiple observers, logged disagreements, signed output. The kind of record you can attach to a file, show in discovery, or hand to your compliance team. That's what Weaver produces."

**Walk them through the law firm case:**

> "Imagine you're using AI-assisted research and a brief goes out. Six months later, opposing counsel subpoenas your AI process. Right now, what do you show them? If you have Weaver running, you show them the session log — every observer, every disagreement, every flag, timestamped and signed. That's not a nice-to-have after *Mata v. Avianca* and *Moffatt v. Air Canada*. That's table stakes."

**Pricing:**

> "Our consultancy engagement is $5,000–$75,000 depending on scope. That's an audit of your current AI stack — we run the attested multi-observer protocol, document what we find, produce a signed evidence binder, and give you a 30-day refund clause on verification failure. Typical Am Law 200 engagement runs $15–25K. A 30-day discovery call is free."

**Objections:**
- *"We need to go through procurement"* → "Understood. I can send you a one-page executive summary and a SOW draft with the scope and price — that's the document your procurement team needs to start the process. Want me to send that today?"
- *"We have internal IT that would need to approve this"* → "Of course. The good news: Weaver is open-source, MIT-licensed, runs on your infrastructure, and your IT team owns the keys. I configure it; I don't host your data unless you want the cloud tier."
- *"What's your track record?"* → "We're early-stage — which means you'd be our first enterprise client, and the engagement comes with direct-founder access for the full term. We can also offer a pilot: run Weaver on one workflow for 30 days, produce one attestation report, and if it doesn't hold up to your GC's review, you don't pay."

**Close:**

> "Here's what I'd suggest: let me send you the SOW template today. Your team reviews it. If it makes sense, we sign, I send the 50% deposit invoice, and we start your deployment within a week. Does that timeline work?"

---

## Wrap (12:00–15:00)

**If yes / interested:**
- Get their email (if not already known)
- Commit to sending: SOW draft (enterprise) OR checkout link (developer) within 2 hours
- Set a follow-up time if they need internal approval

**If not ready:**
- "What's the biggest open question?" (write it down — this is product intel)
- "Would it make sense to check back in [30 days / when X happens]?"
- Ask for one referral: "Who else in your network is dealing with AI liability questions?"

**Do not:**
- Discount on the first call without ENVY sign-off
- Promise a feature that isn't shipped
- Commit Nathan's time for an on-site without asking first
- Take a client whose outcome you'd be ashamed of

---

## Post-call checklist (same day)

- [ ] Send promised doc (SOW or checkout link) within 2 hours
- [ ] Log the call in CLIPBOARD.jsonl with outcome, objections heard, next step
- [ ] If they said yes: issue Stripe checkout link → wait for webhook → confirm API key delivered
- [ ] If they said no: log what stalled it — this is product/pricing intel for ATLAS
- [ ] Draft case study stub if it closes (tweet + LinkedIn + landing page — even if unpublished)

---

*This script is a starting point. The best discovery calls go off-script because the prospect says something unexpected and you listen. The script is for when you need to steer back.*

*⚡ EVERSOUND*
