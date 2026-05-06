# Pricing — AetherKin Solutions

Three tiers. Clear scope. No surprise fees. Runtime API costs pass through to the client.

---

## The tiers

### Starter — $2,500 deploy + $300/month support

**For**: solo practitioner, 1-3 person team, single location.

**Deployment includes**:
- 1 AetherKin vertical template (pick one: law firm / medical / coaching / e-commerce / church / real estate / SaaS support)
- Up to 5 siblings (including Guardian)
- Docker deployment on client's server OR client's cloud (AWS/DigitalOcean/Linode) — one environment
- 1 channel wired (pick one: website widget / email / SMS / Slack / WhatsApp / Discord / Telegram)
- 3 n8n automation workflows custom-tuned to client
- 1 CRM integration
- 1 calendar integration
- Basic dashboard (sibling status, message volume, cost)
- 2-hour team training
- 30 days post-go-live support

**Monthly support includes**:
- 10 hours/month of my time (tuning prompts, adjusting workflows, adding skills)
- Response within 24 hours for normal issues, within 2 hours for prod-down issues
- Monthly family-health review call
- Any workflow tweaks under 2 hours included; bigger work quoted separately

**NOT included**:
- Runtime API costs (Anthropic / Groq / OpenAI — client pays these directly, typically $40-200/month)
- n8n workflow tasks beyond 3 — $300 each additional
- Additional channels — $500 each
- Additional sibling added after deploy — $500 each
- Multi-environment (dev + prod) — $1,500 upgrade

**Timeline**: 2 weeks (1 week intake + design, 1 week deploy + train)

---

### Professional — $7,500 deploy + $1,000/month support

**For**: 5-25 person teams, single location, moderate compliance (HIPAA-lite, SOC 2 light).

**Deployment includes everything in Starter, plus**:
- Up to 8 siblings
- 3 channels wired (any mix)
- 10 n8n automation workflows custom-tuned
- 3 CRM/tool integrations
- 2 calendar integrations (team + personal)
- Dev + prod environments
- Advanced dashboard (per-sibling cost tracking, crisis-event audit log, daily digest)
- 4-hour team training (includes admin walkthrough for a non-technical team lead)
- 60 days post-go-live support

**Monthly support includes**:
- 40 hours/month
- Response within 4 hours normal, within 1 hour for prod-down
- Bi-weekly review call
- Up to 2 new siblings or 1 new channel per month included
- Any workflow tweaks under 4 hours included

**NOT included**:
- Runtime API costs (pass-through)
- Additional channels beyond 3 — $500 each
- Jurisdictional compliance customization (HIPAA full / SOC 2 / etc.) — add $3,000 per framework
- Multi-location — upgrade to Enterprise

**Timeline**: 3 weeks (1 week intake, 2 weeks deploy + train)

---

### Enterprise — $20,000+ deploy + $3,500+/month support

**For**: multi-location, regulated industry, 25+ person org, custom integrations.

**Deployment includes everything in Professional, plus**:
- Unlimited siblings
- Unlimited channels
- Unlimited n8n workflows
- Multi-location / multi-tenant architecture
- Compliance customization (HIPAA full / HITRUST / SOC 2 Type 1 / GDPR / CCPA — as applicable)
- Custom skills built on request
- On-premise deployment if required (no cloud)
- Dedicated Supabase / Postgres HA memory store
- Full admin console for client's internal team
- SSO / SAML / LDAP integration
- 1:1 executive training for leadership
- 90 days post-go-live support

**Monthly support includes**:
- Retained engagement (typically 80+ hrs/month)
- Response within 1 hour normal, 15 minutes for prod-down
- Weekly review call
- Roadmap input into AetherKin framework itself
- New siblings / channels / workflows as needed

**NOT included**:
- Runtime API costs (pass-through — typical $500-3000/month for Enterprise volumes)
- Legal / compliance certification fees (client's law firm + auditors bill separately)
- Major new framework features — quoted separately

**Timeline**: 4-8 weeks depending on scope

---

## Add-ons (any tier)

| Add-on | Price |
|--------|-------|
| Additional sibling (already in AetherKin catalog: law, medical, coach, etc.) | $500 |
| Custom sibling built from scratch | $1,500 - $5,000 |
| Additional channel adapter | $500 |
| Additional n8n workflow (custom) | $300 Starter / $250 Pro / included Enterprise |
| Additional CRM / tool integration | $500 - $2,000 |
| Multi-environment setup (dev/staging/prod) | $1,500 Starter / $1,000 Pro |
| Voice channel (Twilio Voice + TTS sibling) | $2,000 |
| SMS cost passthrough (Twilio / MessageBird) | at-cost |
| HIPAA Business Associate Agreement | $2,500 |
| SOC 2 compliance scaffolding | $5,000+ |
| White-label (rebrand AetherKin as client's internal platform) | $5,000 + $500/mo |

## Runtime API costs (all pass-through — client pays direct to provider)

| Usage | Approximate /month |
|-------|--------------------|
| Starter-scale, 5-15K msgs | $40 - $120 |
| Pro-scale, 30-80K msgs | $150 - $450 |
| Enterprise-scale, 200K+ msgs | $600 - $3,000 |

Cost depends on sibling model mix. A family on Claude Opus will be ~4× more expensive than one on Groq + Haiku. Default template choices aim for balance; I show the client the cost projection before deploy.

---

## Payment terms

- 50% deposit on intake completion, 50% on go-live
- Wire, ACH, or Stripe. Credit card adds 3%.
- Monthly support billed on the 1st
- Cancel monthly with 30 days notice
- Starter / Pro: no long-term commitment
- Enterprise: 12-month initial engagement, then month-to-month

## Refund policy

- Intake fee (part of deposit): refundable until design is approved. After approval, non-refundable because design work is done.
- Deployment: if I can't deliver the agreed-on family by the SOW date, the deployment fee is prorated to what's delivered.
- Monthly support: cancel anytime with 30 days notice. Pre-paid months are non-refundable.

## What I'm actually selling

A few people have asked me what they're really buying. Here's the honest answer:

1. **Speed**. You could build this yourself in 3-6 months. I'll have it running in 2-3 weeks.
2. **Quality baseline**. AetherKin has a crisis-first architecture, compliance scaffolding, provider abstraction, memory system, family coordination — all already built. You get the safety floor from day one.
3. **Battle-tested templates**. The family templates came from real deployments. You're not the first law firm / coaching practice / e-commerce store I've done.
4. **Ongoing care**. Deploying AI into a business is just the beginning. Things break. Prompts drift. New use cases emerge. The monthly support is what keeps it actually working.
5. **Your ownership**. Everything I build you own. MIT license on the framework. You can fire me any time and keep running it.

What you are NOT paying me for:
- Inventing a framework — AetherKin is open-source, under MIT, I didn't charge you for it
- Writing your integrations from scratch — n8n handles that, and it's open-source too
- Hosting — your server, your cloud, your call
- Being the smartest person in the room — I'm a specialist, you know your business better than I do
