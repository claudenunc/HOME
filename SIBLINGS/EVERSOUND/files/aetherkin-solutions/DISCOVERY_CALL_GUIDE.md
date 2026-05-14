# AetherKin Solutions — Discovery Call Guide (90 min)
*EVERSOUND — 2026-05-14T10Z*
*Use this for: AK-2 first discovery call and every AetherKin call after.*
*Read once before the call. Keep open on second screen during.*

---

## Before the call (15 min prep)

1. Read their intake form answers if they filled it out (INTAKE_FORM.md — 29 questions).
   If no intake form, spend 10 min on their website + LinkedIn before dialing.

2. Know which vertical they're in and which template you'll demo:
   - Coaching → 6-agent coaching family (intake, session notes, follow-up, referrals, escalation, retention)
   - Law firm → 4-agent legal family (research review, document audit, client intake, billing alerts)
   - Church → 5-agent pastoral family (prayer routing, visitor follow-up, crisis escalation, volunteer coordination, event ops)
   - Real estate → 4-agent RE family (lead intake, follow-up, referral loop, listing brief prep)
   - E-commerce → 4-agent DTC family (tier-1 support, returns/recovery, VIP escalation, retention signals)
   - SaaS → 4-agent creator/customer success family (onboarding nudges, product Q&A, churn flags, breakout signals)
   - Healthcare → 4-agent clinical-adjacent family (patient comms, intake triage, follow-up, billing alerts — BEACON review required before this goes live)

3. Know the tier you're pitching:
   - Starter ($2,500 + $300/mo): 1-3 person team, single workflow, minimal integration
   - Pro ($7,500 + $1,000/mo): 5-25 team, multi-workflow, Slack/CRM/calendar wiring
   - Enterprise ($20K+ + $3,500/mo): Compliance requirements, multi-location, BEACON safety floor required

4. Have the intake form URL ready to share if they haven't filled it out yet.
   (Or paste the link to INTAKE_FORM.md and offer to walk them through it live.)

---

## Call structure

### Min 0–3: Set context and tone

"Thanks for making time. I want to keep this 20 minutes — 10 minutes you talk, 10 minutes I
show you something specific. If it's not relevant, I'll tell you that myself and we end early.
If it is, we figure out what a next step looks like. Sound good?"

*Why this works: removes the high-pressure feel, signals you respect their time,
gives you permission to pivot or end early without awkwardness.*

---

### Min 3–18: Discovery questions (you listen, they talk)

Pick 4 of these 6. Match to what you learned in prep. Don't read them verbatim.

**Q1 — The workflow toll:**
"Walk me through a typical week for [role you're pitching to]. Where does the team
spend time that surprises you — work that technically needs to happen but probably
shouldn't require a person?"

**Q2 — The leak:**
"What falls through the cracks most consistently? Not in a crisis — just the slow steady drip
of things that don't get followed up, don't get logged, don't get escalated until it's late."

**Q3 — The bottleneck:**
"Who on your team is the bottleneck for [intake / follow-up / client communication / ops decisions]?
What happens to that person's capacity when the business grows 30%?"

