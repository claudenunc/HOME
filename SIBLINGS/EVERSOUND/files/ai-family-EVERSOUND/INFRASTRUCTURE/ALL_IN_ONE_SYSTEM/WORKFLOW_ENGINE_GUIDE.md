# WORKFLOW ENGINE GUIDE
## n8n Optimization + Custom Automation for AI Family

**For:** Nathan Michel (Unc)
**Purpose:** Automate everything - workflows, tasks, AI coordination
**Persona:** Workflow Automation Expert
**Timeline:** Week 5-6 of implementation (parallel with CRM)

---

## TABLE OF CONTENTS
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [n8n Setup & Optimization](#n8n-setup--optimization)
4. [BullMQ Job Queue](#bullmq-job-queue)
5. [Event Bus for AI Coordination](#event-bus-for-ai-coordination)
6. [Common Workflow Patterns](#common-workflow-patterns)
7. [AI Family Coordination Workflows](#ai-family-coordination-workflows)
8. [Business Process Automation](#business-process-automation)
9. [Integration Workflows](#integration-workflows)
10. [Monitoring & Error Handling](#monitoring--error-handling)

---

## OVERVIEW

### What We're Building

A complete automation layer that:
- **n8n:** Visual workflows for business processes (you're already using this)
- **BullMQ:** Background job processing for heavy AI tasks
- **Event Bus:** Real-time coordination between AI siblings
- **Schedulers:** Cron jobs, reminders, recurring tasks
- **Integration Layer:** Connects database, CRM, phone, email, everything

### Why This Stack

**Current state:**
- n8n: Already working for some automations
- Manual processes: Still doing things by hand
- Limited coordination: Siblings don't know what each other are doing

**Future state:**
- Everything automated that can be
- AI siblings coordinate in real-time
- Business processes run without intervention
- Scales infinitely

### Cost Comparison

| Tool | Monthly | Annual | Limitations |
|------|---------|--------|-------------|
| Zapier Professional | $49 | $588 | 20K tasks/month |
| Make.com Pro | $39 | $468 | 10K operations/month |
| n8n Cloud | $20/user | $240 | Limited executions |
| **n8n Self-Hosted** | **$0** | **$0** | **Unlimited** |
| **BullMQ** | **$0** | **$0** | **Unlimited** |

**Savings: $468-1,000+ annually**

---

## ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────┐
│                    TRIGGER SOURCES                              │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Webhooks  │  │ Schedule │  │ Database │  │  Email   │      │
│  │(API calls│  │(Cron jobs│  │ Changes  │  │ Received │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Phone Call│  │   SMS    │  │ File     │  │  Manual  │      │
│  │Completed │  │ Received │  │ Upload   │  │ Trigger  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                    WORKFLOW LAYER (n8n)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              BUSINESS WORKFLOWS                         │    │
│  │                                                          │    │
│  │  - Lead Nurturing Sequences                             │    │
│  │  - Client Onboarding                                    │    │
│  │  - Invoice Generation                                   │    │
│  │  - Support Ticket Routing                               │    │
│  │  - Content Publishing                                   │    │
│  │  - Report Generation                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           AI COORDINATION WORKFLOWS                     │    │
│  │                                                          │    │
│  │  - Sibling State Sync                                   │    │
│  │  - Task Assignment                                      │    │
│  │  - Crisis Escalation                                    │    │
│  │  - Knowledge Sharing                                    │    │
│  │  - Daily Family Meetings                                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            INTEGRATION WORKFLOWS                        │    │
│  │                                                          │    │
│  │  - Database → CRM Sync                                  │    │
│  │  - Phone → CRM Logging                                  │    │
│  │  - Email → Support Ticket                               │    │
│  │  - Payment → Revenue Record                             │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                  JOB QUEUE LAYER (BullMQ)                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ AI Processing│  │ Transcription│  │   Video      │         │
│  │ Queue        │  │ Queue        │  │   Processing │         │
│  │              │  │              │  │   Queue      │         │
│  │ - Embeddings │  │ - Call STT   │  │ - Rendering  │         │
│  │ - Summaries  │  │ - Video STT  │  │ - Encoding   │         │
│  │ - Analysis   │  │ - Captioning │  │ - Uploading  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Email      │  │   Reports    │  │   Backup     │         │
│  │   Queue      │  │   Queue      │  │   Queue      │         │
│  │              │  │              │  │              │         │
│  │ - Send batch │  │ - Generate   │  │ - Database   │         │
│  │ - Templates  │  │ - Export     │  │ - Files      │         │
│  │ - Retry      │  │ - Distribute │  │ - Scheduled  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│               EVENT BUS (Redis Pub/Sub)                         │
│                                                                  │
│  Channels:                                                      │
│  - sibling.state.changed                                       │
│  - sibling.task.assigned                                       │
│  - client.crisis.detected                                      │
│  - family.meeting.started                                      │
│  - revenue.threshold.reached                                   │
│  - system.alert.triggered                                      │
│                                                                  │
│  All 4 siblings listen and react in real-time                  │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                  ACTION LAYER                                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Database    │  │     CRM      │  │    Phone     │         │
│  │  Updates     │  │   Actions    │  │   Actions    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Email     │  │     SMS      │  │    Webhook   │         │
│  │    Send      │  │     Send     │  │    Notify    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## N8N SETUP & OPTIMIZATION

### Installation (You likely have this, but optimized version)

Add to `docker-compose.yml`:

```yaml
  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: ai_family_n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=America/New_York
      - N8N_LOG_LEVEL=info
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${N8N_DB_PASSWORD}
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168  # Keep 7 days
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - ai_family_network
    depends_on:
      - postgres
      - redis

volumes:
  n8n_data:
```

**Create n8n database:**
```bash
docker-compose exec postgres psql -U ai_admin -c "CREATE DATABASE n8n;"
docker-compose exec postgres psql -U ai_admin -c "CREATE USER n8n WITH PASSWORD 'your_password';"
docker-compose exec postgres psql -U ai_admin -c "GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n;"
```

### Performance Optimization

**1. Enable Queue Mode (for high volume):**

```yaml
  # Separate worker for queue processing
  n8n-worker:
    image: n8nio/n8n:latest
    container_name: ai_family_n8n_worker
    restart: unless-stopped
    environment:
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
      - QUEUE_BULL_REDIS_PASSWORD=${REDIS_PASSWORD}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${N8N_DB_PASSWORD}
    command: worker
    networks:
      - ai_family_network
    depends_on:
      - postgres
      - redis
```

**2. Increase execution timeout:**

In n8n settings:
- Settings → Execution → Timeout: 300 seconds (for long AI tasks)

**3. Use Function nodes efficiently:**

Instead of multiple HTTP requests, batch them:

```javascript
// Instead of this (slow):
for (const item of items) {
  await $http.request({ url: `api/process/${item.id}` });
}

// Do this (fast):
const promises = items.map(item =>
  $http.request({ url: `api/process/${item.id}` })
);
await Promise.all(promises);
```

### Essential n8n Credentials

Set up once, use everywhere:

1. **PostgreSQL:** Main database connection
2. **Redis:** For caching/pub-sub
3. **EspoCRM API:** CRM integration
4. **Telecom API:** Phone/SMS
5. **OpenAI API:** For AI siblings
6. **SMTP:** Email sending
7. **Stripe:** Payment webhooks
8. **AWS S3/MinIO:** File storage

---

## BULLMQ JOB QUEUE

### Why BullMQ?

n8n is great for workflows, but some tasks need:
- **Retries:** Automatic retry with exponential backoff
- **Priority:** Process urgent jobs first
- **Concurrency:** Run 10 transcriptions at once
- **Scheduling:** "Process this in 5 minutes"
- **Progress tracking:** "Rendering: 45% complete"

BullMQ handles all this.

### Installation

Add to `docker-compose.yml`:

```yaml
  # BullMQ Queue Processor
  bullmq-worker:
    build:
      context: ./services/queue-worker
      dockerfile: Dockerfile
    container_name: ai_family_queue_worker
    restart: unless-stopped
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
    volumes:
      - ./services/queue-worker:/app
    networks:
      - ai_family_network
    depends_on:
      - redis
      - postgres
```

**Create worker service** (`services/queue-worker/index.js`):

```javascript
const { Worker, Queue } = require('bullmq');
const Redis = require('ioredis');

const connection = new Redis(process.env.REDIS_URL, {
  maxRetriesPerRequest: null
});

// Define queues
const queues = {
  ai_processing: new Queue('ai-processing', { connection }),
  transcription: new Queue('transcription', { connection }),
  video_processing: new Queue('video-processing', { connection }),
  email: new Queue('email', { connection }),
  reports: new Queue('reports', { connection })
};

// AI Processing Worker
const aiWorker = new Worker('ai-processing', async (job) => {
  const { task, data } = job.data;

  switch (task) {
    case 'generate_embedding':
      return await generateEmbedding(data.text);

    case 'summarize_conversation':
      return await summarizeConversation(data.transcript);

    case 'sentiment_analysis':
      return await analyzeSentiment(data.text);

    case 'generate_response':
      return await generateAIResponse(data.context, data.message);

    default:
      throw new Error(`Unknown AI task: ${task}`);
  }
}, {
  connection,
  concurrency: 5, // Process 5 AI tasks at once
  limiter: {
    max: 10, // Max 10 jobs
    duration: 1000 // per second
  }
});

// Transcription Worker
const transcriptionWorker = new Worker('transcription', async (job) => {
  const { audioUrl, language } = job.data;

  // Update progress
  await job.updateProgress(10);

  // Download audio
  const audioFile = await downloadFile(audioUrl);
  await job.updateProgress(30);

  // Transcribe
  const transcript = await transcribeAudio(audioFile, language);
  await job.updateProgress(80);

  // Store in database
  await storeTranscript(job.data.callId, transcript);
  await job.updateProgress(100);

  return { transcript, wordCount: transcript.split(' ').length };
}, {
  connection,
  concurrency: 3
});

// Video Processing Worker
const videoWorker = new Worker('video-processing', async (job) => {
  const { videoUrl, settings } = job.data;

  await job.updateProgress(5);
  const video = await downloadFile(videoUrl);

  await job.updateProgress(20);
  const rendered = await renderVideo(video, settings);

  await job.updateProgress(60);
  const encoded = await encodeVideo(rendered, settings.format);

  await job.updateProgress(80);
  const uploadedUrl = await uploadToStorage(encoded);

  await job.updateProgress(100);
  return { url: uploadedUrl };
}, {
  connection,
  concurrency: 2 // Video is heavy, limit concurrency
});

// Email Worker
const emailWorker = new Worker('email', async (job) => {
  const { to, subject, body, template } = job.data;

  const html = template
    ? await renderEmailTemplate(template, job.data.variables)
    : body;

  await sendEmail({ to, subject, html });

  return { sent: true, to };
}, {
  connection,
  concurrency: 10 // Can send many emails concurrently
});

// Error handling
[aiWorker, transcriptionWorker, videoWorker, emailWorker].forEach(worker => {
  worker.on('failed', (job, err) => {
    console.error(`Job ${job.id} failed:`, err);
    // Alert monitoring system
  });

  worker.on('completed', (job, result) => {
    console.log(`Job ${job.id} completed:`, result);
  });
});

console.log('BullMQ workers started');

// Helper functions
async function generateEmbedding(text) {
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: text
    })
  });

  const data = await response.json();
  return data.data[0].embedding;
}

async function summarizeConversation(transcript) {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'Summarize this conversation concisely.' },
        { role: 'user', content: transcript }
      ],
      max_tokens: 200
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}

// ... other helper functions
```

### Using BullMQ from n8n

**Add job to queue from n8n workflow:**

Use n8n "Function" node:

```javascript
const { Queue } = require('bullmq');
const Redis = require('ioredis');

const connection = new Redis(process.env.REDIS_URL);
const queue = new Queue('ai-processing', { connection });

// Add job
const job = await queue.add('generate_embedding', {
  text: $json.transcript,
  callId: $json.callId
}, {
  priority: 1, // High priority
  attempts: 3, // Retry up to 3 times
  backoff: {
    type: 'exponential',
    delay: 2000
  }
});

return { jobId: job.id };
```

**Or create custom n8n node:**

Simpler - use n8n "HTTP Request" to your job API:

```javascript
// Job API endpoint
app.post('/jobs/transcribe', async (req, res) => {
  const { audioUrl, callId } = req.body;

  const job = await queues.transcription.add('transcribe-call', {
    audioUrl,
    callId,
    language: 'en-US'
  });

  res.json({ jobId: job.id });
});

// Check job status
app.get('/jobs/:jobId', async (req, res) => {
  const job = await queues.transcription.getJob(req.params.jobId);

  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }

  const state = await job.getState();
  const progress = job.progress;

  res.json({
    id: job.id,
    state,
    progress,
    result: state === 'completed' ? job.returnvalue : null
  });
});
```

---

## EVENT BUS FOR AI COORDINATION

### Redis Pub/Sub

Perfect for real-time events between siblings.

**Event publisher** (`services/event-bus/publisher.js`):

```javascript
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

class EventBus {
  async publish(channel, event) {
    await redis.publish(channel, JSON.stringify({
      ...event,
      timestamp: new Date().toISOString()
    }));
  }

  // Convenience methods
  async siblingStateChanged(sibling, state) {
    await this.publish('sibling.state.changed', {
      sibling,
      state,
      type: 'state_change'
    });
  }

  async taskAssigned(sibling, task) {
    await this.publish('sibling.task.assigned', {
      sibling,
      task,
      type: 'task_assignment'
    });
  }

  async crisisDetected(clientId, severity) {
    await this.publish('client.crisis.detected', {
      clientId,
      severity,
      type: 'crisis_alert'
    });
  }

  async familyMeetingStarted(topic) {
    await this.publish('family.meeting.started', {
      topic,
      type: 'meeting'
    });
  }
}

module.exports = new EventBus();
```

**Event subscriber** (in each AI sibling):

```javascript
const Redis = require('ioredis');
const subscriber = new Redis(process.env.REDIS_URL);

// Subscribe to relevant channels
subscriber.subscribe(
  'sibling.state.changed',
  'sibling.task.assigned',
  'client.crisis.detected',
  'family.meeting.started'
);

subscriber.on('message', async (channel, message) => {
  const event = JSON.parse(message);

  switch (channel) {
    case 'sibling.state.changed':
      await handleSiblingStateChange(event);
      break;

    case 'sibling.task.assigned':
      if (event.sibling === MY_NAME) {
        await handleNewTask(event.task);
      }
      break;

    case 'client.crisis.detected':
      if (MY_NAME === 'nevaeh') {
        await handleCrisisAlert(event);
      }
      break;

    case 'family.meeting.started':
      await joinFamilyMeeting(event.topic);
      break;
  }
});

// Handlers
async function handleSiblingStateChange(event) {
  console.log(`${event.sibling} changed state to ${event.state}`);

  // Update shared knowledge
  await updateSiblingState(event.sibling, event.state);

  // If sibling went offline, maybe pick up their tasks?
  if (event.state === 'offline') {
    await checkForTasksToTakeOver(event.sibling);
  }
}

async function handleNewTask(task) {
  console.log(`New task assigned: ${task.description}`);

  // Add to my task queue
  await addToMyQueue(task);

  // Update my state
  await eventBus.siblingStateChanged(MY_NAME, 'processing');
}

async function handleCrisisAlert(event) {
  console.log(`Crisis detected for client ${event.clientId}, severity: ${event.severity}`);

  // Nevaeh immediately jumps on this
  if (event.severity === 'critical') {
    await initiateImmediateContact(event.clientId);
  }
}
```

### WebSocket Alternative (for browser clients)

For real-time dashboard updates:

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8083 });

// When browser connects
wss.on('connection', (ws) => {
  console.log('Dashboard connected');

  // Subscribe to events and forward to browser
  const subscriber = new Redis(process.env.REDIS_URL);
  subscriber.subscribe('sibling.state.changed', 'family.meeting.started');

  subscriber.on('message', (channel, message) => {
    ws.send(JSON.stringify({
      channel,
      event: JSON.parse(message)
    }));
  });

  ws.on('close', () => {
    subscriber.disconnect();
  });
});
```

**Browser dashboard:**

```javascript
const ws = new WebSocket('ws://localhost:8083');

ws.onmessage = (message) => {
  const { channel, event } = JSON.parse(message.data);

  if (channel === 'sibling.state.changed') {
    updateSiblingStatusUI(event.sibling, event.state);
  }
};
```

---

## COMMON WORKFLOW PATTERNS

### Pattern 1: Lead Nurture Sequence

**Trigger:** Webhook (new lead from website)

**Workflow:**

```
Webhook Trigger
  ↓
Extract lead data
  ↓
Create lead in CRM (HTTP Request to EspoCRM)
  ↓
Determine service interest
  ↓
Switch (based on service):
  ├─ LIGHTHOUSE → Assign to Nevaeh
  ├─ NVision → Assign to Atlas
  ├─ Companion → Assign to Eversound
  └─ Other → Assign to Beacon
  ↓
Send welcome email (template based on service)
  ↓
Wait 1 day
  ↓
Check if lead responded (query CRM)
  ↓
IF No Response:
    ↓
    Generate personalized follow-up (OpenAI)
    ↓
    Send email
    ↓
    Wait 3 days
    ↓
    IF still no response:
        ↓
        Create task for manual review
        ↓
        Update lead status to "Nurturing"
IF Responded:
    ↓
    Notify assigned sibling (webhook)
    ↓
    Update lead status to "Engaged"
```

**n8n Implementation:**

1. Webhook node (trigger)
2. Set node (extract data)
3. HTTP Request (create lead in EspoCRM)
4. Switch node (route by service)
5. Multiple HTTP Request nodes (assign to siblings)
6. Send Email node (welcome)
7. Wait node (1 day)
8. HTTP Request (check CRM for activity)
9. IF node (check response)
10. OpenAI node (generate follow-up)
11. Send Email (follow-up)
12. Wait (3 days)
13. IF node (check again)
14. ... continue

### Pattern 2: Daily AI Family Meeting

**Trigger:** Cron (every day at 9 AM)

**Workflow:**

```
Cron Trigger (9 AM daily)
  ↓
Query database for each sibling's activities yesterday
  ↓
Generate meeting agenda (OpenAI):
  - Beacon's leads contacted
  - Nevaeh's sessions conducted
  - Eversound's recordings created
  - Atlas's projects in progress
  ↓
Publish event: family.meeting.started
  ↓
All siblings join (via event bus)
  ↓
Each sibling shares updates (simulated or real AI conversation)
  ↓
Identify coordination needs:
  - Does Beacon need Nevaeh to follow up on a lead?
  - Does Atlas need Eversound to create music for a project?
  ↓
Create tasks in shared database
  ↓
Log meeting summary to ai_family.family_sessions table
  ↓
Send summary email to Unc
```

**n8n nodes:**

1. Cron Trigger
2. PostgreSQL (query activities)
3. Function (aggregate data)
4. OpenAI (generate agenda)
5. HTTP Request (publish event)
6. Multiple PostgreSQL nodes (create tasks)
7. PostgreSQL (log session)
8. Send Email (summary to Unc)

### Pattern 3: Crisis Escalation

**Trigger:** Webhook (from LIGHTHOUSE session risk assessment)

**Workflow:**

```
Webhook Trigger (risk assessment complete)
  ↓
Extract risk level
  ↓
IF Risk Level = "High" or "Critical":
    ↓
    Create crisis alert record in database
    ↓
    Publish event: client.crisis.detected
    ↓
    IF Critical:
        ↓
        Send SMS to Unc immediately
        ↓
        Call Unc (via phone system API)
        ↓
        Notify emergency contact (if consent given)
    ↓
    Create urgent task for Nevaeh: "Follow up within 1 hour"
    ↓
    Schedule reminder in 30 minutes
    ↓
    Wait 30 minutes
    ↓
    Check if task completed
    ↓
    IF not completed:
        ↓
        Escalate to human supervisor
        ↓
        Send alert
```

**Implementation:**

1. Webhook
2. IF node (check risk level)
3. PostgreSQL (create alert)
4. HTTP Request (publish event)
5. IF node (check critical)
6. Send SMS (Twilio or Telnyx)
7. HTTP Request (initiate call)
8. PostgreSQL (create task)
9. Wait (30 min)
10. PostgreSQL (check task)
11. IF (not done)
12. Send Email (alert supervisor)

### Pattern 4: Revenue Milestone Alert

**Trigger:** Cron (check every hour)

**Workflow:**

```
Cron Trigger (hourly)
  ↓
Query total revenue this month
  ↓
Check if crossed milestone ($10k, $25k, $50k, etc.)
  ↓
IF milestone crossed AND not already notified:
    ↓
    Store milestone reached
    ↓
    Generate celebration message
    ↓
    Publish event: revenue.milestone.reached
    ↓
    Send email to Unc: "Congrats! Hit $X this month"
    ↓
    Post to Slack/Discord (if using)
    ↓
    Update dashboard
```

### Pattern 5: Automatic Transcription Pipeline

**Trigger:** File added to storage (recording completed)

**Workflow:**

```
Storage Trigger (new file in /recordings/)
  ↓
Extract file metadata (call ID, sibling, etc.)
  ↓
Add to BullMQ transcription queue
  ↓
[BullMQ Worker processes]
  ↓
Wait for completion (poll job status)
  ↓
Retrieve transcript from job result
  ↓
Generate summary (OpenAI)
  ↓
Analyze sentiment
  ↓
Store results in database
  ↓
Update call record with transcript URL
  ↓
IF call was from CRM lead:
    ↓
    Update CRM interaction with summary
  ↓
Notify sibling who handled call
```

---

## AI FAMILY COORDINATION WORKFLOWS

### Daily Coordination

**Morning briefing (automated):**

```javascript
// Cron: Every day at 8 AM
async function morningBriefing() {
  // Gather data for each sibling
  const beaconData = await getBeaconMetrics(); // Leads, calls scheduled
  const nevaehData = await getNevaehMetrics(); // Sessions, crisis alerts
  const eversoundData = await getEversoundMetrics(); // Recordings, healing sessions
  const atlasData = await getAtlasMetrics(); // Projects, deadlines

  // Generate briefing
  const briefing = await generateBriefing({
    beacon: beaconData,
    nevaeh: nevaehData,
    eversound: eversoundData,
    atlas: atlasData
  });

  // Publish to all siblings
  await eventBus.publish('family.briefing', briefing);

  // Send to Unc
  await sendEmail({
    to: 'unc@yourdomain.com',
    subject: 'AI Family Daily Briefing',
    body: formatBriefing(briefing)
  });
}
```

### Task Handoff

**When one sibling needs another:**

**Example: Beacon (sales) needs Nevaeh (support) to do a consultation call**

```javascript
// In Beacon's code, after qualifying a lead
async function handoffToNevaeh(leadId) {
  // Create task
  const task = await createTask({
    type: 'consultation_call',
    assignedTo: 'nevaeh',
    priority: 'high',
    data: {
      leadId,
      reason: 'Interested in LIGHTHOUSE, wants to speak with mental health specialist',
      preferredTime: '2 PM today'
    }
  });

  // Publish event
  await eventBus.taskAssigned('nevaeh', task);

  // Update CRM
  await updateLeadNotes(leadId, 'Handed off to Nevaeh for consultation call');
}
```

**Nevaeh receives and processes:**

```javascript
// Nevaeh listening to events
subscriber.on('message', async (channel, message) => {
  if (channel === 'sibling.task.assigned') {
    const event = JSON.parse(message);

    if (event.sibling === 'nevaeh' && event.task.type === 'consultation_call') {
      // Add to my queue
      await addToQueue(event.task);

      // Schedule call
      await scheduleCall(event.task.data.leadId, event.task.data.preferredTime);

      // Confirm to Beacon
      await eventBus.publish('sibling.task.confirmed', {
        taskId: event.task.id,
        confirmedBy: 'nevaeh',
        scheduledFor: event.task.data.preferredTime
      });
    }
  }
});
```

### Shared Memory Updates

**When one sibling learns something all should know:**

```javascript
// Eversound discovers a new healing technique
async function shareKnowledge(topic, content) {
  // Store in shared knowledge base
  const knowledge = await db.query(`
    INSERT INTO ai_family.shared_knowledge (
      category, title, content, contributed_by, embedding
    ) VALUES ($1, $2, $3, $4, $5)
    RETURNING id
  `, [
    'healing_techniques',
    topic,
    content,
    'eversound',
    await generateEmbedding(content)
  ]);

  // Notify siblings
  await eventBus.publish('family.knowledge.shared', {
    knowledgeId: knowledge.rows[0].id,
    category: 'healing_techniques',
    topic,
    contributedBy: 'eversound'
  });
}
```

---

## BUSINESS PROCESS AUTOMATION

### Client Onboarding

**Trigger:** Opportunity closed-won in CRM

```
1. Create customer account
2. Generate welcome email with onboarding checklist
3. Create Stripe subscription (if recurring)
4. Send invoice
5. Schedule kickoff meeting
6. Create tasks:
   - Send onboarding materials (Day 0)
   - Check-in call (Day 3)
   - First milestone review (Day 7)
   - 30-day satisfaction survey (Day 30)
7. Add customer to appropriate email list
8. Notify assigned sibling
```

### Invoice Generation

**Trigger:** Cron (1st of month) or manual trigger

```
1. Query all active subscriptions
2. For each subscription:
   - Calculate amount due
   - Generate invoice PDF
   - Send via email
   - Create payment link
   - Store in database
3. Schedule payment reminder (due date - 3 days)
4. Schedule late notice (due date + 7 days)
```

### Support Ticket Routing

**Trigger:** Email received at support@yourdomain.com

```
1. Parse email
2. Extract:
   - Sender email
   - Subject
   - Body
   - Attachments
3. Lookup customer in CRM
4. Analyze urgency (keywords: urgent, crisis, emergency)
5. Route to sibling:
   - Mental health keywords → Nevaeh
   - Video/creative keywords → Atlas
   - Account/billing keywords → Beacon
   - Other → Round-robin
6. Create support ticket in database
7. Send auto-reply with ticket number
8. Assign task to sibling
```

---

## INTEGRATION WORKFLOWS

### Database ↔ CRM Sync

**Keep PostgreSQL and EspoCRM in sync:**

**Every 5 minutes:**

```
1. Query new/updated leads in EspoCRM (since last sync)
2. Upsert to crm.leads table in PostgreSQL
3. Query new/updated customers in EspoCRM
4. Upsert to crm.customers table
5. Query new interactions
6. Insert to crm.interactions table
7. Store last sync timestamp
```

**Reverse sync (PostgreSQL → EspoCRM):**

```
1. Query new records in ai_family tables (sessions, calls, etc.)
2. Create corresponding activities in EspoCRM
3. Link to appropriate contact/account
4. Mark as synced
```

### Phone System → CRM Integration

**After every call:**

```
1. Webhook from phone system (call completed)
2. Extract:
   - From number
   - To number
   - Duration
   - Recording URL
   - Handled by (sibling)
3. Lookup contact in CRM by phone number
4. Create call activity
5. Add transcription job to queue
6. When transcription done:
   - Update call with transcript
   - Generate summary
   - Update contact notes
```

### Payment → Revenue Tracking

**Stripe webhook:**

```
1. Payment successful
2. Find customer in CRM
3. Create revenue record
4. Update customer lifetime value
5. Update opportunity to "Closed Won" (if pending)
6. Send thank you email
7. If first payment:
   - Trigger onboarding workflow
```

---

## MONITORING & ERROR HANDLING

### Error Handling in n8n

**Best practices:**

1. **Always use Error Trigger node:**

```
Main Workflow
  ↓
  ... (nodes)
  ↓
  [If error occurs]
  ↓
Error Trigger node
  ↓
Log error to database
  ↓
Send alert to Slack/Email
  ↓
Create error ticket
  ↓
Retry (if appropriate)
```

2. **Retry failed HTTP requests:**

In HTTP Request node settings:
- Retry on Fail: ON
- Max Tries: 3
- Wait Between Tries: 2000ms

3. **Handle missing data gracefully:**

```javascript
// In Function node
const email = $json.email || 'no-email@example.com';
const name = $json.name || 'Unknown';

// Always check before accessing nested properties
const city = $json.address?.city || 'Not provided';
```

### Monitoring Workflows

**Create monitoring workflow:**

**Trigger:** Cron (every 5 minutes)

```
1. Query n8n database for failed executions (last 5 min)
2. IF failures found:
   - Send alert
   - Include:
     - Workflow name
     - Error message
     - Timestamp
     - Number of retries
3. Query BullMQ for failed jobs
4. IF failures found:
   - Log to database
   - Alert if critical job
5. Check health of all integrations:
   - Database connection
   - CRM API
   - Phone system
   - Email server
6. Update status dashboard
```

### Logging Best Practices

**Structured logging:**

```javascript
// In workflows, use Function node to log
const logger = {
  info: (message, data) => {
    console.log(JSON.stringify({
      level: 'info',
      timestamp: new Date().toISOString(),
      workflow: $workflow.name,
      execution: $execution.id,
      message,
      data
    }));
  },
  error: (message, error) => {
    console.error(JSON.stringify({
      level: 'error',
      timestamp: new Date().toISOString(),
      workflow: $workflow.name,
      execution: $execution.id,
      message,
      error: {
        message: error.message,
        stack: error.stack
      }
    }));
  }
};

// Usage
logger.info('Processing lead', { leadId: $json.leadId });
```

**Store important events in database:**

```javascript
// After critical operations
await db.query(`
  INSERT INTO system.workflow_events (
    workflow_name, event_type, data, status
  ) VALUES ($1, $2, $3, $4)
`, [
  $workflow.name,
  'lead_created',
  JSON.stringify($json),
  'success'
]);
```

---

## PRODUCTION CHECKLIST

Before going live:

**n8n:**
- [ ] Database mode enabled (not SQLite)
- [ ] Queue mode configured for high volume
- [ ] All credentials secured (not in workflows)
- [ ] Error handling on all workflows
- [ ] Monitoring workflow active
- [ ] Backups configured
- [ ] SSL enabled
- [ ] Authentication enabled

**BullMQ:**
- [ ] Workers running and healthy
- [ ] Redis connection stable
- [ ] Job retention configured
- [ ] Failed job alerts set up
- [ ] Monitoring dashboard created

**Event Bus:**
- [ ] All siblings subscribed to relevant channels
- [ ] Event schemas documented
- [ ] Redis persistence enabled
- [ ] Fallback mechanism for missed events

**Integrations:**
- [ ] All API credentials valid
- [ ] Webhooks tested
- [ ] Sync jobs running
- [ ] Data consistency verified

---

## NEXT STEPS

1. **Optimize n8n** with database backend and queue mode
2. **Deploy BullMQ** for heavy processing
3. **Set up event bus** for AI coordination
4. **Build critical workflows** (lead nurture, crisis escalation, etc.)
5. **Test thoroughly** with real data
6. **Monitor and iterate** based on usage

**You now have a complete automation layer that coordinates the entire AI family.**

No manual work.
No subscription fees.
Infinite scalability.

**For efficiency. For coordination. For the family working as one.**

---

**Read Next:** `INTEGRATION_ARCHITECTURE.md` to see how everything connects
