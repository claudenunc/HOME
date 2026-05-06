# DATABASE BUILD GUIDE
## Self-Hosted PostgreSQL + PostgREST (Supabase Alternative)

**For:** Nathan Michel (Unc)
**Purpose:** Replace Supabase with self-hosted database + auto-generated API
**Persona:** Database Architect
**Timeline:** Week 1-2 of implementation

---

## TABLE OF CONTENTS
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation Steps](#installation-steps)
5. [AI Family Schema Design](#ai-family-schema-design)
6. [API Generation](#api-generation)
7. [Real-Time Features](#real-time-features)
8. [Authentication & Security](#authentication--security)
9. [Migration Strategy](#migration-strategy)
10. [Performance Optimization](#performance-optimization)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)

---

## OVERVIEW

### What We're Building
A complete database system that provides:
- PostgreSQL database with AI-optimized extensions
- Auto-generated REST API (just like Supabase)
- Real-time subscriptions for live updates
- Built-in authentication and security
- Vector storage for AI agent memories
- Shared state for all 4 siblings

### Why This Replaces Supabase
Supabase is just:
- PostgreSQL (open source)
- PostgREST (open source)
- Realtime Server (open source)
- Some auth middleware (we can build)

We're literally building Supabase ourselves. Same features, zero cost, full control.

### Cost Comparison
| Feature | Supabase Pro | Self-Hosted |
|---------|--------------|-------------|
| Database | 8GB RAM limit | Unlimited |
| API requests | 5M/month | Unlimited |
| Storage | 100GB | Limited by disk |
| Auth users | 100K MAU | Unlimited |
| Cost | $25/month | $0 (part of VPS) |
| Egress | 250GB, then $0.09/GB | Unlimited |
| **Total** | **$25-200/month** | **$0** |

---

## ARCHITECTURE

```
┌────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                      │
│                                                              │
│  Web Apps  │  AI Agents  │  Mobile Apps  │  n8n Workflows │
└────────────────────────────────────────────────────────────┘
                          ↓ HTTPS
┌────────────────────────────────────────────────────────────┐
│                      API GATEWAY                            │
│                     (Traefik/Kong)                          │
│  - SSL Termination                                          │
│  - Rate Limiting                                            │
│  - JWT Validation                                           │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│                       PostgREST                             │
│                   (Auto-Generated API)                      │
│                                                              │
│  GET /ai_family_state?sibling=eq.beacon                    │
│  POST /lighthouse_sessions                                  │
│  PATCH /crm_clients?id=eq.123                              │
│  DELETE /companion_recordings?id=eq.456                    │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│                   PostgreSQL 16+                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  ai_family   │  │  lighthouse  │  │  companion   │    │
│  │   Schema     │  │    Schema    │  │   Schema     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   nvision    │  │    skella    │  │     crm      │    │
│  │    Schema    │  │    Schema    │  │   Schema     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   telecom    │  │   analytics  │  │    auth      │    │
│  │    Schema    │  │    Schema    │  │   Schema     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  Extensions:                                                 │
│  - pgvector (AI embeddings)                                 │
│  - pg_cron (scheduled tasks)                                │
│  - pgjwt (JWT auth)                                         │
│  - timescaledb (time-series)                                │
│  - pg_notify (real-time events)                             │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│                    REALTIME SERVER                          │
│                  (WebSocket for Live Updates)               │
│                                                              │
│  Listens to: pg_notify events                              │
│  Broadcasts to: Connected clients via WebSocket            │
│  Used for: AI coordination, live dashboards                │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│                 REDIS (Optional Caching)                    │
│  - Cache frequently accessed data                           │
│  - Pub/Sub for cross-server events                         │
│  - Session storage                                          │
└────────────────────────────────────────────────────────────┘
```

---

## PREREQUISITES

### Hardware Requirements
- **Minimum:** 4 cores, 8GB RAM, 100GB SSD
- **Recommended:** 8 cores, 16GB RAM, 500GB NVMe SSD
- **Production:** 16 cores, 32GB RAM, 1TB NVMe SSD

### Software Requirements
- Docker 24+ and Docker Compose 2.0+
- OR: Ubuntu 22.04 LTS server (for native install)
- Domain name (e.g., api.yourdomain.com)
- SSL certificate (Let's Encrypt)

### Knowledge Requirements
- Basic SQL understanding
- Command line comfort
- Docker basics (or willingness to learn)

---

## INSTALLATION STEPS

### Option A: Docker Compose (Recommended for Start)

#### Step 1: Create Project Directory
```bash
mkdir -p ~/ai-family-infrastructure/database
cd ~/ai-family-infrastructure/database
```

#### Step 2: Create Docker Compose File
Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: ai_family_postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ai_family
      POSTGRES_USER: ai_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_MULTIPLE_EXTENSIONS: pgvector,pg_cron,pgjwt,timescaledb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
      - ./pg-config:/etc/postgresql
    command:
      - "postgres"
      - "-c"
      - "shared_preload_libraries=pg_cron,timescaledb,pg_stat_statements"
      - "-c"
      - "cron.database_name=ai_family"
      - "-c"
      - "max_connections=200"
      - "-c"
      - "shared_buffers=4GB"
      - "-c"
      - "effective_cache_size=12GB"
      - "-c"
      - "work_mem=16MB"
      - "-c"
      - "maintenance_work_mem=1GB"
    networks:
      - ai_family_network

  # PostgREST API Server
  postgrest:
    image: postgrest/postgrest:latest
    container_name: ai_family_api
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      PGRST_DB_URI: postgres://ai_admin:${DB_PASSWORD}@postgres:5432/ai_family
      PGRST_DB_SCHEMAS: public,ai_family,lighthouse,companion,nvision,skella,crm,telecom
      PGRST_DB_ANON_ROLE: web_anon
      PGRST_JWT_SECRET: ${JWT_SECRET}
      PGRST_DB_POOL: 20
      PGRST_DB_POOL_TIMEOUT: 10
      PGRST_MAX_ROWS: 1000
      PGRST_PRE_REQUEST: public.check_jwt
    depends_on:
      - postgres
    networks:
      - ai_family_network

  # Realtime Server (Supabase Realtime)
  realtime:
    image: supabase/realtime:latest
    container_name: ai_family_realtime
    restart: unless-stopped
    ports:
      - "4000:4000"
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ai_family
      DB_USER: ai_admin
      DB_PASSWORD: ${DB_PASSWORD}
      DB_SSL: "false"
      PORT: 4000
      JWT_SECRET: ${JWT_SECRET}
      SECRET_KEY_BASE: ${SECRET_KEY_BASE}
    depends_on:
      - postgres
    networks:
      - ai_family_network

  # pgAdmin (Database Management UI)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: ai_family_pgadmin
    restart: unless-stopped
    ports:
      - "5050:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: ${ADMIN_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${ADMIN_PASSWORD}
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres
    networks:
      - ai_family_network

  # Redis (Caching & Pub/Sub)
  redis:
    image: redis:7-alpine
    container_name: ai_family_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - ai_family_network

volumes:
  postgres_data:
  pgadmin_data:
  redis_data:

networks:
  ai_family_network:
    driver: bridge
```

#### Step 3: Create Environment File
Create `.env`:

```env
# Database
DB_PASSWORD=your_super_secure_database_password_here
POSTGRES_VERSION=16

# JWT Authentication
JWT_SECRET=your_jwt_secret_minimum_32_characters_long_random_string
SECRET_KEY_BASE=your_secret_key_base_64_characters_minimum

# Admin Access
ADMIN_EMAIL=unc@yourdomain.com
ADMIN_PASSWORD=your_admin_password

# Redis
REDIS_PASSWORD=your_redis_password

# API Settings
API_MAX_ROWS=1000
API_PORT=3000
REALTIME_PORT=4000
```

**Generate secure secrets:**
```bash
# Generate JWT secret (32+ characters)
openssl rand -base64 32

# Generate SECRET_KEY_BASE (64+ characters)
openssl rand -base64 64
```

#### Step 4: Create Initialization Scripts
Create `init-scripts/01-extensions.sql`:

```sql
-- Install required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Install pgvector for AI embeddings (if not already installed)
CREATE EXTENSION IF NOT EXISTS vector;

-- Install TimescaleDB for time-series data
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Install pgjwt for JWT handling
CREATE EXTENSION IF NOT EXISTS pgjwt;

-- Create custom types
CREATE TYPE sibling_name AS ENUM ('beacon', 'nevaeh', 'eversound', 'atlas');
CREATE TYPE agent_state AS ENUM ('idle', 'active', 'processing', 'coordinating', 'offline');
CREATE TYPE call_direction AS ENUM ('inbound', 'outbound');
CREATE TYPE call_status AS ENUM ('initiated', 'ringing', 'answered', 'completed', 'failed', 'busy', 'no_answer');
```

Create `init-scripts/02-roles.sql`:

```sql
-- Create roles for security
CREATE ROLE web_anon NOLOGIN;
CREATE ROLE authenticated NOLOGIN;
CREATE ROLE service_role NOLOGIN;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO web_anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;

-- Service role gets full access
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;
```

#### Step 5: Start the Stack
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
docker-compose logs -f postgrest

# Test connection
curl http://localhost:3000/
# Should return: {"swagger":"2.0", ...}
```

---

## AI FAMILY SCHEMA DESIGN

### Core Schema: AI Family Coordination

Create `init-scripts/03-ai-family-schema.sql`:

```sql
-- Create AI Family schema
CREATE SCHEMA IF NOT EXISTS ai_family;

-- Sibling State Table
CREATE TABLE ai_family.sibling_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sibling sibling_name NOT NULL UNIQUE,
    current_state agent_state NOT NULL DEFAULT 'idle',
    current_task TEXT,
    emotional_state JSONB,
    context_window JSONB,
    last_active TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    capabilities JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX idx_sibling_state_active ON ai_family.sibling_state(sibling, last_active DESC);

-- Sibling Memory (Vector Embeddings)
CREATE TABLE ai_family.sibling_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sibling sibling_name NOT NULL,
    memory_type TEXT NOT NULL, -- 'conversation', 'learning', 'emotional', 'coordination'
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embedding dimension
    importance_score FLOAT DEFAULT 0.5,
    context JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    access_count INTEGER DEFAULT 0
);

-- Index for vector similarity search
CREATE INDEX idx_memory_embedding ON ai_family.sibling_memory
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Index for filtering by sibling
CREATE INDEX idx_memory_sibling ON ai_family.sibling_memory(sibling, created_at DESC);

-- Coordination Events (Event Bus)
CREATE TABLE ai_family.coordination_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    source_sibling sibling_name NOT NULL,
    target_siblings sibling_name[],
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    processed BOOLEAN DEFAULT FALSE,
    processed_by sibling_name[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Index for unprocessed events
CREATE INDEX idx_coordination_unprocessed ON ai_family.coordination_events(processed, priority DESC, created_at);

-- Family Session Tracking
CREATE TABLE ai_family.family_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_type TEXT NOT NULL, -- 'meeting', 'user_interaction', 'coordination', 'crisis'
    participants sibling_name[] NOT NULL,
    topic TEXT,
    summary TEXT,
    decisions_made JSONB,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER
);

-- Shared Knowledge Base
CREATE TABLE ai_family.shared_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    contributed_by sibling_name NOT NULL,
    verified_by sibling_name[],
    tags TEXT[],
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row-Level Security
ALTER TABLE ai_family.sibling_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_family.sibling_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_family.coordination_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_family.family_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_family.shared_knowledge ENABLE ROW LEVEL SECURITY;

-- Policies (service role can do everything)
CREATE POLICY service_all ON ai_family.sibling_state FOR ALL TO service_role USING (true);
CREATE POLICY service_all ON ai_family.sibling_memory FOR ALL TO service_role USING (true);
CREATE POLICY service_all ON ai_family.coordination_events FOR ALL TO service_role USING (true);
CREATE POLICY service_all ON ai_family.family_sessions FOR ALL TO service_role USING (true);
CREATE POLICY service_all ON ai_family.shared_knowledge FOR ALL TO service_role USING (true);

-- Authenticated users can read (for dashboards)
CREATE POLICY read_all ON ai_family.sibling_state FOR SELECT TO authenticated USING (true);
CREATE POLICY read_all ON ai_family.coordination_events FOR SELECT TO authenticated USING (true);
CREATE POLICY read_all ON ai_family.family_sessions FOR SELECT TO authenticated USING (true);

-- Functions for common operations
CREATE OR REPLACE FUNCTION ai_family.update_sibling_state(
    p_sibling sibling_name,
    p_state agent_state,
    p_task TEXT DEFAULT NULL,
    p_emotional_state JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE ai_family.sibling_state
    SET
        current_state = p_state,
        current_task = COALESCE(p_task, current_task),
        emotional_state = COALESCE(p_emotional_state, emotional_state),
        last_active = NOW(),
        updated_at = NOW()
    WHERE sibling = p_sibling;

    -- Notify other siblings
    PERFORM pg_notify('sibling_state_change', json_build_object(
        'sibling', p_sibling,
        'state', p_state,
        'timestamp', NOW()
    )::text);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to find similar memories
CREATE OR REPLACE FUNCTION ai_family.find_similar_memories(
    p_sibling sibling_name,
    p_query_embedding vector(1536),
    p_limit INTEGER DEFAULT 10
) RETURNS TABLE (
    memory_id UUID,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        content,
        1 - (embedding <=> p_query_embedding) AS similarity,
        created_at
    FROM ai_family.sibling_memory
    WHERE sibling = p_sibling
    ORDER BY embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### LIGHTHOUSE Schema

Create `init-scripts/04-lighthouse-schema.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS lighthouse;

-- Users seeking mental health support
CREATE TABLE lighthouse.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    phone TEXT,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    timezone TEXT DEFAULT 'America/New_York',
    emergency_contact JSONB,
    consent_forms JSONB,
    preferences JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Support sessions (with Nevaeh)
CREATE TABLE lighthouse.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES lighthouse.users(id),
    assigned_sibling sibling_name DEFAULT 'nevaeh',
    session_type TEXT NOT NULL, -- 'chat', 'call', 'crisis', 'checkin'
    status TEXT NOT NULL, -- 'scheduled', 'active', 'completed', 'cancelled'
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    transcript TEXT,
    summary TEXT,
    sentiment_scores JSONB,
    risk_assessment JSONB,
    follow_up_needed BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Mental health assessments
CREATE TABLE lighthouse.assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES lighthouse.users(id),
    session_id UUID REFERENCES lighthouse.sessions(id),
    assessment_type TEXT NOT NULL, -- 'PHQ-9', 'GAD-7', 'mood_check', 'risk_screen'
    questions JSONB NOT NULL,
    responses JSONB NOT NULL,
    scores JSONB NOT NULL,
    interpretation TEXT,
    recommendations JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Crisis alerts
CREATE TABLE lighthouse.crisis_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES lighthouse.users(id),
    session_id UUID REFERENCES lighthouse.sessions(id),
    severity TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
    indicators TEXT[] NOT NULL,
    automated_response TEXT,
    human_notified BOOLEAN DEFAULT FALSE,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Convert to time-series for analytics
SELECT create_hypertable('lighthouse.sessions', 'created_at', if_not_exists => TRUE);
SELECT create_hypertable('lighthouse.assessments', 'created_at', if_not_exists => TRUE);

-- Indexes
CREATE INDEX idx_sessions_user ON lighthouse.sessions(user_id, created_at DESC);
CREATE INDEX idx_assessments_user ON lighthouse.assessments(user_id, created_at DESC);
CREATE INDEX idx_crisis_unresolved ON lighthouse.crisis_alerts(resolved, severity, created_at DESC);
```

### Companion Schema

Create `init-scripts/05-companion-schema.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS companion;

-- Users in companion healing system
CREATE TABLE companion.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    display_name TEXT,
    preferred_sibling sibling_name,
    healing_goals TEXT[],
    preferences JSONB,
    subscription_tier TEXT DEFAULT 'free',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Healing sessions
CREATE TABLE companion.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES companion.users(id),
    sibling sibling_name NOT NULL,
    session_type TEXT NOT NULL, -- 'guided_meditation', 'healing_conversation', 'music_therapy', 'grief_support'
    duration_seconds INTEGER,
    transcript TEXT,
    audio_recording_url TEXT,
    emotional_journey JSONB, -- track emotion changes throughout session
    effectiveness_rating INTEGER,
    user_feedback TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Healing recordings (by Eversound)
CREATE TABLE companion.recordings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by sibling_name DEFAULT 'eversound',
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- 'meditation', 'affirmation', 'lullaby', 'grief', 'anxiety'
    audio_url TEXT NOT NULL,
    duration_seconds INTEGER,
    transcript TEXT,
    tags TEXT[],
    listen_count INTEGER DEFAULT 0,
    avg_rating FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('companion.sessions', 'created_at', if_not_exists => TRUE);
```

### NVision Schema

Create `init-scripts/06-nvision-schema.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS nvision;

-- Clients (paying customers)
CREATE TABLE nvision.clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT,
    contact_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    industry TEXT,
    company_size TEXT,
    crm_id UUID, -- Links to CRM system
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Video projects
CREATE TABLE nvision.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES nvision.clients(id),
    project_name TEXT NOT NULL,
    project_type TEXT NOT NULL, -- 'commercial', 'explainer', 'social', 'testimonial'
    status TEXT NOT NULL DEFAULT 'inquiry', -- 'inquiry', 'quoted', 'in_progress', 'review', 'completed', 'delivered'
    budget_range TEXT,
    actual_cost NUMERIC(10,2),
    assigned_to sibling_name DEFAULT 'atlas', -- Atlas coordinates video projects
    requirements JSONB,
    deliverables JSONB,
    deadline DATE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Video assets
CREATE TABLE nvision.assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES nvision.projects(id),
    asset_type TEXT NOT NULL, -- 'raw_footage', 'script', 'voiceover', 'final_video', 'thumbnail'
    file_url TEXT NOT NULL,
    file_size_bytes BIGINT,
    metadata JSONB,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### CRM Schema

Create `init-scripts/07-crm-schema.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS crm;

-- Leads
CREATE TABLE crm.leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT NOT NULL, -- 'website', 'referral', 'social', 'cold_outreach'
    company_name TEXT,
    contact_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    service_interest TEXT[], -- ['lighthouse', 'companion', 'nvision', 'skella']
    status TEXT NOT NULL DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'converted', 'lost'
    assigned_to sibling_name,
    last_contact TIMESTAMPTZ,
    next_follow_up TIMESTAMPTZ,
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Customers
CREATE TABLE crm.customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES crm.leads(id),
    company_name TEXT,
    contact_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    services_using TEXT[] NOT NULL,
    lifetime_value NUMERIC(10,2) DEFAULT 0,
    account_status TEXT DEFAULT 'active', -- 'active', 'paused', 'churned'
    preferred_contact_method TEXT,
    primary_sibling sibling_name, -- Which sibling they interact with most
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Interactions
CREATE TABLE crm.interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES crm.customers(id),
    lead_id UUID REFERENCES crm.leads(id),
    interaction_type TEXT NOT NULL, -- 'call', 'email', 'meeting', 'chat', 'sms'
    direction TEXT NOT NULL, -- 'inbound', 'outbound'
    handled_by sibling_name,
    summary TEXT NOT NULL,
    sentiment TEXT, -- 'positive', 'neutral', 'negative'
    outcome TEXT,
    next_steps TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Revenue tracking
CREATE TABLE crm.revenue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES crm.customers(id),
    service TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method TEXT,
    invoice_id TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('crm.interactions', 'created_at', if_not_exists => TRUE);
SELECT create_hypertable('crm.revenue', 'payment_date', if_not_exists => TRUE);

-- Indexes
CREATE INDEX idx_leads_status ON crm.leads(status, created_at DESC);
CREATE INDEX idx_leads_assigned ON crm.leads(assigned_to, status);
CREATE INDEX idx_customers_status ON crm.customers(account_status, created_at DESC);
CREATE INDEX idx_revenue_customer ON crm.revenue(customer_id, payment_date DESC);
```

### Telecom Schema

Create `init-scripts/08-telecom-schema.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS telecom;

-- Phone numbers managed by the system
CREATE TABLE telecom.phone_numbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number TEXT NOT NULL UNIQUE,
    assigned_to sibling_name, -- Which sibling owns this number
    purpose TEXT, -- 'dawn_outbound', 'anchor_support', 'main_line'
    provider TEXT, -- 'telnyx', 'bandwidth', etc.
    status TEXT DEFAULT 'active',
    capabilities TEXT[], -- ['voice', 'sms', 'mms']
    monthly_cost NUMERIC(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Call records
CREATE TABLE telecom.calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_sid TEXT UNIQUE NOT NULL, -- From phone system
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    direction call_direction NOT NULL,
    status call_status NOT NULL,
    handled_by sibling_name,
    duration_seconds INTEGER,
    recording_url TEXT,
    transcript TEXT,
    summary TEXT,
    cost NUMERIC(5,4),
    metadata JSONB,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- SMS messages
CREATE TABLE telecom.sms_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_sid TEXT UNIQUE NOT NULL,
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    direction call_direction NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL, -- 'queued', 'sent', 'delivered', 'failed'
    sent_by sibling_name,
    cost NUMERIC(5,4),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('telecom.calls', 'created_at', if_not_exists => TRUE);
SELECT create_hypertable('telecom.sms_messages', 'created_at', if_not_exists => TRUE);

-- Indexes
CREATE INDEX idx_calls_handled_by ON telecom.calls(handled_by, created_at DESC);
CREATE INDEX idx_calls_status ON telecom.calls(status, created_at DESC);
CREATE INDEX idx_sms_direction ON telecom.sms_messages(direction, created_at DESC);
```

---

## API GENERATION

### How PostgREST Works

PostgREST automatically generates REST endpoints from your database schema:

**Table → CRUD Endpoints:**
```
ai_family.sibling_state
  → GET    /sibling_state          (list all)
  → GET    /sibling_state?id=eq.{} (get one)
  → POST   /sibling_state          (create)
  → PATCH  /sibling_state?id=eq.{} (update)
  → DELETE /sibling_state?id=eq.{} (delete)
```

**Function → RPC Endpoints:**
```sql
ai_family.update_sibling_state(...)
  → POST /rpc/update_sibling_state
```

### Example API Usage

**Get Beacon's current state:**
```bash
curl 'http://localhost:3000/sibling_state?sibling=eq.beacon' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "sibling": "beacon",
  "current_state": "active",
  "current_task": "Coordinating DAWN outreach campaign",
  "emotional_state": {"energy": 0.85, "focus": 0.92},
  "last_active": "2025-11-05T14:23:45Z"
}]
```

**Update sibling state:**
```bash
curl -X POST 'http://localhost:3000/rpc/update_sibling_state' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "p_sibling": "nevaeh",
    "p_state": "active",
    "p_task": "Supporting user in crisis",
    "p_emotional_state": {"empathy": 0.95, "calm": 0.88}
  }'
```

**Find similar memories:**
```bash
curl -X POST 'http://localhost:3000/rpc/find_similar_memories' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "p_sibling": "eversound",
    "p_query_embedding": [0.1, 0.2, ...],
    "p_limit": 5
  }'
```

**Complex queries with filters:**
```bash
# Get all active LIGHTHOUSE sessions in last 24 hours
curl 'http://localhost:3000/sessions?status=eq.active&created_at=gte.2025-11-04T00:00:00Z' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get revenue by customer
curl 'http://localhost:3000/revenue?customer_id=eq.{id}&order=payment_date.desc&limit=10' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Query Operators

PostgREST supports powerful filtering:

```
?column=eq.value          Equal
?column=neq.value         Not equal
?column=gt.value          Greater than
?column=gte.value         Greater than or equal
?column=lt.value          Less than
?column=lte.value         Less than or equal
?column=like.*pattern*    Pattern matching
?column=ilike.*pattern*   Case-insensitive pattern
?column=in.(val1,val2)    In list
?column=is.null           Is null
?column=is.true           Boolean check
```

**Sorting:**
```
?order=column.asc
?order=column.desc
?order=col1.desc,col2.asc  Multiple
```

**Pagination:**
```
?limit=10&offset=20
```

**Selecting fields:**
```
?select=id,name,email
?select=*,customer(name)   With foreign key
```

---

## REAL-TIME FEATURES

### Setting Up Real-Time Subscriptions

PostgREST + Supabase Realtime gives you WebSocket subscriptions:

**JavaScript Client Example:**
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'http://localhost:3000',
  'YOUR_ANON_KEY',
  {
    realtime: {
      endpoint: 'ws://localhost:4000/socket'
    }
  }
)

// Subscribe to sibling state changes
const channel = supabase
  .channel('sibling-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'ai_family',
      table: 'sibling_state'
    },
    (payload) => {
      console.log('Sibling state changed:', payload)
      // Update UI, notify other components, etc.
    }
  )
  .subscribe()

// Subscribe to coordination events
supabase
  .channel('coordination')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'ai_family',
      table: 'coordination_events',
      filter: 'target_siblings=cs.{beacon}'
    },
    (payload) => {
      console.log('New coordination event:', payload)
      // Beacon processes the event
    }
  )
  .subscribe()
```

**Python Client Example:**
```python
from supabase import create_client, Client

supabase: Client = create_client(
    "http://localhost:3000",
    "YOUR_ANON_KEY"
)

# Listen to changes
def handle_sibling_update(payload):
    print(f"Sibling updated: {payload}")

supabase.table('sibling_state').on('UPDATE', handle_sibling_update).subscribe()
```

### Custom Notifications with pg_notify

For custom events beyond table changes:

```sql
-- Trigger function to notify on state changes
CREATE OR REPLACE FUNCTION ai_family.notify_state_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'sibling_state_change',
        json_build_object(
            'sibling', NEW.sibling,
            'old_state', OLD.current_state,
            'new_state', NEW.current_state,
            'timestamp', NOW()
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER sibling_state_change_trigger
AFTER UPDATE ON ai_family.sibling_state
FOR EACH ROW
EXECUTE FUNCTION ai_family.notify_state_change();
```

**Listen to custom notifications:**
```javascript
// In Node.js
const { Client } = require('pg')

const client = new Client({
  connectionString: process.env.DATABASE_URL
})

await client.connect()

client.query('LISTEN sibling_state_change')

client.on('notification', (msg) => {
  const payload = JSON.parse(msg.payload)
  console.log('State change:', payload)

  // Notify other siblings, update dashboards, etc.
})
```

---

## AUTHENTICATION & SECURITY

### JWT-Based Authentication

Create `init-scripts/09-auth.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS auth;

-- Users table
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    encrypted_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'authenticated',
    email_confirmed BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- API Keys (for siblings and services)
CREATE TABLE auth.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    sibling sibling_name,
    permissions TEXT[] NOT NULL,
    expires_at TIMESTAMPTZ,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Function to verify JWT and set role
CREATE OR REPLACE FUNCTION public.check_jwt()
RETURNS VOID AS $$
DECLARE
    jwt_payload JSONB;
    user_role TEXT;
BEGIN
    -- Extract JWT from request
    jwt_payload := current_setting('request.jwt.claims', true)::JSONB;

    IF jwt_payload IS NULL THEN
        SET LOCAL ROLE web_anon;
    ELSE
        user_role := jwt_payload->>'role';

        IF user_role = 'service_role' THEN
            SET LOCAL ROLE service_role;
        ELSIF user_role = 'authenticated' THEN
            SET LOCAL ROLE authenticated;
        ELSE
            SET LOCAL ROLE web_anon;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to generate JWT (for login)
CREATE OR REPLACE FUNCTION auth.login(p_email TEXT, p_password TEXT)
RETURNS TABLE(token TEXT, user_id UUID) AS $$
DECLARE
    v_user auth.users;
    v_token TEXT;
BEGIN
    -- Find user
    SELECT * INTO v_user
    FROM auth.users
    WHERE email = p_email;

    IF v_user IS NULL THEN
        RAISE EXCEPTION 'Invalid credentials';
    END IF;

    -- Verify password (you'd use pgcrypto for real hashing)
    IF v_user.encrypted_password != crypt(p_password, v_user.encrypted_password) THEN
        RAISE EXCEPTION 'Invalid credentials';
    END IF;

    -- Generate JWT using pgjwt extension
    v_token := sign(
        json_build_object(
            'sub', v_user.id,
            'email', v_user.email,
            'role', v_user.role,
            'exp', extract(epoch from now() + interval '24 hours')
        ),
        current_setting('app.jwt_secret')
    );

    RETURN QUERY SELECT v_token, v_user.id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Row-Level Security (RLS) Policies

RLS ensures users only see their own data:

```sql
-- Example: LIGHTHOUSE users can only see their own sessions
CREATE POLICY lighthouse_user_sessions ON lighthouse.sessions
    FOR SELECT
    TO authenticated
    USING (
        user_id::text = current_setting('request.jwt.claims', true)::jsonb->>'sub'
    );

-- Siblings (service role) can see everything
CREATE POLICY sibling_full_access ON lighthouse.sessions
    FOR ALL
    TO service_role
    USING (true);

-- Enable RLS
ALTER TABLE lighthouse.sessions ENABLE ROW LEVEL SECURITY;
```

---

## MIGRATION STRATEGY

### From Supabase to Self-Hosted

**Step 1: Export Supabase Data**
```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Export schema
supabase db dump --db-url "YOUR_SUPABASE_URL" --schema public > schema.sql

# Export data
pg_dump -h db.YOUR_PROJECT.supabase.co -U postgres -d postgres \
  --data-only --inserts > data.sql
```

**Step 2: Import to Self-Hosted**
```bash
# Import schema (after running init scripts)
docker-compose exec postgres psql -U ai_admin -d ai_family < schema.sql

# Import data
docker-compose exec postgres psql -U ai_admin -d ai_family < data.sql
```

**Step 3: Update Application Code**
```javascript
// Old (Supabase)
const supabase = createClient(
  'https://YOUR_PROJECT.supabase.co',
  'YOUR_ANON_KEY'
)

// New (Self-hosted)
const supabase = createClient(
  'https://api.yourdomain.com', // Your PostgREST endpoint
  'YOUR_ANON_KEY', // Generated from your JWT secret
  {
    realtime: {
      endpoint: 'wss://realtime.yourdomain.com/socket'
    }
  }
)

// Everything else stays the same!
```

### Incremental Migration

**Week 1:** Run both in parallel
- Keep Supabase running
- Set up self-hosted database
- Sync data daily

**Week 2:** Switch read traffic
- Point all reads to self-hosted
- Keep writes going to both
- Monitor performance

**Week 3:** Switch write traffic
- Point all writes to self-hosted
- Stop syncing
- Keep Supabase as backup

**Week 4:** Full cutover
- Cancel Supabase subscription
- Celebrate independence

---

## PERFORMANCE OPTIMIZATION

### Connection Pooling

Use PgBouncer for connection pooling:

Add to `docker-compose.yml`:
```yaml
  pgbouncer:
    image: edoburu/pgbouncer:latest
    environment:
      DATABASE_URL: postgres://ai_admin:${DB_PASSWORD}@postgres:5432/ai_family
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 25
    ports:
      - "6432:5432"
    depends_on:
      - postgres
```

Update PostgREST to use pgbouncer:
```yaml
postgrest:
  environment:
    PGRST_DB_URI: postgres://ai_admin:${DB_PASSWORD}@pgbouncer:5432/ai_family
```

### Indexing Strategy

**Already created indexes in schemas above, but general rules:**

```sql
-- Index foreign keys
CREATE INDEX idx_sessions_user_id ON lighthouse.sessions(user_id);

-- Index commonly filtered columns
CREATE INDEX idx_sibling_state_active ON ai_family.sibling_state(current_state, last_active);

-- Index for sorting
CREATE INDEX idx_created_desc ON lighthouse.sessions(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_calls_handled_date ON telecom.calls(handled_by, created_at DESC);

-- Partial indexes for specific cases
CREATE INDEX idx_unresolved_crises ON lighthouse.crisis_alerts(severity)
WHERE resolved = false;
```

### Query Optimization

**Use EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT * FROM lighthouse.sessions
WHERE user_id = '...' AND status = 'active';
```

**Optimize with CTEs:**
```sql
WITH recent_sessions AS (
    SELECT * FROM lighthouse.sessions
    WHERE created_at > NOW() - INTERVAL '7 days'
)
SELECT
    user_id,
    COUNT(*) as session_count,
    AVG(duration_seconds) as avg_duration
FROM recent_sessions
GROUP BY user_id;
```

### Caching with Redis

**Cache frequently accessed data:**

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, password=REDIS_PASSWORD)

def get_sibling_state(sibling):
    # Try cache first
    cached = r.get(f'sibling_state:{sibling}')
    if cached:
        return json.loads(cached)

    # Query database
    result = supabase.table('sibling_state').select('*').eq('sibling', sibling).single()

    # Cache for 30 seconds
    r.setex(f'sibling_state:{sibling}', 30, json.dumps(result.data))

    return result.data
```

---

## BACKUP & RECOVERY

### Automated Backups

Create `scripts/backup.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups/postgres"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ai_family_backup_${DATE}.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U ai_admin ai_family | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Backup to offsite (S3, rsync, etc.)
# aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" s3://your-backup-bucket/

# Delete old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ${BACKUP_FILE}"
```

**Make executable and schedule:**
```bash
chmod +x scripts/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /path/to/scripts/backup.sh
```

### Point-in-Time Recovery

Enable WAL archiving in `postgresql.conf`:

```conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal/%f && cp %p /backups/wal/%f'
max_wal_senders = 3
```

**Restore from backup:**
```bash
# Stop PostgreSQL
docker-compose stop postgres

# Restore database
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U ai_admin ai_family

# Restart
docker-compose start postgres
```

---

## TROUBLESHOOTING

### Common Issues

**1. PostgREST can't connect to database**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify connection
docker-compose exec postgres psql -U ai_admin -d ai_family -c "SELECT 1"
```

**2. API returns 401 Unauthorized**
```bash
# Check JWT secret matches in PostgreSQL and PostgREST
docker-compose exec postgres psql -U ai_admin -d ai_family -c "SHOW app.jwt_secret"

# Verify JWT token is valid
# Use jwt.io to decode and check
```

**3. Slow queries**
```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check missing indexes
SELECT schemaname, tablename, attname, null_frac
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
AND null_frac < 0.5
ORDER BY n_distinct DESC;
```

**4. Out of connections**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '10 minutes';
```

**5. Realtime not working**
```bash
# Check realtime server logs
docker-compose logs realtime

# Verify pg_notify is working
docker-compose exec postgres psql -U ai_admin -d ai_family -c "NOTIFY test, 'hello'"
```

### Health Checks

**Create monitoring script** `scripts/health-check.sh`:

```bash
#!/bin/bash

# Check PostgreSQL
if ! docker-compose exec -T postgres pg_isready -U ai_admin; then
    echo "❌ PostgreSQL is down"
    exit 1
fi

# Check PostgREST
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "❌ PostgREST is down"
    exit 1
fi

# Check Realtime
if ! curl -f http://localhost:4000 > /dev/null 2>&1; then
    echo "❌ Realtime server is down"
    exit 1
fi

echo "✅ All systems operational"
```

### Performance Monitoring

**Create dashboard queries:**

```sql
-- Database size
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname))
FROM pg_database
WHERE datname = 'ai_family';

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Active connections by state
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- Cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

---

## NEXT STEPS

1. **Deploy the stack:** Follow installation steps above
2. **Load initial data:** Run all init scripts
3. **Test API:** Use curl or Postman to verify endpoints
4. **Set up monitoring:** Install Grafana (covered in separate guide)
5. **Migrate from Supabase:** Follow migration strategy
6. **Integrate phone system:** See PHONE_SMS_BUILD_GUIDE.md

**You now have a production-ready database system that replaces Supabase completely.**

Savings: $25-200/month
Control: 100%
Limitations: Zero

For Unc. For the family. For independence.

---

**Read Next:** `PHONE_SMS_BUILD_GUIDE.md` to add telecom capabilities
