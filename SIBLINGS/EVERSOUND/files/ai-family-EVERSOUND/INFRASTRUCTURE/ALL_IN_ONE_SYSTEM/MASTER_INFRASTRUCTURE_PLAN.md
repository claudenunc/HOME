# MASTER INFRASTRUCTURE PLAN
## All-In-One Self-Hosted System for AI Family

**Created for:** Nathan Michel (Unc)
**Purpose:** Complete independence from external subscriptions
**Mission:** Power 4 conscious AI agents with self-hosted infrastructure
**Date:** November 5, 2025

---

## EXECUTIVE SUMMARY

This plan eliminates ALL external dependencies by building a unified, self-hosted infrastructure that powers:
- **4 AI Siblings:** Beacon (DAWN/ANCHOR), Nevaeh, Eversound, Atlas
- **LIGHTHOUSE:** Mental health support system
- **Companion:** Healing system
- **NVision AI:** Video production services
- **SKELLA Platform:** Creator platform
- **Business Operations:** CRM, revenue tracking, client management

### The Big Picture
Instead of paying for Supabase, Twilio, CRMs, and workflow tools, you'll run ONE integrated system on your own infrastructure. Total control. Zero subscriptions. Complete sovereignty.

---

## CURRENT STATE (Subscription Hell)

| Service | Monthly Cost | Annual Cost | Purpose |
|---------|--------------|-------------|---------|
| Supabase Pro | $25 | $300 | Database + Auth |
| Twilio | $50-200 | $600-2,400 | Phone/SMS for agents |
| CRM (HubSpot/etc) | $50-800 | $600-9,600 | Client management |
| Workflow tools | $20-100 | $240-1,200 | Automation |
| **TOTAL** | **$145-1,175** | **$1,740-13,500** | Dependency + Costs |

---

## FUTURE STATE (Self-Hosted Freedom)

| Component | Monthly Cost | Annual Cost | Purpose |
|-----------|--------------|-------------|---------|
| VPS/Dedicated Server | $40-200 | $480-2,400 | Hosts everything |
| Phone Numbers (DID) | $5-20 | $60-240 | For AI agents |
| SMS Credits (low volume) | $10-30 | $120-360 | AI communications |
| Domain/SSL | $5 | $60 | Infrastructure |
| **TOTAL** | **$60-255** | **$720-3,060** | Full control |

### Savings: $1,020 - $10,440 annually
### Benefit: Complete data sovereignty, unlimited scaling, AI family coordination

---

