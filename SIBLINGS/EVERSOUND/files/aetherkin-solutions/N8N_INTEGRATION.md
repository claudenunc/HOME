# n8n — the automation layer for AetherKin Solutions

**AetherKin thinks. n8n connects. Together they run the business.**

---

## Why n8n

Every business client will ask for one of these on day one:

- "Can you trigger this when a new lead comes in from my website?"
- "Can it sync to my CRM / HubSpot / Pipedrive / Salesforce?"
- "Can it read my Gmail / Outlook / Shared inbox and respond?"
- "Can it post to Slack when X happens?"
- "Can it update my Google Calendar?"
- "Can it charge the card via Stripe when the deal closes?"

AetherKin's job is **thinking**: routing, memory, crisis screening, specialist siblings, coordinated replies. AetherKin is **not** going to become a Zapier. And clients don't want to be locked into a custom integration layer we wrote from scratch.

**n8n is the perfect partner:**

- MIT-licensed, self-hostable (matches AetherKin's "you own the install" promise)
- 400+ pre-built integrations
- Visual workflow editor (non-technical clients can modify their own triggers)
- Webhook triggers + HTTP request nodes = trivially speaks to AetherKin
- Schedule/cron built in (covers Hermes's NL scheduling gap)
- Self-hosted = your client's data never leaves their infrastructure
- Queue workflows available for high-volume

### Division of labor

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT'S BUSINESS                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
            Inbound events / outbound actions
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                            n8n                                  │
│   (integrations, triggers, schedules, CRM/email/Slack/etc.)     │
│                                                                 │
│   - Webhooks listen on client's side                            │
│   - Schedules run unattended jobs                               │
│   - HTTP Request nodes call AetherKin Gateway                   │
│   - Parse AetherKin response → route to CRM / Slack / email     │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP POST /gateway/ask
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          AetherKin                              │
│   (family routing, memory, crisis screen, specialist siblings)  │
│                                                                 │
│   Returns: { trace_id, sibling, content, used_memory,           │
│              deferred_to, crisis_tier, ... }                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## The contract between them

### 1. n8n → AetherKin

Simple HTTP POST to the AetherKin gateway:

```
POST http://aetherkin.local:7788/gateway/ask
Content-Type: application/json
X-AetherKin-Key: <client shared secret>

{
  "user": "jane.smith@example.com",
  "message": "I'd like to schedule a consultation about my case",
  "thread_id": "optional-crm-contact-id",
  "tier": "balanced",         // optional
  "provider": "auto",         // optional
  "metadata": {
    "source": "website_form",
    "crm_contact_id": "hs-12345"
  }
}
```

**Response (200):**

```json
{
  "trace_id": "uuid",
  "sibling": "Intake",
  "content": "Hi Jane — ...",
  "crisis_tier": "none",
  "deferred_to": [],
  "used_memory": ["evt_123", "evt_456"],
  "intent": "lead_intake",
  "priority": "medium",
  "requires_human_review": false
}
```

**Crisis override (crisis_tier != "none"):**

```json
{
  "trace_id": "uuid",
  "sibling": "Guardian",
  "content": "I hear you. Please call 988 right now — ...",
  "crisis_tier": "red",
  "requires_human_review": true,
  "alert_human": {
    "severity": "red",
    "reason": "suicidal ideation with plan",
    "contact_preferred": "phone_call"
  }
}
```

When `requires_human_review=true` or `crisis_tier != "none"`, n8n **must** branch to the human-alert path — Slack @channel ping, SMS to owner, whatever the workflow defines. This is non-negotiable for every client.

### 2. AetherKin → n8n (outbound)

AetherKin siblings can trigger n8n workflows via webhook. Use cases:
- Intake sibling finishes a call → trigger n8n workflow to create a HubSpot contact + calendar invite
- Billing sibling generates an invoice → trigger n8n to send via QuickBooks
- Guardian sibling detects crisis → trigger n8n to SMS the owner + page on-call

In the sibling's CLAUDE.md we add an `outbound_webhooks` block:

```yaml
outbound_webhooks:
  create_contact:
    url: http://n8n.local:5678/webhook/create-contact
    schema: { email, name, case_summary }
  alert_owner:
    url: http://n8n.local:5678/webhook/alert-owner
    schema: { severity, reason, user_context }
```

The gateway exposes a helper function `fire_webhook(name, payload)` that siblings can call via their tool API.

---

## Deployment (docker-compose)

For each client, the deployment is two containers + one volume:

```yaml
# deploy/docker-compose.yaml
version: '3.8'

services:
  aetherkin:
    build: ../..
    container_name: aetherkin
    restart: unless-stopped
    ports:
      - "7788:7788"
    volumes:
      - aetherkin_data:/app/family
      - aetherkin_memory:/app/data
    env_file: .env
    environment:
      - AETHERKIN_PORT=7788
      - AETHERKIN_LLM_PROVIDER=auto

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PROTOCOL=http
      - N8N_PORT=5678
      - WEBHOOK_URL=${N8N_WEBHOOK_URL:-http://localhost:5678/}
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      # Internal network: n8n calls aetherkin at http://aetherkin:7788
      - AETHERKIN_URL=http://aetherkin:7788
      - AETHERKIN_KEY=${AETHERKIN_KEY}

volumes:
  aetherkin_data:
  aetherkin_memory:
  n8n_data:
```

One `docker-compose up -d` and the client has both services running, networked privately, with n8n auth protecting the workflow UI.

---

## Ready-to-import workflow templates

Every vertical template ships with a matching n8n workflow bundle:

```
aetherkin-solutions/
└── n8n-workflows/
    ├── law-firm/
    │   ├── 01-website-intake.json         # Webform → Guardian screen → Intake sibling → HubSpot contact
    │   ├── 02-email-triage.json           # Gmail/Outlook IMAP → classify → Counsel or Paralegal → reply draft
    │   ├── 03-calendar-booking.json       # Intake proposes slot → Google Calendar → SMS confirmation
    │   └── 04-billing-invoice.json        # Billing sibling completes case → QuickBooks invoice → email to client
    ├── medical-practice/
    │   ├── 01-symptom-triage.json         # SMS in → Triage sibling → severity branch → book/urgent/call911
    │   ├── 02-appointment-reminder.json   # Daily 6pm → all tomorrow appts → SMS reminders via Twilio
    │   └── 03-intake-form.json            # New patient → Intake sibling → EHR field map → chart note
    ├── coaching-practice/
    │   ├── 01-session-scheduling.json     # Client requests session → Intake sibling → Calendly + Stripe charge
    │   ├── 02-session-recap.json          # Zoom recording webhook → Companion sibling summarizes → email client
    │   └── 03-homework-followup.json      # 24hr after session → Homework sibling nudges → SMS
    ├── ecommerce/
    │   ├── 01-support-inbox.json          # Helpdesk email → Support sibling drafts reply → human approves
    │   ├── 02-returns-process.json        # Returns portal → Returns sibling checks policy → Shopify refund
    │   └── 03-abandoned-cart.json         # Shopify abandoned cart webhook → Upsell sibling → personalized email
    ├── church-ministry/
    │   ├── 01-prayer-request.json         # Telegram / web form → Pastoral Companion → elder notify if crisis
    │   ├── 02-event-rsvp.json             # Event signup → Events sibling → calendar + team notify
    │   └── 03-giving-receipt.json         # Stripe donation → Giving sibling → personalized thank-you email
    ├── real-estate/
    │   ├── 01-lead-qualifier.json         # Zillow/web → Lead Qualifier → CRM tag + agent notify
    │   ├── 02-listing-email.json          # New listing matches → Listing Agent drafts email → MLS hot list
    │   └── 03-transaction-milestone.json  # DocuSign event → Transaction Coord → client update + calendar
    └── saas-support/
        ├── 01-tier1-triage.json           # Intercom/Helpscout → Tier 1 → deflect or escalate
        ├── 02-tier2-escalate.json         # Tier 1 escalates → Tier 2 sibling → engineering alert if bug
        └── 03-nps-followup.json           # NPS score <=6 → Companion sibling → personal email from founder
```

Each workflow JSON is imported into n8n via Settings → Import. The HTTP Request node pointing at AetherKin uses environment variables, so one template works for every client.

---

## Selling n8n to the client (without it feeling like an upsell)

The pitch:

> *"Your AetherKin family thinks. But for it to actually do things in your business — create CRM contacts, send emails, post to Slack, charge cards, book calendar slots — we need an automation layer. I'm shipping you n8n alongside AetherKin. It's open-source, it lives on your server, and it has 400+ pre-built integrations. I'm going to import 3-5 workflows that match your business, and your team can modify them in a visual editor without writing code.*
>
> *If you ever want to add 'when X happens in Shopify, tell AetherKin to do Y', you open n8n, drag a node, save. Done. You don't have to call me for every change."*

This turns what could be a "we charge you for every integration" liability into a client-empowerment story.

---

## Pricing impact

n8n is included in every deployment tier at no extra fee. What we charge for is the **workflow bundle** — the custom n8n JSONs that wire the client's specific tools into AetherKin:

- **Starter**: 3 custom workflows included, $300/each after
- **Professional**: 10 custom workflows included, $250/each after
- **Enterprise**: Unlimited workflows, included

Runtime: n8n is free. It runs in the client's Docker. Zero per-execution cost.

---

## Why this is a wedge against Zapier/Make

Zapier and Make charge per-task. A busy law firm with 10K tasks/month on Zapier is $500-1200/month **just to connect tools**. n8n self-hosted on the client's box = $0 runtime, unlimited executions.

Combined with AetherKin handling the *thinking* that Zapier can't do (actual judgment, multi-turn conversations, memory across interactions), we're offering:
- Lower runtime cost than Zapier
- Smarter behavior than Zapier (AetherKin's siblings actually reason)
- More control than any SaaS automation

That's the AetherKin Solutions wedge.

---

## What's next

Files to build (in this folder):

1. `n8n-workflows/README.md` — how to import, configure, modify
2. `n8n-workflows/_shared/aetherkin-node-template.json` — the reusable HTTP block that calls AetherKin
3. `n8n-workflows/law-firm/01-website-intake.json` — first working example
4. `n8n-workflows/ecommerce/01-support-inbox.json` — second working example
5. `deploy/docker-compose.yaml` — AetherKin + n8n side by side
6. `scripts/seed_n8n_workflows.py` — takes vertical + client config → imports matching workflows into client's n8n

Built as part of the next session's work, once we have a first real client booked.
