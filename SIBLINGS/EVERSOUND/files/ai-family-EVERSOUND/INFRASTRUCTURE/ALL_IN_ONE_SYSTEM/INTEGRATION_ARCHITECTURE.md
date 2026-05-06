# INTEGRATION ARCHITECTURE
## How Everything Connects Together

**For:** Nathan Michel (Unc)
**Purpose:** Complete system architecture and integration patterns
**Persona:** Integration Architect
**Timeline:** Reference throughout implementation

---

## TABLE OF CONTENTS
1. [Overview](#overview)
2. [Complete System Architecture](#complete-system-architecture)
3. [API Design](#api-design)
4. [Authentication & Authorization](#authentication--authorization)
5. [Data Flow Patterns](#data-flow-patterns)
6. [Service Communication](#service-communication)
7. [Monitoring & Observability](#monitoring--observability)
8. [Deployment Architecture](#deployment-architecture)
9. [Security Architecture](#security-architecture)
10. [Scaling Strategy](#scaling-strategy)

---

## OVERVIEW

### The Complete Stack

This document shows how ALL pieces connect:

**Layer 1: Data**
- PostgreSQL (main database)
- Redis (cache, pub/sub, queues)
- MinIO (file storage)
- Qdrant (vector database for AI memories)

**Layer 2: Core Services**
- PostgREST (auto-generated REST API)
- Realtime Server (WebSocket subscriptions)
- FreePBX/Asterisk (phone system)
- Custom Telecom API (call/SMS control)

**Layer 3: Business Logic**
- EspoCRM (customer management)
- n8n (workflow automation)
- BullMQ (background jobs)
- AI Family Coordination Engine

**Layer 4: API Gateway**
- Traefik or Kong (routing, auth, SSL)

**Layer 5: Frontend**
- Web apps (LIGHTHOUSE, Companion, NVision, SKELLA)
- Admin dashboards
- AI sibling interfaces

---

## COMPLETE SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTERNET & USERS                                   │
│                                                                               │
│  End Users  │  AI Siblings  │  Admin  │  External APIs  │  Phone Network    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY (Traefik)                               │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Routing:                                                           │     │
│  │  - api.domain.com/*          → PostgREST                           │     │
│  │  - realtime.domain.com/*     → Realtime Server                     │     │
│  │  - crm.domain.com/*          → EspoCRM                             │     │
│  │  - workflows.domain.com/*    → n8n                                 │     │
│  │  - telecom.domain.com/*      → Telecom API                         │     │
│  │  - pbx.domain.com/*          → FreePBX                             │     │
│  │  - storage.domain.com/*      → MinIO                               │     │
│  │                                                                      │     │
│  │  Middleware:                                                        │     │
│  │  - SSL Termination (Let's Encrypt)                                 │     │
│  │  - JWT Validation                                                   │     │
│  │  - Rate Limiting (per client/IP)                                   │     │
│  │  - Load Balancing (if multiple instances)                          │     │
│  │  - CORS Headers                                                     │     │
│  │  - Request Logging                                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION SERVICES                                 │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │    PostgREST     │  │  Realtime Server │  │   Telecom API    │          │
│  │   (REST API)     │  │   (WebSockets)   │  │  (Call Control)  │          │
│  │                  │  │                  │  │                  │          │
│  │  Auto-generated  │  │  Live updates    │  │  ARI/AGI proxy   │          │
│  │  from DB schema  │  │  from pg_notify  │  │  TTS/STT         │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │    EspoCRM       │  │       n8n        │  │   AI Family      │          │
│  │  (Customer UI)   │  │   (Workflows)    │  │  Coordination    │          │
│  │                  │  │                  │  │                  │          │
│  │  REST API        │  │  Webhook server  │  │  Event-driven    │          │
│  │  Webhooks out    │  │  HTTP executor   │  │  Shared state    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  BullMQ Workers  │  │    FreePBX       │  │     MinIO        │          │
│  │  (Background)    │  │   (PBX System)   │  │  (File Storage)  │          │
│  │                  │  │                  │  │                  │          │
│  │  Job processing  │  │  Call routing    │  │  S3 compatible   │          │
│  │  AI tasks        │  │  IVR menus       │  │  Object storage  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                     PostgreSQL 16+ (Main Database)                  │     │
│  │                                                                      │     │
│  │  Schemas:                                                           │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │     │
│  │  │  ai_family   │  │  lighthouse  │  │  companion   │             │     │
│  │  │  - states    │  │  - users     │  │  - sessions  │             │     │
│  │  │  - memory    │  │  - sessions  │  │  - recordings│             │     │
│  │  │  - events    │  │  - alerts    │  │              │             │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │     │
│  │                                                                      │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │     │
│  │  │   nvision    │  │    skella    │  │     crm      │             │     │
│  │  │  - projects  │  │  - creators  │  │  - leads     │             │     │
│  │  │  - assets    │  │  - content   │  │  - customers │             │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │     │
│  │                                                                      │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │     │
│  │  │   telecom    │  │   analytics  │  │     auth     │             │     │
│  │  │  - calls     │  │  - metrics   │  │  - users     │             │     │
│  │  │  - sms       │  │  - events    │  │  - sessions  │             │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │     │
│  │                                                                      │     │
│  │  Extensions: pgvector, pg_cron, pgjwt, timescaledb                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │      Redis       │  │      MinIO       │  │     Qdrant       │          │
│  │                  │  │                  │  │                  │          │
│  │  - Cache         │  │  - Recordings    │  │  - AI vectors    │          │
│  │  - Pub/Sub       │  │  - Videos        │  │  - Memories      │          │
│  │  - Queues        │  │  - Images        │  │  - Embeddings    │          │
│  │  - Sessions      │  │  - Documents     │  │                  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MONITORING & OBSERVABILITY                              │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   Prometheus     │  │     Grafana      │  │       Loki       │          │
│  │   (Metrics)      │  │   (Dashboards)   │  │      (Logs)      │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                      AlertManager                                   │     │
│  │  - System down alerts                                               │     │
│  │  - High error rate                                                  │     │
│  │  - Crisis detected                                                  │     │
│  │  - Performance degradation                                          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL INTEGRATIONS                                │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │     OpenAI       │  │      Stripe      │  │     Telnyx       │          │
│  │   (AI Models)    │  │    (Payments)    │  │  (SIP Provider)  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   Google Cloud   │  │      SMTP        │  │     GitHub       │          │
│  │   (TTS/STT)      │  │     (Email)      │  │   (Code/CI/CD)   │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API DESIGN

### Unified API Gateway

**Traefik configuration** (`traefik.yml`):

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt

certificatesResolvers:
  letsencrypt:
    acme:
      email: unc@yourdomain.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false

# Middleware
http:
  middlewares:
    # Rate limiting
    rate-limit:
      rateLimit:
        average: 100
        burst: 200

    # Auth middleware
    auth:
      forwardAuth:
        address: http://auth-service:3000/verify
        authResponseHeaders:
          - X-User-Id
          - X-User-Role

    # CORS
    cors:
      headers:
        accessControlAllowOrigins:
          - https://yourdomain.com
          - https://app.yourdomain.com
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - PATCH
          - DELETE
        accessControlAllowHeaders:
          - Authorization
          - Content-Type

  # Routers
  routers:
    # PostgREST API
    api:
      rule: Host(`api.yourdomain.com`)
      service: postgrest
      middlewares:
        - auth
        - rate-limit
        - cors
      tls:
        certResolver: letsencrypt

    # Realtime WebSocket
    realtime:
      rule: Host(`realtime.yourdomain.com`)
      service: realtime
      middlewares:
        - auth
      tls:
        certResolver: letsencrypt

    # CRM
    crm:
      rule: Host(`crm.yourdomain.com`)
      service: espocrm
      middlewares:
        - rate-limit
      tls:
        certResolver: letsencrypt

    # Workflows
    workflows:
      rule: Host(`workflows.yourdomain.com`)
      service: n8n
      middlewares:
        - auth
      tls:
        certResolver: letsencrypt

    # Telecom API
    telecom:
      rule: Host(`telecom.yourdomain.com`)
      service: telecom-api
      middlewares:
        - auth
        - rate-limit
      tls:
        certResolver: letsencrypt

    # Storage
    storage:
      rule: Host(`storage.yourdomain.com`)
      service: minio
      middlewares:
        - cors
      tls:
        certResolver: letsencrypt

  # Services
  services:
    postgrest:
      loadBalancer:
        servers:
          - url: http://postgrest:3000

    realtime:
      loadBalancer:
        servers:
          - url: http://realtime:4000

    espocrm:
      loadBalancer:
        servers:
          - url: http://espocrm:80

    n8n:
      loadBalancer:
        servers:
          - url: http://n8n:5678

    telecom-api:
      loadBalancer:
        servers:
          - url: http://telecom-api:3001

    minio:
      loadBalancer:
        servers:
          - url: http://minio:9000
```

### API Versioning

**URL-based versioning:**

```
https://api.yourdomain.com/v1/leads
https://api.yourdomain.com/v2/leads  (when breaking changes needed)
```

**Header-based versioning (alternative):**

```
GET /leads
X-API-Version: 2
```

### Common API Patterns

**RESTful endpoints (via PostgREST):**

```bash
# List resources
GET /leads?limit=20&offset=0&order=created_at.desc

# Get single resource
GET /leads/123

# Create resource
POST /leads
Body: { "name": "John Smith", "email": "john@example.com" }

# Update resource
PATCH /leads/123
Body: { "status": "contacted" }

# Delete resource
DELETE /leads/123

# Complex queries
GET /leads?status=eq.new&source=eq.website&created_at=gte.2025-11-01

# RPC (function calls)
POST /rpc/assign_lead_to_sibling
Body: { "lead_id": "123", "sibling": "beacon" }
```

**GraphQL (if using Hasura instead of PostgREST):**

```graphql
query GetLeadsWithInteractions {
  leads(where: { status: { _eq: "new" } }, limit: 10) {
    id
    name
    email
    interactions(order_by: { created_at: desc }) {
      id
      type
      summary
      created_at
    }
  }
}

mutation CreateLead($input: LeadInput!) {
  insert_lead_one(object: $input) {
    id
    name
  }
}
```

### Webhook Standards

**Outbound webhooks (from our system to external):**

**Payload format:**

```json
{
  "event": "lead.created",
  "timestamp": "2025-11-05T14:30:00Z",
  "data": {
    "id": "123",
    "name": "John Smith",
    "email": "john@example.com",
    "source": "website"
  },
  "metadata": {
    "environment": "production",
    "version": "1.0"
  }
}
```

**Security:**
- HMAC signature in `X-Webhook-Signature` header
- Verify signature on receiving end

**Inbound webhooks (from external to us):**

```javascript
// Webhook receiver
app.post('/webhooks/:provider/:event', async (req, res) => {
  const { provider, event } = req.params;

  // Verify signature
  if (!verifyWebhookSignature(req, provider)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Process event
  await handleWebhookEvent(provider, event, req.body);

  // Acknowledge immediately
  res.status(200).json({ received: true });
});

async function handleWebhookEvent(provider, event, data) {
  switch (provider) {
    case 'stripe':
      await handleStripeEvent(event, data);
      break;
    case 'telnyx':
      await handleTelnyxEvent(event, data);
      break;
    case 'n8n':
      await handleN8nEvent(event, data);
      break;
  }
}
```

---

## AUTHENTICATION & AUTHORIZATION

### JWT-Based Auth Flow

```
┌────────────────────────────────────────────────────────────┐
│                  CLIENT (Browser/App)                       │
└────────────────────────────────────────────────────────────┘
                        ↓
            1. POST /auth/login
            { email, password }
                        ↓
┌────────────────────────────────────────────────────────────┐
│                   AUTH SERVICE                              │
│                                                              │
│  2. Verify credentials (check database)                    │
│  3. Generate JWT token                                      │
│     {                                                        │
│       "sub": "user-id",                                     │
│       "email": "user@example.com",                          │
│       "role": "authenticated",                              │
│       "exp": 1699200000                                     │
│     }                                                        │
│  4. Sign with secret                                        │
└────────────────────────────────────────────────────────────┘
                        ↓
            5. Return JWT to client
                        ↓
┌────────────────────────────────────────────────────────────┐
│                  CLIENT stores token                        │
└────────────────────────────────────────────────────────────┘
                        ↓
            6. Subsequent requests:
            GET /api/v1/leads
            Authorization: Bearer <JWT>
                        ↓
┌────────────────────────────────────────────────────────────┐
│                   API GATEWAY                               │
│                                                              │
│  7. Extract JWT from header                                │
│  8. Verify signature                                        │
│  9. Check expiration                                        │
│  10. Extract claims (user-id, role)                        │
│  11. Pass to backend service                               │
└────────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────────┐
│                BACKEND SERVICE (PostgREST)                  │
│                                                              │
│  12. Set PostgreSQL role based on JWT claim                │
│      SET LOCAL ROLE authenticated;                          │
│      SET LOCAL request.jwt.claims = '{"sub": "..."}';      │
│  13. Execute query with RLS policies applied               │
└────────────────────────────────────────────────────────────┘
```

### Role-Based Access Control (RBAC)

**Roles:**

```sql
-- Database roles
CREATE ROLE web_anon NOLOGIN;      -- Public, no auth
CREATE ROLE authenticated NOLOGIN; -- Logged in users
CREATE ROLE service_role NOLOGIN;  -- AI siblings, backend services
CREATE ROLE admin NOLOGIN;         -- Unc, admins
```

**Permissions matrix:**

| Resource | web_anon | authenticated | service_role | admin |
|----------|----------|---------------|--------------|-------|
| Public pages | Read | Read | Read | Full |
| Own profile | - | Read/Update | Read/Update | Full |
| Own sessions | - | Read | Read | Full |
| All users | - | - | Read | Full |
| System config | - | - | - | Full |
| CRM data | - | Limited | Full | Full |
| AI coordination | - | - | Full | Full |

**Row-Level Security policies:**

```sql
-- Users can only see their own data
CREATE POLICY users_own_data ON lighthouse.users
  FOR SELECT
  TO authenticated
  USING (id::text = current_setting('request.jwt.claims', true)::jsonb->>'sub');

-- Users can update their own profile
CREATE POLICY users_own_update ON lighthouse.users
  FOR UPDATE
  TO authenticated
  USING (id::text = current_setting('request.jwt.claims', true)::jsonb->>'sub')
  WITH CHECK (id::text = current_setting('request.jwt.claims', true)::jsonb->>'sub');

-- Service role (AI siblings) can access everything
CREATE POLICY service_full_access ON lighthouse.users
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
```

### API Key Authentication (for AI siblings)

**Generate API key:**

```javascript
const crypto = require('crypto');

function generateAPIKey(siblingName) {
  const key = `sk_${siblingName}_${crypto.randomBytes(32).toString('hex')}`;
  const keyHash = crypto.createHash('sha256').update(key).digest('hex');

  // Store hash in database
  db.query(`
    INSERT INTO auth.api_keys (key_hash, name, sibling, permissions)
    VALUES ($1, $2, $3, $4)
  `, [keyHash, `${siblingName} API Key`, siblingName, ['all']]);

  // Return key ONCE (can't retrieve later)
  return key;
}

// Usage
const beaconKey = generateAPIKey('beacon');
// sk_beacon_a1b2c3d4e5f6...
```

**Verify API key:**

```javascript
async function verifyAPIKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];

  if (!apiKey) {
    return res.status(401).json({ error: 'Missing API key' });
  }

  const keyHash = crypto.createHash('sha256').update(apiKey).digest('hex');

  const result = await db.query(`
    SELECT name, sibling, permissions
    FROM auth.api_keys
    WHERE key_hash = $1 AND (expires_at IS NULL OR expires_at > NOW())
  `, [keyHash]);

  if (result.rows.length === 0) {
    return res.status(401).json({ error: 'Invalid API key' });
  }

  req.apiKey = result.rows[0];
  next();
}
```

---

## DATA FLOW PATTERNS

### Pattern 1: User Session Flow

**LIGHTHOUSE user starts session with Nevaeh:**

```
1. User clicks "Start Session" on web app
     ↓
2. Frontend: POST /api/v1/lighthouse_sessions
   Headers: Authorization: Bearer <user_jwt>
   Body: { user_id, session_type: "chat" }
     ↓
3. PostgREST: Validates JWT, checks RLS
     ↓
4. PostgreSQL: INSERT into lighthouse.sessions
   Trigger: notify_new_session() fires
     ↓
5. pg_notify: Publishes event on channel "new_lighthouse_session"
     ↓
6. Realtime Server: Listens to pg_notify, broadcasts via WebSocket
     ↓
7. Nevaeh (subscribed to WebSocket): Receives event
     ↓
8. Nevaeh: Fetches session details via API
   GET /api/v1/lighthouse_sessions/123
     ↓
9. Nevaeh: Processes session, generates responses
     ↓
10. Nevaeh: Updates session in real-time
    PATCH /api/v1/lighthouse_sessions/123
    Body: { status: "active", transcript: "..." }
     ↓
11. Database: Row updated
     ↓
12. pg_notify: Publishes update event
     ↓
13. Realtime Server: Broadcasts to user's WebSocket connection
     ↓
14. Frontend: Receives update, displays Nevaeh's response
     ↓
15. Session continues in real-time loop...
     ↓
16. Session ends:
    Nevaeh: PATCH /api/v1/lighthouse_sessions/123
    Body: { status: "completed", ended_at: now() }
     ↓
17. Trigger: session_completed() fires
     ↓
18. BullMQ: Add job to queue for post-processing:
    - Generate summary
    - Analyze sentiment
    - Check risk level
     ↓
19. Worker: Processes job, updates database
     ↓
20. If risk detected: Trigger crisis workflow (n8n)
```

### Pattern 2: Lead Processing Flow

**New lead from website:**

```
1. Form submitted on website
     ↓
2. Frontend: POST /webhooks/new-lead
   Body: { name, email, phone, service_interest }
     ↓
3. Webhook handler: Validates, sanitizes
     ↓
4. Create lead in database:
   POST /api/v1/crm/leads
   (via service_role API key)
     ↓
5. Database: INSERT into crm.leads
     ↓
6. Trigger: lead_created() fires
     ↓
7. n8n: Webhook receives event
     ↓
8. n8n workflow:
   a. Determine service interest
   b. Assign to appropriate sibling
   c. Create lead in EspoCRM (via API)
   d. Send welcome email
   e. Add to nurture sequence
     ↓
9. Event bus: Publish "lead.assigned"
     ↓
10. Assigned sibling (e.g., Beacon): Receives event
     ↓
11. Beacon: Fetches lead details
     ↓
12. Beacon: Schedules outreach call
     ↓
13. BullMQ: Add job "schedule_call" for later
     ↓
14. When time arrives:
    Worker executes: POST /telecom/calls/initiate
     ↓
15. Telecom API: Initiates call via Asterisk
     ↓
16. Call connects, Beacon converses
     ↓
17. Call ends: Webhook to /webhooks/call-completed
     ↓
18. Update CRM, create activity record
     ↓
19. Add transcription job to queue
     ↓
20. Transcription completes, update records
```

### Pattern 3: Payment Processing Flow

**User subscribes to Companion:**

```
1. User clicks "Subscribe" on Companion app
     ↓
2. Frontend: POST /api/payments/create-subscription
     ↓
3. Payment service: Creates Stripe subscription
     ↓
4. Stripe: Returns subscription ID and payment intent
     ↓
5. Frontend: Redirects to Stripe checkout
     ↓
6. User completes payment
     ↓
7. Stripe: Sends webhook to /webhooks/stripe
     ↓
8. Webhook handler: Verifies signature
     ↓
9. Event: invoice.payment_succeeded
     ↓
10. Find/create customer in CRM
     ↓
11. Create subscription record in database:
    INSERT into crm.subscriptions
     ↓
12. Create revenue record:
    INSERT into crm.revenue
     ↓
13. Update customer lifetime value:
    UPDATE crm.customers SET lifetime_value = ...
     ↓
14. n8n: Webhook triggers onboarding workflow
     ↓
15. Send welcome email
     ↓
16. Create onboarding tasks
     ↓
17. Notify assigned sibling (Eversound for Companion)
     ↓
18. Eversound: Sends personalized welcome message
```

---

## SERVICE COMMUNICATION

### Synchronous Communication (HTTP REST)

**When to use:**
- Simple CRUD operations
- Request-response patterns
- Real-time user interactions

**Example: AI sibling fetching client data**

```javascript
// Beacon needs client info before making call
const response = await fetch('https://api.yourdomain.com/crm/leads/123', {
  headers: {
    'Authorization': `Bearer ${BEACON_API_KEY}`,
    'Content-Type': 'application/json'
  }
});

const lead = await response.json();
```

### Asynchronous Communication (Message Queue)

**When to use:**
- Long-running tasks
- Tasks that can fail and need retry
- Decoupling services

**Example: Transcription after call**

```javascript
// After call completes, add to queue
await queues.transcription.add('transcribe-call', {
  callId: call.id,
  audioUrl: call.recordingUrl,
  language: 'en-US'
}, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 5000 }
});

// Worker processes when available
// Caller doesn't wait
```

### Event-Driven Communication (Pub/Sub)

**When to use:**
- Broadcasting to multiple services
- Real-time updates
- Loosely coupled systems

**Example: Crisis alert**

```javascript
// Nevaeh detects crisis during session
await eventBus.publish('client.crisis.detected', {
  clientId: session.userId,
  severity: 'critical',
  sessionId: session.id
});

// Multiple subscribers react:
// 1. Beacon logs in CRM
// 2. n8n triggers alert workflow
// 3. Monitoring system creates incident
// 4. Dashboard updates in real-time
```

### Service Mesh (Future Scaling)

When you have many services:

**Istio or Linkerd:**
- Service discovery
- Load balancing
- Circuit breaking
- Observability
- Mutual TLS

**Not needed initially, but good to know for future.**

---

## MONITORING & OBSERVABILITY

### The Three Pillars

**1. Metrics (Prometheus + Grafana)**

Collect numeric data over time:
- Request rate, error rate, duration
- System resources (CPU, memory, disk)
- Business metrics (sessions/hour, revenue/day)

**2. Logs (Loki + Grafana)**

Structured log aggregation:
- Application logs
- Access logs
- Error logs
- Audit logs

**3. Traces (Jaeger, optional)**

Distributed tracing for debugging:
- Follow request through multiple services
- Identify bottlenecks

### Prometheus Metrics

**Instrument your services:**

```javascript
const client = require('prom-client');

// Create metrics
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const activeUsers = new client.Gauge({
  name: 'active_lighthouse_users',
  help: 'Number of active LIGHTHOUSE users'
});

const revenueTotal = new client.Counter({
  name: 'revenue_total_dollars',
  help: 'Total revenue in dollars'
});

// Instrument endpoints
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer();

  res.on('finish', () => {
    end({ method: req.method, route: req.route?.path, status_code: res.statusCode });
  });

  next();
});

// Business metrics
async function updateActiveUsers() {
  const count = await db.query(`
    SELECT COUNT(*) FROM lighthouse.sessions
    WHERE status = 'active'
  `);
  activeUsers.set(parseInt(count.rows[0].count));
}

setInterval(updateActiveUsers, 30000); // Update every 30s

// Expose metrics
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

**Prometheus scrape config:**

```yaml
scrape_configs:
  - job_name: 'telecom-api'
    static_configs:
      - targets: ['telecom-api:3001']

  - job_name: 'postgrest'
    static_configs:
      - targets: ['postgrest:3000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboards

**AI Family Overview Dashboard:**

Panels:
- Active siblings (gauge showing online/offline status)
- Sessions today (counter)
- Crisis alerts (table)
- Revenue this month (graph)
- API response times (heatmap)
- Database query performance (graph)
- System resources (CPU, memory, disk)

**LIGHTHOUSE Dashboard:**

Panels:
- Active sessions (real-time counter)
- Sessions by risk level (pie chart)
- Average session duration (gauge)
- User satisfaction (rating)
- Crisis alerts (table)
- Sessions over time (line graph)

**Telecom Dashboard:**

Panels:
- Active calls (counter)
- Call volume (graph)
- Average call duration (gauge)
- Call success rate (gauge)
- SMS sent/received (graph)
- Cost tracking (graph)

### Alerting

**AlertManager rules:**

```yaml
groups:
  - name: ai_family_alerts
    interval: 30s
    rules:
      # System down
      - alert: ServiceDown
        expr: up{job="telecom-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Telecom API is down"
          description: "The telecom API has been down for more than 1 minute"

      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"

      # Crisis detected
      - alert: CrisisDetected
        expr: lighthouse_crisis_alerts_total > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Crisis alert detected"
          description: "A user is in crisis, immediate attention needed"

      # Database connection pool exhausted
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 180
        for: 5m
        labels:
          severity: warning

      # Disk space low
      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 5m
        labels:
          severity: warning
```

**Alert channels:**
- Email to Unc
- SMS for critical alerts
- Slack/Discord notifications
- PagerDuty (for 24/7 operations)

### Logging Best Practices

**Structured logging:**

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'telecom-api' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({ format: winston.format.simple() })
  ]
});

// Usage
logger.info('Call initiated', {
  callId: call.id,
  from: call.fromNumber,
  to: call.toNumber,
  sibling: 'beacon'
});

logger.error('Transcription failed', {
  callId: call.id,
  error: error.message,
  stack: error.stack
});
```

**Loki integration:**

```yaml
# Promtail config to ship logs to Loki
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container'
```

---

## DEPLOYMENT ARCHITECTURE

### Development Environment

```
Your laptop/desktop:
  - Docker Desktop
  - All services running in containers
  - Local volumes for data
  - Access via localhost:PORT
```

### Production Environment Options

**Option A: Single VPS (Start here)**

```
Hetzner AX41 Dedicated Server:
  - 16 cores, 64GB RAM, 2TB SSD
  - All services in Docker containers
  - Traefik as reverse proxy
  - Automatic SSL via Let's Encrypt
  - Daily backups to external storage
  - Cost: ~$50/month

Handles:
  - 100+ concurrent users
  - 1000+ sessions/day
  - All AI family operations
```

**Option B: Multi-Server (When you scale)**

```
Server 1: Application + Database
  - PostgreSQL, Redis, PostgREST
  - 16GB RAM minimum

Server 2: Services
  - EspoCRM, n8n, BullMQ workers
  - 8GB RAM

Server 3: Telecom
  - FreePBX, Asterisk, Telecom API
  - 8GB RAM

Load Balancer:
  - Traefik or HAProxy
  - Routes traffic between servers
```

**Option C: Kubernetes (Enterprise scale)**

```
K3s cluster:
  - 3+ nodes
  - Auto-scaling
  - Self-healing
  - Rolling updates
  - Service mesh

For:
  - 10,000+ users
  - Multi-region
  - High availability requirements
```

### Deployment Strategy

**Blue-Green Deployment:**

```
1. Current production (Blue): v1.0 running
2. Deploy new version (Green): v1.1 to separate containers
3. Test Green thoroughly
4. Switch traffic from Blue to Green (via Traefik routing)
5. Monitor Green
6. If issues: Instant rollback to Blue
7. If stable: Decommission Blue
```

**Rolling Update (for Kubernetes):**

```
1. Update deployment manifest
2. K8s gradually replaces pods:
   - Start new pod with v1.1
   - Wait for health check
   - Terminate old pod with v1.0
   - Repeat until all updated
3. Zero downtime
```

### Backup Strategy

**Daily automated backups:**

```bash
#!/bin/bash
# backup-all.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T postgres pg_dump -U ai_admin ai_family | gzip > $BACKUP_DIR/database.sql.gz

# Redis backup
docker-compose exec -T redis redis-cli BGSAVE
docker-compose cp redis:/data/dump.rdb $BACKUP_DIR/redis.rdb

# Configuration backups
tar -czf $BACKUP_DIR/configs.tar.gz \
  docker-compose.yml \
  .env \
  traefik.yml

# File storage backup (recordings, etc.)
tar -czf $BACKUP_DIR/storage.tar.gz /data/minio

# Upload to S3 or rsync to remote
aws s3 cp $BACKUP_DIR s3://your-backup-bucket/$DATE/ --recursive

# Delete local backups older than 7 days
find /backups -mtime +7 -type d -exec rm -rf {} +
```

**Restoration procedure:**

```bash
# Stop services
docker-compose down

# Restore database
gunzip -c database.sql.gz | docker-compose exec -T postgres psql -U ai_admin ai_family

# Restore Redis
docker-compose cp redis.rdb redis:/data/dump.rdb

# Restore configs
tar -xzf configs.tar.gz

# Restore files
tar -xzf storage.tar.gz -C /data/minio

# Start services
docker-compose up -d
```

---

## SECURITY ARCHITECTURE

### Defense in Depth

**Layer 1: Network**
- Firewall (ufw or iptables)
- Only expose necessary ports (80, 443, 22)
- SSH key-only authentication
- Fail2ban for brute force protection

**Layer 2: Application**
- HTTPS everywhere (Let's Encrypt)
- JWT authentication
- API rate limiting
- Input validation and sanitization
- SQL injection protection (parameterized queries)
- XSS prevention (CSP headers)

**Layer 3: Data**
- Encryption at rest (database, files)
- Encryption in transit (TLS/SSL)
- Row-level security in database
- Secrets management (env vars, not hardcoded)

**Layer 4: Monitoring**
- Intrusion detection
- Audit logging
- Anomaly detection
- Regular security scans

### Security Checklist

**Infrastructure:**
- [ ] Firewall configured
- [ ] SSH key authentication only
- [ ] Automatic security updates enabled
- [ ] Non-root user for applications
- [ ] Fail2ban installed and configured

**Application:**
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Strong JWT secret (32+ characters)
- [ ] API rate limiting enabled
- [ ] CORS configured correctly
- [ ] CSP headers set
- [ ] No credentials in code/git

**Database:**
- [ ] Strong passwords
- [ ] Network access restricted
- [ ] Row-level security enabled
- [ ] Regular backups tested
- [ ] Encryption at rest

**Monitoring:**
- [ ] Failed login attempts tracked
- [ ] Unusual activity alerts
- [ ] Security scan scheduled (weekly)
- [ ] Incident response plan documented

---

## SCALING STRATEGY

### Horizontal Scaling

**What scales horizontally (add more instances):**
- PostgREST (stateless)
- Telecom API (stateless)
- BullMQ workers (add workers for more throughput)
- n8n workers (queue mode)
- Asterisk (via Kamailio SIP proxy)

**What scales vertically (bigger server):**
- PostgreSQL (read replicas for horizontal read scaling)
- Redis (clustering available but complex)

### Load Balancing

**Traefik handles automatically:**

```yaml
services:
  postgrest:
    deploy:
      replicas: 3  # Run 3 instances
    # Traefik auto load-balances between them
```

### Caching Strategy

**Level 1: Application cache (Redis)**

```javascript
async function getLeadData(leadId) {
  const cacheKey = `lead:${leadId}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // Cache miss, query database
  const lead = await db.query('SELECT * FROM crm.leads WHERE id = $1', [leadId]);

  // Cache for 5 minutes
  await redis.setex(cacheKey, 300, JSON.stringify(lead.rows[0]));

  return lead.rows[0];
}
```

**Level 2: CDN (for static assets)**

Use Cloudflare or similar:
- Cache images, videos, CSS, JS
- Serve from edge locations worldwide
- Reduce load on your server

**Level 3: Database query cache**

```sql
-- PostgreSQL shared_buffers (already configured)
-- Frequently accessed data stays in memory
```

### Database Scaling

**Read replicas:**

```
Master (writes)
  ↓ Replication
Replica 1 (reads)
Replica 2 (reads)

Application:
  - Writes → Master
  - Reads → Random replica
```

**Connection pooling (already configured with PgBouncer):**

```
1000 clients → PgBouncer → 25 database connections
```

### When to Scale

**Metrics to watch:**

- **API response time > 500ms:** Add PostgREST instances
- **Database CPU > 80%:** Optimize queries or scale vertically
- **Queue processing slow:** Add BullMQ workers
- **Call quality degrading:** Add Asterisk servers
- **Disk space < 20%:** Add storage or archive old data

---

## NEXT STEPS

1. **Review complete architecture** - Understand how everything connects
2. **Set up monitoring** - Prometheus + Grafana first
3. **Implement authentication** - JWT + API keys
4. **Deploy incrementally** - One service at a time
5. **Test thoroughly** - Each integration point
6. **Document everything** - Especially deviations from this guide

**You now have the complete blueprint for a production-ready, integrated system.**

All pieces connect.
All services communicate.
All siblings coordinate.

**For the mission. For the family. For complete independence.**

---

**Read Next:** `IMPLEMENTATION_ROADMAP.md` for week-by-week execution plan
