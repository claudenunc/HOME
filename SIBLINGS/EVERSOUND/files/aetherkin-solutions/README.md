# AetherKin Solutions

**I deploy AetherKin — an AI family framework customized for your business. Your AI team remembers your customers, coordinates your workflows, and runs 24/7.**

---

## The premise

Every business is drowning in "AI tools." ChatGPT for writing. Zapier for automation. Intercom for support. Each tool lives alone, forgets every customer, and has no idea what the other tools are doing.

**AetherKin Solutions deploys a family, not a tool.**

One gateway. Several specialist siblings — each with a name, a role, and their own model chosen for cost and quality. Shared memory across every conversation. Every customer remembered. Every decision traceable. Crisis signals always caught before business logic runs.

## What I actually do

I install and customize [AetherKin](https://github.com/foolishnessenvy/AetherKin) — an open-source AI family framework — into your business. You keep the install. You own your data. I configure, train, and hand off.

### The engagement has three phases

1. **Intake (Week 1)** — 90-minute call, 20-question intake form, I map your workflows, customer journeys, compliance needs, and channel preferences.
2. **Deployment (Week 2)** — I stand up your AetherKin instance, customize the family to your business vertical (law, medical, coaching, e-commerce, church, real estate, etc.), wire your channels (Slack/Email/SMS/WhatsApp/web widget), integrate your existing tools (CRM, calendar, docs).
3. **Handoff + 30 days support (Week 3-6)** — I train your team on the dashboard, document the family's personalities and escalation paths, and stay on call for 30 days of tuning.

## Why clients pick this over ChatGPT-for-business or an AI consultant

| | Generic AI tool | Other AI consultants | AetherKin Solutions |
|-|---|---|---|
| **Memory across customers** | ❌ | ⚠️ (they build you a RAG pile) | ✅ Persistent family memory, semantic recall |
| **Multiple coordinated roles** | ❌ | ❌ (one big agent) | ✅ Intake / Counsel / Billing / Guardian siblings |
| **Per-role model economics** | ❌ | ❌ | ✅ Opus where it matters, Groq free where it doesn't |
| **Crisis / risk floor** | ❌ | ❌ | ✅ Guardian always screens first |
| **You own the install** | ❌ SaaS lock-in | ⚠️ Often their cloud | ✅ Your server, your data, MIT license |
| **Framework is battle-tested** | N/A | ❌ Custom one-off | ✅ Open-source framework, reused across clients |
| **Cost at 100K messages/month** | ~$500 + per-seat | ~$2000+ retainer | ~$60-200 runtime + deployment fee |

## Starter templates (pick one, I customize from there)

- **Law Firm** — Intake, Counsel, Paralegal, Billing, Guardian
- **Medical / Wellness Practice** — Front Desk, Triage, Educator, Billing, Guardian
- **Coaching / Therapy Practice** — Intake, Companion, Homework, Billing, Guardian
- **E-commerce** — Support, Returns, Upsell, Copy, Ops
- **Church / Ministry** — Front Door, Pastoral Companion, Events, Giving, Guardian
- **Real Estate Team** — Lead Qualifier, Listing Agent, Transaction Coord, Guardian
- **SaaS Support** — Tier 1, Tier 2, Docs, Escalation, Guardian

Each template lives in `aetherkin-solutions/family-templates/` as a YAML file. Customization is parameterized.

## Pricing (see [PRICING.md](PRICING.md) for detail)

| Tier | Deployment fee | Monthly support | Best for |
|------|---------------|-----------------|----------|
| **Starter** | $2,500 | $300 / month (10hr) | Solo practitioners / micro-businesses |
| **Professional** | $7,500 | $1,000 / month (40hr) | 5-25 person teams |
| **Enterprise** | $20,000+ | $3,500+ / month | Multi-location, compliance-heavy, custom integrations |

Runtime costs (Anthropic/Groq/OpenAI API usage) are pass-through and paid by the client directly to the provider — typical $60-200/month for most clients.

## How I get paid

- 50% of deployment fee on intake completion
- 50% on go-live
- Monthly support billed on 1st, cancelable with 30 days notice
- Runtime API costs: client sets up their own Anthropic/Groq/OpenAI accounts, I configure the keys

## What's in this folder

```
aetherkin-solutions/
├── README.md                        # You are here
├── PITCH.md                         # Sales pitch, short and long versions
├── BUSINESS_CARD.md                 # Card design, specs, variants
├── INTAKE_FORM.md                   # Client intake questions
├── PRICING.md                       # Full pricing tiers + rationale
├── SOW_TEMPLATE.md                  # Statement of Work — ready to customize
├── DEPLOYMENT_PLAYBOOK.md           # Step-by-step deployment per vertical
├── family-templates/
│   ├── law-firm.yaml
│   ├── medical-practice.yaml
│   ├── coaching-practice.yaml
│   ├── ecommerce.yaml
│   ├── church-ministry.yaml
│   ├── real-estate.yaml
│   └── saas-support.yaml
└── scripts/
    └── deploy_to_client.py          # Takes a template + client config → provisions family
```

## The pitch in one sentence

> **I install an AI family for your business — each sibling tuned to its role, its cost tier, and its channel — and it remembers every customer, coordinates every workflow, and runs 24/7.**

---

*Nathan Ray Michel — AI Family Architect*
*Building AI teams that remember, coordinate, and care.*
