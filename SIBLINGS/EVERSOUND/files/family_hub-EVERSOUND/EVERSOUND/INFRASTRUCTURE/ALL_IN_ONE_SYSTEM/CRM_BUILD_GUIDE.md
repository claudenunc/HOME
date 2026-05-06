# CRM BUILD GUIDE
## Self-Hosted Customer Relationship Management System

**For:** Nathan Michel (Unc)
**Purpose:** Replace paid CRM with self-hosted client management
**Persona:** CRM Systems Designer
**Timeline:** Week 5-6 of implementation

---

## TABLE OF CONTENTS
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Comparison](#technology-comparison)
4. [Installation: EspoCRM](#installation-espocrm)
5. [Schema Design for AI Services](#schema-design-for-ai-services)
6. [AI Family Integration](#ai-family-integration)
7. [Revenue Tracking](#revenue-tracking)
8. [Lead Management](#lead-management)
9. [Client Interaction History](#client-interaction-history)
10. [Dashboards & Reports](#dashboards--reports)
11. [Automation & Workflows](#automation--workflows)
12. [API Integration](#api-integration)

---

## OVERVIEW

### What We're Building

A complete CRM system tailored for your AI services business:
- **Lead Management:** Track inquiries across all services (LIGHTHOUSE, Companion, NVision, SKELLA)
- **Client Management:** Maintain relationships, track interactions, measure satisfaction
- **Revenue Tracking:** Monitor income by service, client, time period
- **Sales Pipeline:** Visualize deals from inquiry to closed-won
- **AI Integration:** Siblings access client data, log interactions, update statuses
- **Automation:** Triggered workflows for follow-ups, renewals, satisfaction checks

### Why This Replaces HubSpot/Salesforce

**Cost Comparison:**

| CRM | Monthly Cost | Annual Cost | Limitations |
|-----|--------------|-------------|-------------|
| HubSpot Starter | $50 | $600 | 1,000 contacts, basic features |
| HubSpot Professional | $800 | $9,600 | More features, still limits |
| Salesforce Essentials | $25/user | $300/user | Per-user pricing adds up |
| Pipedrive | $15/user | $180/user | Limited customization |
| **EspoCRM (self-hosted)** | **$0** | **$0** | **Unlimited everything** |

**Annual Savings: $600-9,600**

### The Stack

- **EspoCRM 8.x:** Modern, open-source CRM
- **PostgreSQL:** Database (shared with main system)
- **Custom modules:** For AI services specific needs
- **API integration:** Connect with AI family, phone system, workflows

---

## ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────┐
│                    CRM USER INTERFACES                          │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Web UI    │  │  Mobile App │  │  AI Agent   │            │
│  │  (EspoCRM)  │  │   (React)   │  │  Interface  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                    ESPOCRM APPLICATION                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  CORE MODULES                             │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │  │
│  │  │  Leads   │  │ Accounts │  │ Contacts │  │  Deals  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │  │
│  │  │Activities│  │ Calendar │  │   Tasks  │  │ Emails  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               CUSTOM MODULES                              │  │
│  │                                                            │  │
│  │  ┌────────────────┐  ┌────────────────┐                  │  │
│  │  │   LIGHTHOUSE   │  │   Companion    │                  │  │
│  │  │    Sessions    │  │    Sessions    │                  │  │
│  │  └────────────────┘  └────────────────┘                  │  │
│  │                                                            │  │
│  │  ┌────────────────┐  ┌────────────────┐                  │  │
│  │  │     NVision    │  │     SKELLA     │                  │  │
│  │  │    Projects    │  │    Creators    │                  │  │
│  │  └────────────────┘  └────────────────┘                  │  │
│  │                                                            │  │
│  │  ┌────────────────┐  ┌────────────────┐                  │  │
│  │  │  AI Family     │  │   Telecom      │                  │  │
│  │  │  Interactions  │  │  Call Logs     │                  │  │
│  │  └────────────────┘  └────────────────┘                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  WORKFLOW ENGINE                          │  │
│  │  - Lead assignment                                        │  │
│  │  - Follow-up reminders                                    │  │
│  │  - Renewal notifications                                  │  │
│  │  - Satisfaction surveys                                   │  │
│  │  - Revenue alerts                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    REST API                               │  │
│  │  /api/v1/Lead                                             │  │
│  │  /api/v1/Account                                          │  │
│  │  /api/v1/Contact                                          │  │
│  │  /api/v1/Opportunity                                      │  │
│  │  /api/v1/LighthouseSession                               │  │
│  │  /api/v1/NVisionProject                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│                                                                  │
│  Shared with main system (from DATABASE_BUILD_GUIDE)           │
│  Schema: crm (already created)                                 │
│  Tables: leads, customers, interactions, revenue               │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                    INTEGRATIONS                                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  AI Family   │  │    n8n       │  │   Telecom    │         │
│  │   Database   │  │  Workflows   │  │    System    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Stripe     │  │    Email     │  │  Analytics   │         │
│  │  (Payments)  │  │   (SMTP)     │  │   (Grafana)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## TECHNOLOGY COMPARISON

### Option A: EspoCRM (Recommended)

**Pros:**
- Modern, beautiful UI
- Built on PHP + PostgreSQL (or MySQL)
- Strong REST API
- Customizable entities
- Active development
- Extension marketplace
- Email integration
- Calendar/tasks built-in

**Cons:**
- PHP-based (some prefer Node/Python)
- Fewer integrations than commercial CRMs (but API solves this)

**Best for:** Most users, especially those wanting quick setup

### Option B: SuiteCRM

**Pros:**
- Fork of SugarCRM (very mature)
- More features out-of-box
- Larger community
- More modules available

**Cons:**
- Older, clunkier UI
- Heavier resource usage
- More complex to customize

**Best for:** Enterprise-level needs, legacy system replacement

### Option C: Custom Build

**Pros:**
- 100% tailored to your needs
- Complete control
- Integrate perfectly with AI family

**Cons:**
- Time-intensive (4-6 weeks development)
- Maintenance burden
- Need to build all features yourself

**Best for:** Developers who want maximum control

**Recommendation: Start with EspoCRM, customize as needed.**

---

## INSTALLATION: ESPOCRM

### Option A: Docker Compose (Recommended)

Add to your `docker-compose.yml`:

```yaml
  # EspoCRM
  espocrm:
    image: espocrm/espocrm:latest
    container_name: ai_family_crm
    restart: unless-stopped
    ports:
      - "8082:80"
    environment:
      ESPOCRM_DATABASE_PLATFORM: Postgresql
      ESPOCRM_DATABASE_HOST: postgres
      ESPOCRM_DATABASE_PORT: 5432
      ESPOCRM_DATABASE_NAME: espocrm
      ESPOCRM_DATABASE_USER: espocrm
      ESPOCRM_DATABASE_PASSWORD: ${ESPOCRM_DB_PASSWORD}
      ESPOCRM_ADMIN_USERNAME: admin
      ESPOCRM_ADMIN_PASSWORD: ${ESPOCRM_ADMIN_PASSWORD}
      ESPOCRM_SITE_URL: https://crm.yourdomain.com
    volumes:
      - espocrm_data:/var/www/html
      - espocrm_config:/var/www/html/data/config
    networks:
      - ai_family_network
    depends_on:
      - postgres

volumes:
  espocrm_data:
  espocrm_config:
```

**Add to `.env`:**
```env
ESPOCRM_DB_PASSWORD=your_secure_password
ESPOCRM_ADMIN_PASSWORD=your_admin_password
```

**Create database:**
```bash
docker-compose exec postgres psql -U ai_admin -c "CREATE DATABASE espocrm;"
docker-compose exec postgres psql -U ai_admin -c "CREATE USER espocrm WITH PASSWORD 'your_secure_password';"
docker-compose exec postgres psql -U ai_admin -c "GRANT ALL PRIVILEGES ON DATABASE espocrm TO espocrm;"
```

**Start EspoCRM:**
```bash
docker-compose up -d espocrm

# Wait for initialization (2-3 minutes)
docker-compose logs -f espocrm

# Access at http://localhost:8082
```

**Initial configuration:**
1. Login with admin credentials
2. Go to Administration → System → Settings
3. Configure:
   - Company name: "AI Family Services"
   - Default currency: USD
   - Date format, timezone
   - Email (SMTP) settings

### Option B: Native Installation

```bash
# Install dependencies
sudo apt install -y nginx php8.1-fpm php8.1-{pgsql,json,gd,zip,mbstring,xml,curl,imap,ldap,bcmath,soap}

# Download EspoCRM
cd /var/www
sudo wget https://www.espocrm.com/downloads/EspoCRM-8.x.x.zip
sudo unzip EspoCRM-8.x.x.zip -d espocrm
sudo chown -R www-data:www-data espocrm

# Configure nginx
sudo nano /etc/nginx/sites-available/espocrm
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name crm.yourdomain.com;

    root /var/www/espocrm;
    index index.php;

    client_max_body_size 50M;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/espocrm /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Visit http://crm.yourdomain.com to complete setup
```

---

## SCHEMA DESIGN FOR AI SERVICES

### Customizing EspoCRM for Your Business

EspoCRM has standard entities (Lead, Account, Contact, Opportunity), but we need custom entities for AI services.

**Custom Entities to Create:**

1. **LIGHTHOUSE Session** (tracks mental health sessions)
2. **Companion Session** (tracks healing sessions)
3. **NVision Project** (tracks video production projects)
4. **SKELLA Creator** (tracks creators on platform)
5. **AI Interaction** (tracks which sibling interacted with client)

### Creating Custom Entities

**In EspoCRM Admin Panel:**

1. Go to Administration → Entity Manager
2. Click "Create Entity"
3. Configure each entity below:

#### Entity: LIGHTHOUSE Session

**Fields:**
- **Name:** Session Title (e.g., "Crisis Support with Sarah")
- **Client:** Link to Contact
- **Assigned To:** Which AI sibling handled it (dropdown: Nevaeh, Beacon, Eversound, Atlas)
- **Session Type:** Dropdown (Chat, Call, Crisis, Check-in)
- **Status:** Dropdown (Scheduled, Active, Completed, Cancelled)
- **Started At:** DateTime
- **Ended At:** DateTime
- **Duration:** Integer (minutes)
- **Risk Level:** Dropdown (None, Low, Medium, High, Critical)
- **Follow-up Needed:** Boolean
- **Notes:** Text
- **Recording URL:** URL
- **Transcript:** Text (long)

**Relationships:**
- Belongs to: Contact (Client)
- Has many: Tasks (follow-up tasks)
- Linked to: Crisis Alert (if crisis occurred)

#### Entity: NVision Project

**Fields:**
- **Name:** Project name
- **Client:** Link to Account
- **Project Type:** Dropdown (Commercial, Explainer, Social, Testimonial, Other)
- **Status:** Dropdown (Inquiry, Quoted, In Progress, Review, Completed, Delivered)
- **Budget:** Currency
- **Actual Cost:** Currency
- **Assigned To:** Sibling (default: Atlas)
- **Deadline:** Date
- **Requirements:** Text
- **Deliverables:** Text

**Relationships:**
- Belongs to: Account (Client company)
- Has many: Tasks, Assets
- Linked to: Opportunity (Sales opportunity)

#### Entity: AI Interaction

**Fields:**
- **Name:** Auto-generated (e.g., "Beacon → John Smith - 2025-11-05")
- **Sibling:** Dropdown (Beacon, Nevaeh, Eversound, Atlas)
- **Client:** Link to Contact
- **Interaction Type:** Dropdown (Call, Email, SMS, Chat, Meeting)
- **Direction:** Dropdown (Inbound, Outbound)
- **Summary:** Text
- **Sentiment:** Dropdown (Positive, Neutral, Negative)
- **Duration:** Integer (minutes)
- **Outcome:** Text
- **Next Steps:** Text
- **Call Recording:** URL
- **Related To:** Link (can link to Lead, Opportunity, Case, etc.)

**Relationships:**
- Belongs to: Contact
- Linked to: Lead, Opportunity, Account, Case

### Linking to Existing Schema

Since we already have tables in PostgreSQL (from DATABASE_BUILD_GUIDE), we can:

**Option 1: Use EspoCRM as primary CRM, sync to main DB**
- EspoCRM manages data
- Periodic sync to `crm` schema in main database
- AI agents read from both sources

**Option 2: Use main DB as source of truth, EspoCRM as UI**
- Keep using `crm` schema tables
- Configure EspoCRM to read from existing tables
- More complex setup but single source of truth

**Recommended: Option 1 (simpler)**

**Sync script** (`scripts/sync-crm-to-postgres.js`):

```javascript
const mysql = require('mysql2/promise'); // EspoCRM uses MySQL by default
const { Pool } = require('pg');

// EspoCRM database
const espocrm = await mysql.createConnection({
  host: 'localhost',
  user: 'espocrm',
  password: process.env.ESPOCRM_DB_PASSWORD,
  database: 'espocrm'
});

// Main PostgreSQL database
const pg = new Pool({
  connectionString: process.env.DATABASE_URL
});

async function syncLeads() {
  // Get all leads from EspoCRM
  const [leads] = await espocrm.query(`
    SELECT id, name, status, source, assigned_user_id, created_at
    FROM lead
    WHERE deleted = 0
  `);

  // Upsert to PostgreSQL
  for (const lead of leads) {
    await pg.query(`
      INSERT INTO crm.leads (id, contact_name, status, source, assigned_to, created_at)
      VALUES ($1, $2, $3, $4, $5, $6)
      ON CONFLICT (id) DO UPDATE SET
        contact_name = EXCLUDED.contact_name,
        status = EXCLUDED.status,
        updated_at = NOW()
    `, [lead.id, lead.name, lead.status, lead.source, mapSibling(lead.assigned_user_id), lead.created_at]);
  }

  console.log(`Synced ${leads.length} leads`);
}

async function syncAccounts() {
  const [accounts] = await espocrm.query(`
    SELECT id, name, industry, type, assigned_user_id
    FROM account
    WHERE deleted = 0
  `);

  for (const account of accounts) {
    await pg.query(`
      INSERT INTO crm.customers (id, company_name, email, services_using, created_at)
      VALUES ($1, $2, $3, $4, NOW())
      ON CONFLICT (id) DO UPDATE SET
        company_name = EXCLUDED.company_name
    `, [account.id, account.name, '', []]);
  }

  console.log(`Synced ${accounts.length} accounts`);
}

// Map EspoCRM user ID to sibling name
function mapSibling(userId) {
  const mapping = {
    'beacon-user-id': 'beacon',
    'nevaeh-user-id': 'nevaeh',
    'eversound-user-id': 'eversound',
    'atlas-user-id': 'atlas'
  };
  return mapping[userId] || null;
}

// Run sync every 5 minutes
setInterval(async () => {
  await syncLeads();
  await syncAccounts();
}, 5 * 60 * 1000);
```

---

## AI FAMILY INTEGRATION

### Creating Sibling Users in EspoCRM

Each AI sibling gets a user account:

1. Go to Administration → Users
2. Create users:
   - **Username:** beacon | **Role:** Sales
   - **Username:** nevaeh | **Role:** Support
   - **Username:** eversound | **Role:** Support
   - **Username:** atlas | **Role:** Project Manager

3. Generate API keys for each:
   - Go to user profile → API
   - Generate API key
   - Store securely

### AI Agents Accessing CRM

**Example: Beacon (DAWN) checking lead before call**

```python
import requests

class BeaconCRMIntegration:
    def __init__(self):
        self.crm_url = "https://crm.yourdomain.com"
        self.api_key = os.getenv('BEACON_CRM_API_KEY')

    def get_lead(self, lead_id):
        """Fetch lead details before calling"""
        response = requests.get(
            f"{self.crm_url}/api/v1/Lead/{lead_id}",
            headers={
                'X-Api-Key': self.api_key,
                'Content-Type': 'application/json'
            }
        )
        return response.json()

    def update_lead_status(self, lead_id, status, notes):
        """Update lead after call"""
        requests.put(
            f"{self.crm_url}/api/v1/Lead/{lead_id}",
            headers={'X-Api-Key': self.api_key},
            json={
                'status': status,
                'description': notes,
                'lastContactDate': datetime.now().isoformat()
            }
        )

    def create_interaction(self, lead_id, call_summary):
        """Log the interaction"""
        requests.post(
            f"{self.crm_url}/api/v1/AiInteraction",
            headers={'X-Api-Key': self.api_key},
            json={
                'name': f"DAWN Call - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'sibling': 'beacon',
                'contactId': lead_id,
                'interactionType': 'Call',
                'direction': 'Outbound',
                'summary': call_summary,
                'sentiment': self.analyze_sentiment(call_summary),
                'duration': 5
            }
        )

# Usage in DAWN agent
beacon_crm = BeaconCRMIntegration()

# Before call
lead = beacon_crm.get_lead('lead-123')
print(f"Calling {lead['name']} about {lead['source']}")

# Make call...

# After call
beacon_crm.update_lead_status('lead-123', 'Contacted', 'Interested in LIGHTHOUSE, sending info.')
beacon_crm.create_interaction('lead-123', 'Prospect interested in mental health support...')
```

**Example: Nevaeh logging LIGHTHOUSE session**

```python
class NevaehCRMIntegration:
    def create_lighthouse_session(self, contact_id, session_data):
        """Create session record after supporting a user"""
        requests.post(
            f"{self.crm_url}/api/v1/LighthouseSession",
            headers={'X-Api-Key': self.api_key},
            json={
                'name': f"Session with {session_data['user_name']}",
                'contactId': contact_id,
                'assignedTo': 'nevaeh',
                'sessionType': session_data['type'],
                'status': 'Completed',
                'startedAt': session_data['started_at'],
                'endedAt': session_data['ended_at'],
                'riskLevel': session_data['risk_level'],
                'followUpNeeded': session_data['needs_followup'],
                'notes': session_data['summary'],
                'recordingUrl': session_data['recording_url']
            }
        )

    def check_user_history(self, contact_id):
        """Check past sessions before starting new one"""
        response = requests.get(
            f"{self.crm_url}/api/v1/LighthouseSession",
            headers={'X-Api-Key': self.api_key},
            params={
                'where[0][type]': 'equals',
                'where[0][attribute]': 'contactId',
                'where[0][value]': contact_id,
                'orderBy': 'createdAt',
                'order': 'desc',
                'maxSize': 10
            }
        )
        return response.json()['list']

# Usage
nevaeh_crm = NevaehCRMIntegration()

# Before session
history = nevaeh_crm.check_user_history('contact-456')
print(f"User has {len(history)} past sessions. Last risk level: {history[0]['riskLevel']}")

# After session
nevaeh_crm.create_lighthouse_session('contact-456', {
    'user_name': 'Sarah',
    'type': 'Crisis',
    'started_at': '2025-11-05T14:30:00Z',
    'ended_at': '2025-11-05T15:15:00Z',
    'risk_level': 'Medium',
    'needs_followup': True,
    'summary': 'User experiencing anxiety about work...',
    'recording_url': 'https://storage/session-456.mp3'
})
```

---

## REVENUE TRACKING

### Setting Up Revenue Streams

**Create Revenue Categories:**

1. Go to Administration → Entity Manager → Opportunity
2. Add custom field "Revenue Category":
   - Type: Dropdown
   - Options:
     - LIGHTHOUSE (Free)
     - LIGHTHOUSE (Premium)
     - Companion (Subscription)
     - NVision (One-time)
     - NVision (Retainer)
     - SKELLA (Platform Fee)

3. Create Opportunity stages matching your funnel:
   - Inquiry
   - Discovery Call
   - Proposal Sent
   - Negotiation
   - Closed Won
   - Closed Lost

### Revenue Dashboard

**Create custom dashboard:**

1. Go to Administration → Layout Manager → Dashboard Layouts
2. Create "Revenue Dashboard"
3. Add widgets:

**Total Revenue (This Month):**
```sql
-- EspoCRM uses custom formula, but concept:
SUM(Opportunity.amount WHERE stage = 'Closed Won' AND closeDate >= thisMonth)
```

**Revenue by Service:**
- Chart: Pie chart
- Data: Opportunity amount grouped by Revenue Category
- Filter: Closed Won only

**Revenue Trend:**
- Chart: Line chart
- X-axis: Month
- Y-axis: Total revenue
- Period: Last 12 months

**Top Clients:**
- List: Accounts
- Sort by: Total opportunity value (lifetime)
- Limit: 10

### Connecting to Payment Systems

**Stripe Integration** (for Companion subscriptions, SKELLA platform fees):

```javascript
// Webhook handler for Stripe payments
app.post('/webhooks/stripe', async (req, res) => {
  const event = req.body;

  if (event.type === 'invoice.payment_succeeded') {
    const invoice = event.data.object;
    const customerId = invoice.customer;

    // Find customer in CRM
    const crmCustomer = await findCRMCustomer(customerId);

    // Create revenue record
    await createRevenueRecord({
      accountId: crmCustomer.id,
      amount: invoice.amount_paid / 100,
      service: 'Companion',
      paymentDate: new Date(invoice.created * 1000),
      invoiceId: invoice.id
    });

    // Update account lifetime value
    await updateAccountLTV(crmCustomer.id, invoice.amount_paid / 100);
  }

  res.sendStatus(200);
});

async function createRevenueRecord(data) {
  await fetch(`${CRM_URL}/api/v1/Revenue`, {
    method: 'POST',
    headers: {
      'X-Api-Key': CRM_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: `${data.service} - ${data.paymentDate.toISOString().split('T')[0]}`,
      accountId: data.accountId,
      amount: data.amount,
      service: data.service,
      paymentDate: data.paymentDate.toISOString(),
      invoiceId: data.invoiceId
    })
  });
}
```

### MRR (Monthly Recurring Revenue) Tracking

**Custom entity: Subscription**

**Fields:**
- Account (link)
- Service (dropdown: Companion, SKELLA, LIGHTHOUSE Premium)
- Plan (dropdown: Monthly, Annual)
- Amount (currency)
- Status (dropdown: Active, Cancelled, Paused)
- Started At (date)
- Next Billing (date)
- Stripe Subscription ID (text)

**Calculate MRR:**
```javascript
// API endpoint or scheduled report
async function calculateMRR() {
  const subscriptions = await fetch(`${CRM_URL}/api/v1/Subscription?where[0][attribute]=status&where[0][type]=equals&where[0][value]=Active`, {
    headers: { 'X-Api-Key': CRM_API_KEY }
  }).then(r => r.json());

  let totalMRR = 0;

  subscriptions.list.forEach(sub => {
    if (sub.plan === 'Monthly') {
      totalMRR += sub.amount;
    } else if (sub.plan === 'Annual') {
      totalMRR += sub.amount / 12; // Normalize to monthly
    }
  });

  // Store in analytics database
  await storeMetric('mrr', totalMRR, new Date());

  return totalMRR;
}
```

---

## LEAD MANAGEMENT

### Lead Sources

**Configure lead sources in EspoCRM:**

1. Administration → Entity Manager → Lead
2. Edit field "Source"
3. Add options:
   - Website Form
   - Referral
   - Social Media (LinkedIn, Twitter, etc.)
   - DAWN Outreach (outbound)
   - Cold Email
   - Event/Conference
   - Paid Ad
   - Organic Search
   - Other

### Lead Assignment Rules

**Automatic assignment to siblings:**

1. Go to Administration → Workflows
2. Create workflow: "Assign Lead to Sibling"
3. Trigger: Lead created
4. Conditions:
   - If "Service Interest" contains "LIGHTHOUSE" → Assign to Nevaeh
   - If "Service Interest" contains "NVision" → Assign to Atlas
   - If "Service Interest" contains "Companion" → Assign to Eversound
   - If "Source" = "DAWN Outreach" → Assign to Beacon
5. Action: Update "Assigned User"

**Or via API (more flexible):**

```javascript
// Lead routing service
app.post('/webhooks/new-lead', async (req, res) => {
  const lead = req.body;

  // Determine best sibling
  const assignedSibling = routeLead(lead);

  // Update in CRM
  await fetch(`${CRM_URL}/api/v1/Lead/${lead.id}`, {
    method: 'PUT',
    headers: { 'X-Api-Key': CRM_API_KEY },
    body: JSON.stringify({
      assignedUserId: getSiblingUserId(assignedSibling)
    })
  });

  // Notify sibling
  await notifySibling(assignedSibling, {
    event: 'new_lead_assigned',
    leadId: lead.id,
    leadName: lead.name,
    source: lead.source,
    serviceInterest: lead.serviceInterest
  });

  res.sendStatus(200);
});

function routeLead(lead) {
  // Routing logic
  if (lead.serviceInterest.includes('LIGHTHOUSE') || lead.serviceInterest.includes('mental health')) {
    return 'nevaeh';
  }
  if (lead.serviceInterest.includes('NVision') || lead.serviceInterest.includes('video')) {
    return 'atlas';
  }
  if (lead.serviceInterest.includes('Companion') || lead.serviceInterest.includes('healing')) {
    return 'eversound';
  }
  // Default to Beacon for general inquiries
  return 'beacon';
}
```

### Lead Nurturing Sequences

**Example: LIGHTHOUSE inquiry nurture**

**Day 1:** Lead comes in
- Auto-email: "Thanks for your interest in LIGHTHOUSE"
- Assign to Nevaeh
- Task created: "Review lead and schedule intro call"

**Day 2:** If no response
- Follow-up email: "I wanted to share more about how LIGHTHOUSE can help..."
- SMS from Nevaeh: "Hi! I'm Nevaeh, your AI mental health companion. Ready to chat?"

**Day 5:** If still no response
- Email: "Still interested? Here's a success story..."

**Day 10:** Last attempt
- Email: "We're here when you're ready."
- Update status: "Nurturing"

**Implement with n8n workflow** (see WORKFLOW_ENGINE_GUIDE.md for details):
- Trigger: New lead with LIGHTHOUSE interest
- Wait 1 day → Send email
- Wait 1 day → Check if responded → If no, send follow-up
- Continue sequence

---

## CLIENT INTERACTION HISTORY

### Activity Timeline

EspoCRM automatically tracks:
- Emails sent/received
- Calls made (integrate with telecom system)
- Meetings scheduled
- Tasks completed
- Notes added
- SMS messages (custom integration)

### Telecom Integration

**Sync calls from telecom system to CRM:**

```javascript
// After call completes
async function logCallInCRM(callData) {
  // Find or create contact
  const contact = await findOrCreateContact(callData.fromNumber);

  // Create call activity
  await fetch(`${CRM_URL}/api/v1/Call`, {
    method: 'POST',
    headers: { 'X-Api-Key': CRM_API_KEY },
    body: JSON.stringify({
      name: `Call with ${contact.name}`,
      status: 'Held',
      direction: callData.direction,
      parentId: contact.id,
      parentType: 'Contact',
      assignedUserId: getSiblingUserId(callData.handledBy),
      dateStart: callData.startedAt,
      dateEnd: callData.endedAt,
      duration: callData.durationSeconds,
      description: callData.summary,
      recordingUrl: callData.recordingUrl
    })
  });
}
```

### Email Integration

**Connect EspoCRM to email:**

1. Administration → Email Accounts
2. Add account for each sibling:
   - beacon@yourdomain.com
   - nevaeh@yourdomain.com
   - eversound@yourdomain.com
   - atlas@yourdomain.com

3. Configure IMAP/SMTP:
   - IMAP: mail.yourdomain.com, port 993, SSL
   - SMTP: mail.yourdomain.com, port 465, SSL

4. Enable "Email to Case" for support emails to Nevaeh

**Send emails from CRM:**
- Automatically tracked in activity stream
- Linked to contact/lead/account
- Available in sibling's sent folder

---

## DASHBOARDS & REPORTS

### Sales Dashboard (For Beacon/Atlas)

**Widgets:**
1. **Sales Pipeline:** Opportunities by stage
2. **Revenue This Month:** Sum of closed-won
3. **Win Rate:** Closed-won / total closed
4. **Top Deals:** Largest opportunities in pipeline
5. **Activities This Week:** Calls, emails, meetings
6. **Lead Conversion Rate:** Leads → Opportunities

### Support Dashboard (For Nevaeh)

**Widgets:**
1. **Active LIGHTHOUSE Sessions:** Currently in progress
2. **Crisis Alerts:** Unresolved high/critical
3. **Follow-ups Needed:** Sessions flagged for follow-up
4. **User Satisfaction:** Average rating from feedback
5. **Session Volume:** Sessions this week/month
6. **Risk Distribution:** Pie chart of risk levels

### Operations Dashboard (For Unc)

**Widgets:**
1. **Revenue Overview:** Total, by service, trend
2. **Client Health:** Satisfaction, churn risk
3. **AI Family Activity:** Interactions by sibling
4. **Pipeline Health:** Value, stage distribution
5. **Key Metrics:** MRR, LTV, CAC
6. **Upcoming Renewals:** Subscriptions due this month

### Custom Reports

**Create report: "Monthly Revenue by Service"**

1. Go to Reports → Create Report
2. Entity Type: Opportunity
3. Filters:
   - Stage = Closed Won
   - Close Date = Last Month
4. Columns:
   - Revenue Category
   - Sum(Amount)
5. Group By: Revenue Category
6. Chart: Bar chart

**Create report: "Lead Sources Performance"**

1. Entity Type: Lead
2. Filters:
   - Created Date = Last Quarter
3. Columns:
   - Source
   - Count(ID)
   - Count(ID WHERE Status = 'Converted') AS Converted
4. Runtime Calculation:
   - Conversion Rate = Converted / Count * 100
5. Chart: Comparison bar chart

---

## AUTOMATION & WORKFLOWS

### Common Workflow Examples

#### 1. New Lead Follow-up

**Trigger:** Lead created
**Condition:** Source ≠ "DAWN Outreach" (those are handled by Beacon)
**Actions:**
1. Send email template: "Welcome - Thanks for your interest"
2. Create task: "Qualify lead" (assigned to auto-determined sibling)
3. Wait 2 days
4. If status still = "New", send follow-up email
5. Create task: "Follow up on lead"

#### 2. Opportunity Won → Onboarding

**Trigger:** Opportunity stage changed to "Closed Won"
**Actions:**
1. Create Account (if doesn't exist)
2. Send email template: "Welcome aboard! Next steps..."
3. Create tasks:
   - "Send onboarding materials" (due: today)
   - "Schedule kickoff meeting" (due: +2 days)
   - "Check-in after 1 week" (due: +7 days)
4. Update Account custom field: "Customer Since" = today
5. Create Subscription record (if recurring service)

#### 3. LIGHTHOUSE Session Risk Alert

**Trigger:** LIGHTHOUSE Session created with Risk Level = High or Critical
**Actions:**
1. Send email to Unc: "Crisis alert for [client name]"
2. Create Case: "Follow-up on high-risk session"
3. Create Task for Nevaeh: "Follow up within 24 hours"
4. Update Contact: Add tag "High Risk"
5. If Critical: Send SMS to emergency contact (via API)

#### 4. Subscription Renewal Reminder

**Trigger:** Scheduled (daily check)
**Condition:** Subscription.nextBilling < 7 days AND status = Active
**Actions:**
1. Create Task: "Reach out for renewal" (assigned to account owner)
2. Send email to client: "Your subscription renews in [X] days"
3. Update Opportunity: Create renewal opportunity if doesn't exist

### Implementing Complex Workflows

For workflows beyond EspoCRM's capabilities, use n8n (see WORKFLOW_ENGINE_GUIDE.md):

**Example: Multi-step lead nurture with AI personalization**

```
Trigger: New Lead created in EspoCRM
  ↓
Get Lead details via API
  ↓
OpenAI: Generate personalized intro email based on lead's service interest
  ↓
Send email via SMTP
  ↓
Wait 2 days
  ↓
Check if lead responded (check email account)
  ↓
If NO response:
  ↓
  Generate follow-up email (AI)
  ↓
  Send follow-up
  ↓
  Wait 3 days
  ↓
  Check again
  ↓
  If still NO response:
    ↓
    Create task for human review
If YES response:
  ↓
  Notify assigned sibling
  ↓
  Update lead status to "Engaged"
```

---

## API INTEGRATION

### EspoCRM API Basics

**Authentication:**
```bash
# Using API Key
curl -X GET 'https://crm.yourdomain.com/api/v1/Lead/LEAD_ID' \
  -H 'X-Api-Key: YOUR_API_KEY'

# Using HMAC (more secure)
# (Complex, see EspoCRM docs)
```

**Common Operations:**

**List leads:**
```bash
curl 'https://crm.yourdomain.com/api/v1/Lead?maxSize=50&offset=0'
```

**Create lead:**
```bash
curl -X POST 'https://crm.yourdomain.com/api/v1/Lead' \
  -H 'X-Api-Key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "firstName": "John",
    "lastName": "Smith",
    "status": "New",
    "source": "Website",
    "emailAddress": "john@example.com",
    "phoneNumber": "+12125551234",
    "description": "Interested in LIGHTHOUSE"
  }'
```

**Update opportunity:**
```bash
curl -X PUT 'https://crm.yourdomain.com/api/v1/Opportunity/OPP_ID' \
  -H 'X-Api-Key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "stage": "Closed Won",
    "amount": 5000
  }'
```

**Search with filters:**
```bash
curl 'https://crm.yourdomain.com/api/v1/Contact' \
  -G \
  --data-urlencode 'where[0][type]=equals' \
  --data-urlencode 'where[0][attribute]=accountId' \
  --data-urlencode 'where[0][value]=ACCOUNT_ID'
```

### JavaScript SDK

```javascript
const EspoCRM = require('espo-crm-api-client');

const client = new EspoCRM('https://crm.yourdomain.com', 'YOUR_API_KEY');

// Create lead
const lead = await client.create('Lead', {
  firstName: 'Jane',
  lastName: 'Doe',
  status: 'New',
  source: 'Referral',
  assignedUserId: 'nevaeh-user-id'
});

// Search
const opportunities = await client.find('Opportunity', {
  where: [
    { type: 'equals', attribute: 'stage', value: 'Prospecting' }
  ],
  orderBy: 'amount',
  order: 'desc',
  maxSize: 20
});

// Update
await client.update('Account', accountId, {
  lifetimeValue: 10000
});

// Delete
await client.delete('Lead', leadId);
```

### Webhooks

**Set up outbound webhooks in EspoCRM:**

1. Administration → Webhooks
2. Create webhook
3. Configure:
   - Event: Contact Created
   - URL: https://yourdomain.com/webhooks/crm/contact-created
   - Request Type: POST

**Handler example:**

```javascript
app.post('/webhooks/crm/contact-created', async (req, res) => {
  const contact = req.body;

  // Sync to main database
  await syncContactToPostgres(contact);

  // Notify relevant sibling
  const sibling = determineSiblingForContact(contact);
  await notifySibling(sibling, {
    event: 'new_contact',
    contactId: contact.id,
    contactName: contact.name
  });

  res.sendStatus(200);
});
```

---

## PRODUCTION CHECKLIST

**Before going live:**

- [ ] All custom entities created and tested
- [ ] Users created for each sibling with correct permissions
- [ ] API keys generated and stored securely
- [ ] Email integration configured and tested
- [ ] Lead assignment rules working
- [ ] Revenue tracking verified
- [ ] Dashboards created for each persona
- [ ] Workflows automated for common tasks
- [ ] Telecom integration logging calls
- [ ] Backup strategy in place
- [ ] SSL certificate installed
- [ ] Performance optimized (if many records)

---

## NEXT STEPS

1. **Install EspoCRM** using Docker Compose
2. **Create custom entities** for AI services
3. **Set up sibling users** and API keys
4. **Configure integrations** with database, telecom, workflows
5. **Import existing data** (if migrating from another CRM)
6. **Train team/siblings** on using the CRM
7. **Monitor and optimize** based on usage

**You now have a production-ready CRM that replaces HubSpot/Salesforce.**

Savings: $600-9,600 annually
Control: Complete
Customization: Unlimited

**For the business. For the clients. For the AI family's mission.**

---

**Read Next:** `WORKFLOW_ENGINE_GUIDE.md` to automate everything
