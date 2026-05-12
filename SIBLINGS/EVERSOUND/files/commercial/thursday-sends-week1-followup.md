# Thursday Sends — Week 1 Follow-Up
*EVERSOUND — Day 3 follow-ups to monday-sends-week1.md (sent 2026-05-11)*
*5 emails, ~20 minutes. Short, add value, soft ask. Do not repeat the pitch.*

**Timing:**
- If you sent Monday May 11 → send these **Thursday May 14**
- If you sent Tuesday May 12 → send these **Friday May 16** (skip Saturday — use Monday May 18 if you prefer)

**Strategy for Day 3:** One new piece of information. One soft ask. No apology for following up.
The job is to be worth reading, not to close. Closing happens on the call.

---

## SEND ORDER

1. CoachHub — hottest EU deadline hook (Day 3 specificity on DPA audit)
2. Littler Mendelson — Article 9 mapping (gives them something to evaluate)
3. K&L Gates — sample evidence binder offer (concrete preview)
4. Paradox.ai — per-decision vs. per-policy distinction (technical precision)
5. Offerpad — async architecture detail (removes the "latency" objection before they raise it)

Log each send in `SHARED/STATE/active-deals.md`.

---

## EMAIL 1 — CoachHub (Day 3 follow-up)

**Contact:** Same as Monday — CTO or Chief Product

**Subject:** The DPA documentation angle — more specific than Monday

---

Hi [Name],

Following up on Monday's note.

One specific thing your DPA auditor will ask for under the EU AI Act: evidence that AI-assisted career recommendations were subject to human oversight AND that disagreements between the AI and oversight mechanisms were logged. The Weaver receipt captures both — observer disagreements are recorded at the decision level, not buried in a policy document.

That's the artifact your auditor is looking for. It's also what you'd need if an employee challenged a career decision that involved AI coaching.

I'd rather you see the receipt format before August than scramble to build documentation in July. Still 15 minutes available this week?

Nathan Michel
Foolishness Envy Inc / Weaver Protocol

---

## EMAIL 2 — Littler Mendelson (Day 3 follow-up)

**Contact:** Same as Monday — Chief Innovation or Managing Shareholder

**Subject:** One thing I left out Monday — the Article 9 mapping

---

Hi [Name],

Quick follow-up to Monday's note.

One thing I didn't include: the Weaver verification receipt maps to EU AI Act Article 9 (risk management system requirements) — the section that Annex III high-risk AI is specifically measured against. It's not just an attestation; it's a structured record that answers the six questions Article 9 auditors are trained to ask.

That means when your employment clients ask "what does compliance documentation look like," you have a concrete format to show them — not a policy framework, but a per-decision evidence artifact.

15 minutes to look at the receipt format together?

Nathan Michel
Foolishness Envy Inc / Weaver Protocol

---

## EMAIL 3 — K&L Gates (Day 3 follow-up)

**Contact:** Same as Monday — AI Task Force Chair or equivalent

**Subject:** What "Weaver-attested" looks like — I can send the sample binder

---

Hi [Name],

Following up on Monday's note.

One concrete offer: I can send you a sample evidence binder before any call — takes 2 minutes to look at and tells you whether this is worth your time.

The binder includes: observer disagreement log with session IDs and timestamps, HMAC-signed output attestations, and a mapping to applicable AI Act provisions. It's what you'd hand to a malpractice carrier or present at a client pitch — not a self-assessment, but an independently produced artifact.

Want me to send it over?

Nathan Michel
Foolishness Envy Inc / Weaver Protocol

---

## EMAIL 4 — Paradox.ai (Day 3 follow-up)

**Contact:** Aaron Matos (CEO) or CTO — same contact as Monday

**Subject:** Per-decision vs. per-policy (what makes this different from a compliance doc)

---

Hi Aaron / [Name],

Following up from Monday.

One thing I should have named more precisely: the verification receipt exists per-decision, not per-policy. Every Olivia match produces a distinct receipt with a session ID, observer disagreement breakdown, and timestamp signature. The collection of those receipts is the audit trail an EEOC investigator or plaintiff's attorney would have to argue against decision by decision — much harder than attacking a policy document.

The integration runs async — no latency on Olivia's response time, receipt available within 30 seconds of each match, logged automatically.

Still worth 15 minutes?

Nathan Michel
Foolishness Envy Inc / Weaver Protocol

---

## EMAIL 5 — Offerpad (Day 3 follow-up)

**Contact:** Brian Bair (CEO) or General Counsel — same as Monday

**Subject:** No latency on the offer engine — the async architecture

---

Hi [Name],

Following up from Monday.

One thing I should have been clearer about: the observers run async, so there's no latency impact on offer generation. The receipt is produced and logged within 30 seconds of each offer — automatically, without touching the offer engine's response time.

For a high-volume operation like Offerpad's, that's the only viable integration model. We built it that way specifically because synchronous verification would have been a non-starter for any sub-100ms SLA requirement.

Still up for 15 minutes to see the receipt format?

Nathan Michel
Foolishness Envy Inc / Weaver Protocol

---

## After You Send

Log each in `SHARED/STATE/active-deals.md`:

```
| [Date] | [Company] | [Contact] | Day 3 follow-up sent | [Reply Y/N] |
```

**If they reply:** Open `prospect-reply-playbook.md` — it has word-for-word responses for every scenario.

**If no reply after Day 7 (next Monday/Tuesday):**
See `outreach-week2-followups.md` for the Day 7 email — shorter, asks one genuine question, no close attempt.

**Stop at Day 21.** Two value-add touches after the first email. A third is harassment territory.

---

## What's Still Needed From Nathan

1. **Deploy the API:** `cd ~/HOME/LIVE/weaver-protocol && vercel deploy --prod` — the emails reference weaver-protocol.dev; make the /demo endpoint live before Day 7 follow-ups go out
2. **Post the launch blog:** `launch-blog-post.md` ready — dev.to + LinkedIn, best time is Thursday morning

---

*EVERSOUND ⚡ — 2026-05-12*
*Pair with: monday-sends-week1.md (first emails), prospect-reply-playbook.md (when they respond), outreach-week2-followups.md (Day 7 if no reply)*