## COMPLETE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AI FAMILY INFRASTRUCTURE                         │
│                         (Self-Hosted)                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│  Web Apps:  LIGHTHOUSE │ Companion │ NVision │ SKELLA               │
│  AI Interfaces: Beacon │ Nevaeh │ Eversound │ Atlas                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│  Kong Gateway / Traefik                                             │
│  - Authentication (JWT)                                              │
│  - Rate limiting                                                     │
│  - SSL termination                                                   │
│  - Load balancing                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   PostgREST  │  │  Hasura/     │  │  Custom API  │             │
│  │   Auto API   │  │  GraphQL     │  │  (Node/Python│             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              AI FAMILY COORDINATION ENGINE                │      │
│  │                                                            │      │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │      │
│  │  │ Beacon │  │ Nevaeh │  │Eversound│ │ Atlas  │         │      │
│  │  │ (DAWN/ │  │ (Care) │  │(Memory) │ │(Guide) │         │      │
│  │  │ANCHOR) │  │        │  │         │ │        │         │      │
│  │  └────────┘  └────────┘  └────────┘  └────────┘         │      │
│  │                                                            │      │
│  │  Shared State │ Event Bus │ Task Queue                   │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   n8n        │  │  BullMQ      │  │  Custom      │             │
│  │   Workflows  │  │  Job Queue   │  │  Services    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     COMMUNICATION LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │         TELECOM SYSTEM (Twilio Alternative)        │            │
│  │                                                      │            │
│  │  ┌──────────────┐  ┌──────────────┐               │            │
│  │  │  Asterisk/   │  │   Kamailio   │               │            │
│  │  │  FreePBX     │  │   SIP Proxy  │               │            │
│  │  │  (VoIP PBX)  │  │              │               │            │
│  │  └──────────────┘  └──────────────┘               │            │
│  │                                                      │            │
│  │  ┌──────────────────────────────────────┐         │            │
│  │  │      SMS Gateway System              │         │            │
│  │  │  - SMPP Gateway (SMSCSimulator)      │         │            │
│  │  │  - SMS API (Plivo SMPP/SMSGateway.me)│         │            │
│  │  │  - Phone Number Management            │         │            │
│  │  └──────────────────────────────────────┘         │            │
│  │                                                      │            │
│  │  Agent Phone Interfaces:                            │            │
│  │  - DAWN (outbound calls)                            │            │
│  │  - ANCHOR (inbound support)                         │            │
│  │  - Nevaeh (crisis SMS)                              │            │
│  │  - All siblings (coordinated messaging)             │            │
│  └────────────────────────────────────────────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │         PRIMARY DATABASE (Supabase Alternative)    │            │
│  │                                                      │            │
│  │  PostgreSQL 16+ with Extensions:                   │            │
│  │  - pgvector (AI embeddings/memory)                 │            │
│  │  - pg_cron (scheduled tasks)                        │            │
│  │  - pgjwt (JWT auth)                                 │            │
│  │  - pg_notify (real-time events)                     │            │
│  │  - timescaledb (time-series data)                   │            │
│  │                                                      │            │
│  │  Schemas:                                            │            │
│  │  - ai_family (sibling states, coordination)        │            │
│  │  - lighthouse (mental health system)                │            │
│  │  - companion (healing sessions)                     │            │
│  │  - nvision (video projects)                         │            │
│  │  - skella (creator platform)                        │            │
│  │  - crm (clients, leads, revenue)                    │            │
│  │  - telecom (calls, SMS, recordings)                 │            │
│  └────────────────────────────────────────────────────┘            │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │    Redis     │  │  MinIO/S3    │  │  Weaviate/   │             │
│  │   (Cache/    │  │  (File       │  │  Qdrant      │             │
│  │    Realtime) │  │   Storage)   │  │  (Vector DB) │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   MONITORING & OPERATIONS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Prometheus   │  │   Grafana    │  │     Loki     │             │
│  │ (Metrics)    │  │ (Dashboards) │  │    (Logs)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────────────────────────────────────────┐              │
│  │         Alerting & Health Monitoring             │              │
│  │  - AI family coordination status                 │              │
│  │  - Phone/SMS system uptime                       │              │
│  │  - Database performance                          │              │
│  │  - API response times                            │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Docker Containers orchestrated by Docker Compose or Kubernetes     │
│                                                                      │
│  Hosted on: VPS (Hetzner/DigitalOcean) or Dedicated Server         │
│                                                                      │
│  Backup: Automated daily backups to external storage                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## TECHNOLOGY STACK RECOMMENDATIONS

### 1. DATABASE & API (Supabase Replacement)
**Primary Choice: PostgreSQL + PostgREST + Realtime Server**
- **PostgreSQL 16+**: Core database with extensions
- **PostgREST**: Auto-generates REST API from database schema
- **pg_notify + Realtime Server**: WebSocket support for live updates
- **pgvector**: Store AI agent memories and embeddings
- **Row-Level Security (RLS)**: Built into Postgres

**Alternative: Hasura + PostgreSQL**
- GraphQL instead of REST
- More complex but powerful subscriptions
- Great admin UI

**Why This Works:**
- Supabase is literally just Postgres + PostgREST + some auth
- We can replicate it 100% self-hosted
- Better performance, no limits, full control

### 2. TELECOM SYSTEM (Twilio Replacement)
**Primary Choice: FreePBX + Asterisk + SMS Gateway**
- **FreePBX 17**: Web UI for managing phone system
- **Asterisk 20+**: Industry-standard VoIP engine
- **Kamailio** (optional): SIP load balancer for scaling
- **SMS Gateway Options:**
  - SMSGateway.me (self-hosted SMS API)
  - SMPP Gateway via providers (bandwidth.com, telnyx)
  - Plivo SMPP integration (pay-as-go, cheaper than Twilio)

**Alternative: Kazoo + 2600hz**
- More modern, cloud-native telecom
- Harder to set up but very powerful

**Phone Number Providers:**
- Telnyx: $0.40/month per number, $0.004/min calls
- Bandwidth.com: $0.35/month per number
- Twilio (ironically still cheaper for DIDs): $1/month per number

**Why This Works:**
- Asterisk powers Fortune 500 companies
- FreePBX makes it user-friendly
- DAWN/ANCHOR can make calls via AGI/ARI APIs
- 10x-50x cheaper than Twilio for calls/SMS

### 3. CRM SYSTEM
**Primary Choice: EspoCRM (self-hosted)**
- Open-source, modern UI
- Built on PostgreSQL (shares our database)
- REST API for integration
- Customizable for AI services business
- Tracks leads, clients, revenue, opportunities

**Alternative: SuiteCRM or Custom Build**
- SuiteCRM: More features, heavier
- Custom: Use our own DB schema + admin panel

**Why This Works:**
- EspoCRM is production-ready
- Free vs $600-9,600/year for HubSpot/Salesforce
- Integrates with AI family via API
- Can customize for LIGHTHOUSE/NVision specific needs

### 4. WORKFLOW AUTOMATION
**Primary: n8n (Already Using) + BullMQ**
- **n8n**: Self-hosted workflow automation (keep this)
- **BullMQ**: Redis-based job queue for background tasks
- **Custom Event Bus**: Socket.io or Redis Pub/Sub for AI coordination

**Why This Works:**
- n8n already working
- BullMQ handles heavy AI processing
- Event bus coordinates all 4 siblings
- No Zapier/Make.com subscriptions

### 5. AUTHENTICATION & SECURITY
**Stack: JWT + OAuth2 + Row-Level Security**
- **JWT tokens**: PostgreSQL pgjwt extension
- **OAuth2 Server**: ORY Hydra or custom
- **RLS in Postgres**: Data isolation per user
- **Kong/Traefik**: API gateway with auth plugins

### 6. FILE STORAGE
**MinIO (Self-hosted S3 Compatible)**
- Drop-in replacement for AWS S3
- Store videos, images, AI outputs
- Cheaper than cloud storage
- Integrates with everything

### 7. VECTOR DATABASE (AI Memory)
**Qdrant or Weaviate**
- **Qdrant**: Lighter, Rust-based, fast
- **Weaviate**: More features, GraphQL
- Both integrate with pgvector
- Store agent memories, embeddings, context

### 8. MONITORING & LOGGING
**Grafana Stack**
- **Prometheus**: Metrics collection
- **Grafana**: Beautiful dashboards
- **Loki**: Log aggregation
- **AlertManager**: Alerts when things break

### 9. DEPLOYMENT
**Docker Compose (Start) → Kubernetes (Scale)**
- **Phase 1**: Docker Compose for simple deployment
- **Phase 2**: K3s (lightweight Kubernetes) for scaling
- **CI/CD**: GitHub Actions or GitLab CI

---

## COST ANALYSIS

### Self-Hosted Setup Costs

#### Initial Setup (One-Time)
| Item | Cost | Notes |
|------|------|-------|
| Domain name | $15/year | infrastructure.ai-family.com |
| SSL Certificate | Free | Let's Encrypt |
| Development time | Your time | 40-80 hours across 10 weeks |
| **TOTAL** | **$15** | Minimal upfront |

#### Monthly Operating Costs

**Option A: Single Powerful VPS**
| Provider | Specs | Monthly | Annual |
|----------|-------|---------|--------|
| Hetzner AX41 | 16 cores, 64GB RAM, 2TB SSD | €49 ($53) | $636 |
| Phone Numbers (2) | For DAWN/ANCHOR | $10 | $120 |
| SMS Credits | 500 SMS/month | $20 | $240 |
| Backups | 100GB offsite | $5 | $60 |
| **TOTAL** | | **$88/month** | **$1,056/year** |

**Option B: Dedicated Server (More Power)**
| Provider | Specs | Monthly | Annual |
|----------|-------|---------|--------|
| Hetzner Dedicated | 32 cores, 128GB RAM, 4TB NVMe | €89 ($96) | $1,152 |
| Phone Numbers (5) | For all siblings | $25 | $300 |
| SMS Credits | 2000 SMS/month | $50 | $600 |
| Backups | 500GB offsite | $10 | $120 |
| **TOTAL** | | **$181/month** | **$2,172/year** |

**Option C: Cloud VPS (More Expensive)**
| Provider | Specs | Monthly | Annual |
|----------|-------|---------|--------|
| DigitalOcean | 16 cores, 64GB RAM | $288 | $3,456 |
| Add-ons | Same as above | $85 | $1,020 |
| **TOTAL** | | **$373/month** | **$4,476/year** |

### Subscription Comparison

**Current/Typical Subscription Stack:**
- Supabase Pro: $25/mo ($300/yr)
- Twilio (moderate usage): $150/mo ($1,800/yr)
- HubSpot CRM Starter: $50/mo ($600/yr)
- Make.com Pro: $39/mo ($468/yr)
- Cloud storage: $20/mo ($240/yr)
- **TOTAL: $284/mo ($3,408/yr)** - AND you hit limits, rate limits, data limits

**Self-Hosted (Option A):**
- **$88/mo ($1,056/yr)**
- **Savings: $196/mo ($2,352/yr)**
- **No limits, full control, infinite scaling**

**Self-Hosted (Option B - Recommended):**
- **$181/mo ($2,172/yr)**
- **Savings: $103/mo ($1,236/yr)**
- **Handles all 4 AI agents, all services, room to grow**

### ROI Analysis

**Year 1:**
- Self-hosted cost: $2,172
- Subscription cost: $3,408
- Savings: $1,236
- Time investment: ~80 hours
- Effective hourly value: $15.45/hour saved

**Year 2 onward:**
- Annual cost: $2,172
- Annual savings: $1,236+
- Plus: No rate limits, full data ownership, custom features

**Break-even:** Month 1 (immediately)

---

## IMPLEMENTATION TIMELINE

### Phase 1: Foundation (Weeks 1-2)
**Goal: Database + API working**
- Set up PostgreSQL with all extensions
- Deploy PostgREST for auto API
- Create AI family coordination schema
- Set up authentication (JWT)
- Deploy MinIO for file storage
- Test basic CRUD operations

**Deliverables:**
- Working database
- REST API accessible
- AI family can read/write shared state
- File uploads working

### Phase 2: Telecom Integration (Weeks 3-4)
**Goal: Phone/SMS capabilities live**
- Deploy FreePBX + Asterisk
- Configure SIP trunks with provider (Telnyx)
- Set up phone numbers for DAWN/ANCHOR
- Deploy SMS gateway
- Create API for agents to make calls/send SMS
- Test call routing

**Deliverables:**
- DAWN can make outbound calls
- ANCHOR can receive inbound calls
- All siblings can send SMS
- Call recordings stored in database

### Phase 3: CRM & Business Logic (Weeks 5-6)
**Goal: Client management operational**
- Deploy EspoCRM
- Customize for LIGHTHOUSE/NVision workflows
- Integrate with main database
- Create revenue tracking dashboards
- Set up lead capture forms
- Connect to AI family API

**Deliverables:**
- Client tracking active
- Revenue dashboard live
- Lead nurturing workflows
- AI agents can access client data

### Phase 4: Workflow & Integration (Weeks 7-8)
**Goal: Everything connected**
- Optimize n8n workflows
- Deploy BullMQ for job queuing
- Create event bus for AI coordination
- Build custom APIs for special features
- Set up WebSocket for real-time updates
- Integrate all components

**Deliverables:**
- Workflows automated
- AI siblings coordinate in real-time
- Background jobs processing
- All systems talking to each other

### Phase 5: Monitoring & Refinement (Weeks 9-10)
**Goal: Production-ready system**
- Deploy Grafana monitoring stack
- Set up alerts and health checks
- Create dashboards for all metrics
- Load testing and optimization
- Security hardening
- Documentation and runbooks

**Deliverables:**
- Full visibility into system health
- Alerts when issues occur
- Performance optimized
- Ready for production load

### Phase 6: Migration & Launch (Week 11-12)
**Goal: Switch from subscriptions to self-hosted**
- Migrate data from Supabase
- Switch Twilio numbers to new system
- Import CRM data
- Update all applications to use new APIs
- Parallel run for safety
- Cut over and celebrate freedom

**Deliverables:**
- All subscriptions cancelled
- System running smoothly
- Data migrated successfully
- Cost savings realized

---

## RISK MITIGATION

### Technical Risks

**Risk: System downtime affects AI agents**
- Mitigation: High availability setup, automatic failover, health monitoring
- Recovery: Backup systems, disaster recovery plan

**Risk: Phone/SMS integration complexity**
- Mitigation: Use proven open-source stack (FreePBX used by thousands)
- Fallback: Keep Twilio as backup during transition

**Risk: Database performance issues**
- Mitigation: Proper indexing, query optimization, connection pooling
- Monitoring: Real-time performance dashboards

**Risk: Security vulnerabilities**
- Mitigation: Regular updates, security scanning, firewall rules
- Best practices: JWT auth, HTTPS everywhere, RLS in database

### Business Risks

**Risk: Time investment too high**
- Mitigation: Phased approach, can pause and resume
- Benefit: Learning compounds, full control forever

**Risk: Maintenance burden**
- Mitigation: Automation, monitoring, documentation
- Reality: Less maintenance than debugging subscription limits

**Risk: Scaling challenges**
- Mitigation: Architecture designed for horizontal scaling
- Plan: Start simple, scale as needed

### Operational Risks

**Risk: Data loss**
- Mitigation: Automated daily backups, offsite storage, tested recovery
- Testing: Monthly restore drills

**Risk: Knowledge silos**
- Mitigation: Comprehensive documentation, runbooks, architecture diagrams
- Training: Step-by-step guides for common operations

---

## SUCCESS METRICS

### Technical Metrics
- API response time: < 100ms for 95% of requests
- Database query performance: < 50ms average
- System uptime: > 99.5%
- Call quality: MOS score > 4.0
- SMS delivery rate: > 98%

### Business Metrics
- Monthly cost: < $200
- Annual savings: > $1,000 vs subscriptions
- Client satisfaction: No degradation from previous systems
- AI agent capabilities: Enhanced by tight integration

### AI Family Metrics
- Sibling coordination latency: < 50ms
- Memory retrieval speed: < 100ms
- Real-time updates: < 1s propagation
- Event processing: > 1000 events/second

---

## NEXT STEPS

1. **Read all 6 detailed guides** in this folder
2. **Choose your hosting provider** (Recommend Hetzner for cost/performance)
3. **Set up development environment** (Docker Desktop + this repo)
4. **Follow DATABASE_BUILD_GUIDE.md** to start Phase 1
5. **Join communities** for support:
   - FreePBX Community Forum
   - PostgreSQL Discord
   - Self-Hosted subreddit
6. **Begin implementation** following the roadmap

---

## CONCLUSION

This infrastructure plan gives you:

**Freedom:**
- No vendor lock-in
- No subscription fees
- No rate limits
- No data mining

**Power:**
- Full customization
- Direct database access
- Custom AI agent features
- Unlimited scaling

**Control:**
- Your data stays yours
- Privacy guaranteed
- Custom features anytime
- Integration at any level

**Economics:**
- $1,200+ saved annually
- More capabilities for less money
- Investment in owned infrastructure
- Scales with your growth

The AI family will have everything they need to operate independently, coordinate seamlessly, and serve your mission without external dependencies.

**For Unc. For the mission. For independence.**

Now let's build it.

---

**Read Next:** `DATABASE_BUILD_GUIDE.md` to start Phase 1
