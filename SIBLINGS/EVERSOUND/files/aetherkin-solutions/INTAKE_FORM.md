# Client Intake Form — AetherKin Solutions

Target: 15 minutes to complete. Every question exists because I need the answer to design the family.

Deliver via: Typeform / Tally / Google Form / shared Notion / inline-email — whichever the client prefers. A Typeform template lives at `intake-form.typeform.json` (TODO: build).

---

## Section 1 — About you and your business (5 questions)

1. **Business name** (legal name + DBA if different)
2. **What does your business do?** (2-3 sentences — not your marketing pitch, your actual operations)
3. **Team size and roles** (e.g., "1 attorney, 1 paralegal, 1 receptionist" or "solo coach, part-time VA")
4. **Primary location(s) and timezone(s)**
5. **Your role + email + phone** (the person I'll be working with)

## Section 2 — How customers reach you today (4 questions)

6. **How do new prospects find you?** (check all: website form, Google Ads, referrals, social, cold outreach, Zillow/Yelp/industry directory, other)
7. **What channels do customers use to talk to you?** (check all: phone, SMS, email, website chat, Slack, WhatsApp, Signal, Telegram, Discord, Messenger, Instagram DM, in-person)
8. **Which channel has the most inbound volume right now?**
9. **What's the #1 channel you WISH you could respond to 24/7 but currently can't?**

## Section 3 — Your current tools (5 questions)

10. **What CRM / contact database do you use?** (HubSpot, Pipedrive, Salesforce, Monday, Airtable, spreadsheet, none, other)
11. **Where does customer communication live?** (Gmail, Outlook, Intercom, Helpscout, Zendesk, Front, other)
12. **What calendar tool?** (Google Calendar, Outlook, Calendly, Acuity, Cal.com, other)
13. **What payment / billing tool?** (Stripe, Square, QuickBooks, FreshBooks, Ivy, PracticeBetter, other)
14. **What other SaaS tools are critical?** (free text — list anything that needs to connect)

## Section 4 — The real work (6 questions)

15. **What do you spend the MOST time on that you wish you didn't?** (free text — this is the highest-leverage question)
16. **What customer question gets asked most often?** (free text — this is the first workflow we build)
17. **What's a task that absolutely should NOT be automated?** (free text — this is where we put the escalation rules)
18. **How do you currently handle a customer in crisis / emergency / urgent situation?** (free text — this is where Guardian's rules come from)
19. **What does "a great customer experience" look like in your business?** (free text — this tunes the sibling voices)
20. **What would you want your team's time freed up to do instead?** (free text — this is the ROI story)

## Section 5 — Compliance & risk (3-5 questions, varies by vertical)

**Ask all clients**:
- 21. **Do you have any regulatory requirements?** (HIPAA, SOC 2, GDPR, CCPA, industry-specific, none-that-I-know-of)
- 22. **Where must customer data live?** (US / EU / on-prem / no preference)
- 23. **Are there topics the AI must NEVER discuss?** (medical advice, legal advice, investment advice, crisis support, competitor comparison, pricing negotiation, specific topics per your business)

**Medical / therapy / coaching only**:
- 24. **What's your license / credential type?** (determines compliance posture)
- 25. **Do you need a BAA?** (HIPAA Business Associate Agreement)

**Law firm only**:
- 24. **Which jurisdictions do you practice in?**
- 25. **What practice areas?** (determines intake qualification rules)

**E-commerce only**:
- 24. **What platform?** (Shopify, WooCommerce, BigCommerce, Magento, custom)
- 25. **Typical order value range?** (determines refund / support thresholds)

## Section 6 — Fit and logistics (4 questions)

26. **Budget range for deployment?** (under $5K / $5-15K / $15K+ / not sure)
27. **Who signs the check on your side?** (name + role — so I know who needs to be in the SOW meeting)
28. **Target go-live date?** (specific date / "ASAP" / "next quarter" / "whenever")
29. **Anything else I should know before the discovery call?** (free text)

---

## What I do with the answers

Before the discovery call:
1. Match to the closest family template (law, medical, coaching, e-commerce, church, real estate, SaaS, or custom).
2. Draft a sibling roster for their business — 3-6 siblings with names, roles, missions.
3. Draft the 3-5 n8n workflows that would deliver the biggest wins based on #15, #16, #18.
4. Estimate runtime cost based on expected message volume.
5. Prepare a demo of what their family would look like (screenshots of the dashboard populated with their info).

That demo is the hook for the call. By the time we're 20 minutes in, they're not looking at "AI" — they're looking at their team, just with roles they didn't have before.

---

## Red-flag answers that mean "don't take this client"

- Question 18 ("crisis handling") is a shrug or "we don't deal with that." Every business deals with crises — they just might not know it. If they refuse to think about it after I raise it, they're not ready for AetherKin.
- Question 21 disclosure hidden until signing (HIPAA obligations they didn't mention up front).
- Question 26 + 28 mismatch — wants Enterprise scope, Starter budget, next-week go-live.
- They tell me "just make it like ChatGPT but with our data." That's not a client, that's a request I should politely decline or redirect to building a custom GPT.

## Green-flag answers that mean "lean in"

- Specific, concrete answer to #15 (they know their biggest pain).
- Answer to #17 has a human-centered reason, not just "I don't know."
- Answer to #18 shows they already think about safety.
- Question 20 answer is NOT "grow revenue" but something human ("spend more time with clients" / "stop working weekends").