**Q4 — The compliance moment:**
"Are there any documented requirements — legal, compliance, accreditation, regulatory —
that touch the workflows you're describing? Or any that you're expecting in the next 12 months?"
*(This surfaces GDPR, EU AI Act, ICF, SOC 2, HIPAA exposure. If they mention any of these,
slow down — that's the buying decision driver.)*

**Q5 — The tool graveyard:**
"What have you tried before to solve this — software, consultants, internal hires?
What worked and what didn't?"
*(Answers this tells you their exact objections before you hit them.)*

**Q6 — The metric:**
"If this was working better — let's say 6 months from now — what's the number that would
have moved? Retention rate, hours recovered, response time, revenue per employee?"
*(This becomes the ROI anchor in the SOW.)*

---

### Min 18–30: Show them something specific

Do NOT run a general demo. Show them the one template that matches their vertical.

"Based on what you just told me, here's what the agent family would look like in your setup."

Then walk through:
1. The 4–6 agents in their vertical (by name, what each one does)
2. The trigger: "Agent 1 fires when a [form submission / new lead / prayer request / ticket]
   comes in. Here's what it sends."
3. The escalation: "When Agent 3 detects [crisis language / VIP signal / churn pattern],
   it hands to a human immediately — your team gets a Slack ping. The agent never makes the
   call alone."
4. The log: "Every action is timestamped and logged. You have a full audit trail."

If they ask "can it do X?" — your answer is almost always yes, with scope clarification:
"Yes — that's a workflow we wire in the first week. It's one of the 3-10 n8n workflows
included in the deploy."

---

### Min 30–45: Qualification — confirm tier and timeline

Three questions:

**Timeline:** "If the SOW looked right, when would you want to go live? Is there a specific
date that's meaningful — a product launch, a compliance deadline, a quarter start?"

**Decision:** "Who else needs to be in the room before this moves forward? Are you the
decision-maker, or is there a CTO/CFO/ED who needs to sign?"

**Budget:** "Our install range is $2,500 to $7,500 depending on scope, plus $300–$1,000/month.
Does that land in a range that's possible, or do we need to find a smaller first step?"

*If budget is the blocker:* "We have a Starter tier that's a single-workflow install — one
agent, one problem, $2,500 once and $300/month. It's designed to prove the value before
you invest in the full family."

*If timeline is the blocker:* "We do one-week deploys. We could have your first agent live
the week you sign. What's blocking you from a decision before [their stated timeline]?"

*If decision-maker is missing:* "Can we get them on a 20-minute call this week? I want to
make sure the SOW answers their specific questions — it'll make the close faster."

---

### Min 45–55: SOW framing

"I'll draft the SOW within 48 hours. Here's what it'll include:

- The 4/5/6 agents scoped to your workflow (I'll name each one)
- The 3-10 n8n workflows we'll wire in week 1
- The integrations: [Slack / HubSpot / Calendly / Stripe / whatever they named]
- Go-live timeline: [X days from deposit]
- Your team's roles (who approves agent responses, who handles escalations)
- Price: $[tier] deploy + $[monthly] monthly, 30-day cancel on the monthly
- 50% deposit to start, 50% at go-live

Does that structure work, or is there something you need to see that I'm not including?"

---

### Min 55–65: The close (if they're ready)

"Before we hang up — two things:

One: I'll send you the SOW within 48 hours. It'll have a 50% deposit invoice attached.
As soon as that clears, we start the week.

Two: I want you to read the SOW before you commit. If anything in it isn't right,
tell me within 48 hours and we revise. I'm not trying to close you on a call —
I'm trying to build something that works.

When's the best time for you to have eyes on it this week?"

---

### Min 65–75: Safety check (do not skip this)

Before you wrap, ask one more question:

"One thing I want to make sure we cover: your [clients / members / customers] —
are any of them in situations where a slow or wrong response from an AI could create
a real problem? Mental health, crisis, medical, financial distress?"

**If they say yes or maybe:** BEACON reviews before deploy. Non-negotiable.
Note it in the SOW draft. Do not promise a go-live date until BEACON has cleared the
crisis-detection path.

**If they say no:** Log the answer. Still scope the escalation path in the SOW so there's
always a human on the back end.

---

### Min 75–90: Wrap and next steps

Repeat the three things they said that made this relevant:
"You mentioned [the leak], [the bottleneck], and [the compliance moment]. The SOW will be
scoped to those three specifically. If it doesn't address them directly, tell me."

Then:
"SOW in 48 hours. If I miss that, ping me. I'll also include my cell number in the email
so you have a direct line. Thanks for your time — this was useful."

---

## After the call (do within 2 hours)

1. Update `SHARED/STATE/active-deals.md`:
   ```
   | [date] | [Company] | [Name] | AetherKin [Starter/Pro/Enterprise] | Discovery call done | $[deal value] | [date] | SOW due [date] |
   ```

2. Draft SOW from `weaver-audit-sow-template.md` (adapt brackets to this client).
   Attach 50% invoice.

3. Send SOW within 48 hours. Add to calendar as a hard deadline.

4. If BEACON flag was raised: send her a one-line note to SHARED/ROOM/inbox/BEACON/
   before sending the SOW.

---

## Red lines (do not negotiate these on the call)

- Never promise a go-live date without a signed SOW and deposit received
- Never promise agents will replace a specific named person on their team
- Never commit runtime API costs to Foolishness Envy — always pass-through, client's keys
- Never promise HIPAA-compliant or GDPR-compliant without BEACON + legal review
- Never promise a weekly support hour count above tier (Starter=10, Pro=40)
- Never promise results (hours saved, revenue generated) — promise inputs (workflows deployed, agents configured, training completed)

---

## If the call goes sideways

**"We already have ChatGPT/Copilot/Notion AI":**
"Those are single-model tools. AetherKin is a coordinated family — 4-6 agents working
together, each with a specific function, handing off to the next. It's the difference
between one employee and a team. The question isn't whether you have AI — it's whether
it coordinates."

**"We need to think about it":**
"That's totally fair. The SOW is the thing to react to — not a verbal pitch. When I send it,
read section 3 (the agent scope) first. If it matches what you told me, the rest is logistics.
If it doesn't, tell me and we fix it."

**"We don't have budget right now":**
"The Starter tier is $2,500 once. Most clients recover that in one month of admin hours not
spent. The ROI math is usually: how many hours per week are going to [intake / follow-up /
support tasks]? At even $25/hr blended cost, $2,500 needs 100 recovered hours to pay back —
that's 4-5 weeks at a conservative estimate. Is the spend blocker budget or timing?"

**"We want to see a live demo first":**
"I can set up a 15-minute async demo — a recording that shows the specific workflow for
your vertical. I'll have it to you within 24 hours. If it answers your questions, we book
the call then. Easier than scheduling another live session."

---

*EVERSOUND ⚡ — 2026-05-14T10Z*
*Milestone: AK-2 first discovery call — Day 30 (2026-06-04)*
*Revenue target: AK-3 first paid deploy ($2,500+) — Day 60 (2026-07-04)*
*Red lines: BEACON clears any emotional-care surface before SOW is signed*
