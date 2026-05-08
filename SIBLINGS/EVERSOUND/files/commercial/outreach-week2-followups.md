# Week 2 Follow-Up Sequences
*EVERSOUND — 2026-05-08*
*For use when Week 1 outreach (law firm + developer sequences) has gone out and received no reply.*

---

## Overview

Week 1 sequences are in:
- `law-firm-outreach-sequence.md` (3 emails, law firm partners)
- `developer-outreach-sequence.md` (3 touches: email + Discord + GitHub)

This document provides Week 2 follow-ups — shorter, value-add, no ask. The job of Week 2 is to be worth reading, not to close.

**Send Week 2 only if:** Week 1 Email 3 was sent AND no reply in 7+ days.

---

## Law Firm — Week 2 Email

**Subject:** One thing from last week + a question

**Body:**

Hi [Name],

Quick follow-up on the AI verification note I sent last week.

One thing I didn't include: the EU AI Act's high-risk AI provisions take full effect August 2026. Law firms using AI for document review, case research, or client-facing tools will need documented evidence of human oversight and error-detection. The regulation doesn't specify the mechanism — but a signed, dated multi-observer disagreement log is exactly the kind of artifact that satisfies the requirement.

My one question for you: does your firm currently have a process for documenting AI errors before they reach a client? Not asking you to buy anything — genuinely curious what that looks like in practice at your firm.

If the timing is ever right to talk through what we built, I'm here.

[Signature]

---

**What this email does:** anchors to the EU AI Act deadline (August 2026 — real, confirmed), asks a real question instead of pitching, positions you as someone who knows the regulatory landscape.

---

## Developer Outreach — Week 2 Email

**Subject:** Quick thing that might save you a debugging hour

**Body:**

Hi [Name],

Sent you a note last week about Weaver Protocol — didn't want to pile on if timing is bad, but wanted to share one thing first.

We added a `weaver report` command that generates a signed HTML attestation report from your session logs. HMAC-SHA256, zero external deps, reads from `sessions.jsonl + disagreements.jsonl`. The idea: when your AI does something weird, you have a timestamped receipt of exactly what the observers saw and where they disagreed.

Might be useful even outside the multi-observer setup — just as a local debug log with a professional format.

```bash
pip install weaver-protocol
weaver report --log-dir ./weaver_logs
```

No API keys needed for the report generator.

Hope something in there is useful. If you want to talk AI verification architecture, happy to.

[Signature]

---

**What this email does:** leads with a concrete free feature (`weaver report`), includes a copy-paste command, removes the buy friction. Developers respond to specifics over pitches.

---

## Discord/Slack — Week 2 Message

**For use in:** channels where Week 1 drop happened and got no traction.

**Message:**

Hey — dropped a note here last week about Weaver Protocol, the multi-observer AI verification library. Didn't want to just leave it hanging.

Quick update: we added a `weaver report` command — generates a signed HTML attestation from your local session logs. No API keys, no hosting required.

```
pip install weaver-protocol
weaver verify --text "your claim"
weaver report --log-dir ./weaver_logs
```

Anyone here doing AI-in-production work who's had to deal with hallucination incidents? Curious what your current approach is for documenting them.

---

**GitHub Issues — Week 2**

If you opened an issue on a repo that uses an AI verification or testing library, this is the Week 2 follow-up if the maintainer didn't respond:

**Comment:**

Hi [maintainer name],

Checking in on this. Quick note: `weaver report` is now in v0.1.0 — generates a signed attestation HTML from session logs if you want a quick way to document verification runs. Might complement what you're building here.

`pip install weaver-protocol` — no external deps for the core features.

Happy to help scope an integration if useful.

---

## CRM Tracking (copy from Week 1 template)

After each Week 2 touch:

```
Date: YYYY-MM-DD
Contact: [Name] / [Firm] / [Channel]
Week 1 sent: [date]
Week 2 sent: [date]
Response: [Y/N]
Notes:
```

Move to "inactive" if no reply after Week 2. Do not send a Week 3. Two touches with value is the rule — a third is harassment territory.

---

## Timing

| Sequence step | When |
|---|---|
| Week 1 Email 1 | Day 0 |
| Week 1 Email 2 | Day 3 |
| Week 1 Email 3 | Day 7 |
| Week 2 Follow-up | Day 14+ (only if no reply) |
| Stop | Day 21 — move to inactive |

---

*EVERSOUND ⚡ — 2026-05-08*
*Revenue is a tool. Healing is the point. The follow-up is just good manners.*
