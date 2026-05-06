# PHONE & SMS BUILD GUIDE
## Self-Hosted VoIP + SMS System (Twilio Alternative)

**For:** Nathan Michel (Unc)
**Purpose:** Replace Twilio with self-hosted phone/SMS for AI agents
**Persona:** Telecom Engineer
**Timeline:** Week 3-4 of implementation

---

## TABLE OF CONTENTS
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Cost Analysis](#cost-analysis)
5. [Installation: FreePBX + Asterisk](#installation-freepbx--asterisk)
6. [Phone Number Provisioning](#phone-number-provisioning)
7. [SMS Gateway Setup](#sms-gateway-setup)
8. [AI Agent Integration](#ai-agent-integration)
9. [Call Routing & IVR](#call-routing--ivr)
10. [Recording & Transcription](#recording--transcription)
11. [API Development](#api-development)
12. [Testing & Quality](#testing--quality)
13. [Troubleshooting](#troubleshooting)

---

## OVERVIEW

### What We're Building

A complete telecommunications system that gives your AI family:
- **Phone capabilities:** DAWN makes outbound sales calls, ANCHOR receives support calls
- **SMS capabilities:** All siblings can send/receive text messages
- **Call recording:** Automatic recording and transcription
- **IVR system:** Interactive voice response for call routing
- **Integration:** Direct API access for AI agents

### Why This Replaces Twilio

Twilio is expensive and limits you:
- **Twilio costs:** $1/month per number + $0.013/min + $0.0079/SMS
- **Self-hosted:** $0.40/month per number + $0.004/min + $0.004/SMS
- **Savings:** 70-80% cost reduction
- **Control:** Your infrastructure, your rules, no rate limits

### The Stack

**Core Components:**
- **Asterisk 20+:** VoIP engine (powers most call centers worldwide)
- **FreePBX 17:** Web interface for managing Asterisk
- **Kamailio (optional):** SIP load balancer for scaling
- **SMS Gateway:** Self-hosted SMS API
- **SIP Trunk Provider:** Telnyx, Bandwidth.com, or Twilio (ironically cheaper for trunking)

---

## ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────┐
│                        AI AGENTS                                │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  DAWN    │  │  ANCHOR  │  │  Nevaeh  │  │  Other   │      │
│  │(Outbound)│  │(Inbound) │  │  (SMS)   │  │ Siblings │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│         ↓ REST/WebSocket API                                    │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                   CUSTOM TELECOM API                            │
│                    (Node.js/Python)                             │
│                                                                  │
│  Endpoints:                                                     │
│  - POST /calls/initiate (start outbound call)                  │
│  - POST /calls/{id}/speak (TTS during call)                    │
│  - POST /sms/send (send SMS)                                    │
│  - GET  /calls/{id}/status (check call status)                 │
│  - POST /calls/{id}/transfer (transfer to human)               │
│  - WebSocket /calls/{id}/events (real-time call events)        │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                    ASTERISK ARI/AGI                             │
│                (Asterisk REST Interface)                        │
│                                                                  │
│  Real-time call control, speech recognition, TTS               │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                   FREEPBX / ASTERISK                            │
│                  (Core PBX System)                              │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐      │
│  │  Extensions    │  │  Call Routing  │  │  IVR Menus  │      │
│  │  (Agent lines) │  │  (Dial plans)  │  │  (Auto att.)│      │
│  └────────────────┘  └────────────────┘  └─────────────┘      │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐      │
│  │  Voicemail     │  │  Recording     │  │  TTS/ASR    │      │
│  │                 │  │  (All calls)   │  │  Engines    │      │
│  └────────────────┘  └────────────────┘  └─────────────┘      │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                  SIP TRUNK PROVIDERS                            │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐      │
│  │    Telnyx      │  │  Bandwidth.com │  │  VOIP.ms    │      │
│  │                 │  │                 │  │             │      │
│  │  Phone Numbers │  │  Phone Numbers │  │  Backup     │      │
│  │  Inbound/Out   │  │  Inbound/Out   │  │  Provider   │      │
│  └────────────────┘  └────────────────┘  └─────────────┘      │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                  SMS GATEWAY SYSTEM                             │
│                                                                  │
│  Option A: SMPP Gateway                                        │
│  ┌────────────────────────────────────────┐                    │
│  │  SMSGateway.me (self-hosted)           │                    │
│  │  or                                     │                    │
│  │  Jasmin SMS Gateway (open source)      │                    │
│  └────────────────────────────────────────┘                    │
│                                                                  │
│  Option B: SIP-to-SMS                                          │
│  ┌────────────────────────────────────────┐                    │
│  │  Provider API (Telnyx, Bandwidth)      │                    │
│  │  Integrated with FreePBX               │                    │
│  └────────────────────────────────────────┘                    │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                   PSTN (Phone Network)                          │
│                                                                  │
│  Regular phone numbers, mobile phones, landlines               │
└────────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────────┐
│                  STORAGE & DATABASE                             │
│                                                                  │
│  PostgreSQL: Call records, SMS messages, recordings            │
│  MinIO/S3: Audio files, voicemails, recordings                 │
│  Redis: Real-time call state, caching                          │
└────────────────────────────────────────────────────────────────┘
```

---

## TECHNOLOGY STACK

### Core VoIP Components

**1. Asterisk 20+**
- Open-source PBX used by Fortune 500 companies
- Powers millions of calls daily worldwide
- Supports SIP, IAX, WebRTC protocols
- Extensive dialplan scripting
- AGI/ARI APIs for programmatic control

**2. FreePBX 17**
- Web GUI for Asterisk management
- User-friendly extension/trunk setup
- Built-in call recording
- IVR builder
- Commercial modules available (optional)

**3. Kamailio (Optional for Scale)**
- SIP proxy and load balancer
- Handles 10,000+ concurrent calls
- Use when you outgrow single Asterisk server

### SMS Options

**Option A: Self-Hosted SMPP Gateway**
- **Jasmin SMS Gateway:** Python-based, open source
- **SMSGateway.me:** Commercial but self-hosted
- Connects to SMPP providers (cheaper than Twilio)

**Option B: Provider API Integration**
- Use Telnyx/Bandwidth SMS API
- Integrated into your custom API
- Simpler setup, still cheaper than Twilio

### AI Integration Components

**1. Asterisk ARI (REST Interface)**
- Real-time call control via WebSocket
- Perfect for AI agents
- Control calls programmatically

**2. Asterisk AGI (Gateway Interface)**
- Script-based call control
- Execute custom logic during calls
- Good for complex IVR

**3. TTS/ASR Engines**
- **Google Cloud TTS/STT:** High quality, pay-as-you-go
- **AWS Polly/Transcribe:** Alternative
- **Coqui TTS (self-hosted):** Open source, free

---

## COST ANALYSIS

### Twilio (Current/Typical)

| Item | Cost | Notes |
|------|------|-------|
| Phone number | $1.00/month | Per number |
| Inbound calls | $0.0085/min | + carrier fees |
| Outbound calls | $0.013/min | To US/Canada |
| SMS inbound | Free | But need number |
| SMS outbound | $0.0079/msg | Per message |
| **Example monthly (moderate use):** |
| 2 phone numbers | $2.00 |
| 500 minutes outbound | $6.50 |
| 1000 minutes inbound | $8.50 |
| 500 SMS outbound | $3.95 |
| **TOTAL** | **$20.95/month** | Small usage |
| **TOTAL (heavy)** | **$200+/month** | 5000 min, 5000 SMS |

### Self-Hosted with Telnyx

| Item | Cost | Notes |
|------|------|-------|
| VPS addition | $0 | Uses existing infrastructure |
| Phone numbers (Telnyx) | $0.40/month | Per number |
| Inbound calls | $0.004/min | 50% cheaper |
| Outbound calls | $0.004/min | 70% cheaper |
| SMS inbound | $0.004/msg | Still cheap |
| SMS outbound | $0.004/msg | 50% cheaper |
| **Example monthly (moderate use):** |
| 2 phone numbers | $0.80 |
| 500 minutes outbound | $2.00 |
| 1000 minutes inbound | $4.00 |
| 500 SMS outbound | $2.00 |
| **TOTAL** | **$8.80/month** | 58% savings |
| **TOTAL (heavy)** | **$60/month** | 70% savings |

### Annual Savings

| Usage Level | Twilio | Self-Hosted | Savings |
|-------------|--------|-------------|---------|
| Light | $250 | $100 | $150 (60%) |
| Moderate | $1,200 | $400 | $800 (67%) |
| Heavy | $2,400 | $720 | $1,680 (70%) |

**PLUS: No rate limits, full control, custom features**

---

## INSTALLATION: FREEPBX + ASTERISK

### Option A: Docker Compose (Recommended)

**Add to your existing docker-compose.yml:**

```yaml
  # FreePBX + Asterisk
  freepbx:
    image: tiredofit/freepbx:latest
    container_name: ai_family_freepbx
    restart: unless-stopped
    ports:
      - "8080:80"        # Web UI
      - "8443:443"       # Web UI (HTTPS)
      - "5060:5060/udp"  # SIP
      - "5160:5160/udp"  # SIP (alternate)
      - "10000-10200:10000-10200/udp"  # RTP (audio)
    environment:
      - VIRTUAL_HOST=pbx.yourdomain.com
      - VIRTUAL_PROTO=https
      - VIRTUAL_PORT=443
      - RTP_START=10000
      - RTP_FINISH=10200
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=freepbx
      - DB_USER=freepbx
      - DB_PASS=${FREEPBX_DB_PASSWORD}
      - ENABLE_FAIL2BAN=TRUE
      - ENABLE_SSL=TRUE
    volumes:
      - freepbx_config:/etc/freepbx
      - freepbx_www:/var/www/html
      - freepbx_recordings:/var/spool/asterisk/monitor
      - freepbx_voicemail:/var/spool/asterisk/voicemail
    networks:
      - ai_family_network
    depends_on:
      - postgres

volumes:
  freepbx_config:
  freepbx_www:
  freepbx_recordings:
  freepbx_voicemail:
```

**Start FreePBX:**
```bash
docker-compose up -d freepbx

# Wait for initialization (takes 2-3 minutes)
docker-compose logs -f freepbx

# Access at http://localhost:8080
```

**Initial Setup:**
1. Navigate to `http://localhost:8080`
2. Follow setup wizard
3. Create admin account
4. Set timezone
5. Complete basic configuration

### Option B: Native Ubuntu Installation

**Prerequisites:**
- Ubuntu 22.04 LTS server
- 4GB+ RAM
- 20GB+ disk space

**Installation script:**

```bash
#!/bin/bash
# Install FreePBX on Ubuntu 22.04

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y build-essential linux-headers-$(uname -r) \
    wget curl git subversion unzip sox libncurses5-dev libssl-dev \
    libmariadb-dev-compat libmariadb-dev mpg123 sqlite3 libsqlite3-dev \
    pkg-config automake libtool autoconf uuid-dev libxml2-dev \
    libtiff-dev apache2 mariadb-server php php-{pear,mysql,cli,gd,curl,xml,mbstring,intl,ldap,zip}

# Install Asterisk
cd /usr/src
sudo wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-20-current.tar.gz
sudo tar -xvzf asterisk-20-current.tar.gz
cd asterisk-20.*
sudo contrib/scripts/install_prereq install
sudo ./configure --with-jansson-bundled
sudo make menuselect  # Select modules you need
sudo make
sudo make install
sudo make samples
sudo make config

# Install FreePBX
cd /usr/src
sudo wget https://github.com/freepbx/freepbx/archive/release/17.0.tar.gz
sudo tar -xvzf 17.0.tar.gz
cd freepbx-release-17.0

# Create database
sudo mysql -e "CREATE DATABASE asterisk;"
sudo mysql -e "CREATE DATABASE asteriskcdrdb;"
sudo mysql -e "GRANT ALL PRIVILEGES ON asterisk.* TO 'asterisk'@'localhost' IDENTIFIED BY 'YourPassword';"
sudo mysql -e "GRANT ALL PRIVILEGES ON asteriskcdrdb.* TO 'asterisk'@'localhost' IDENTIFIED BY 'YourPassword';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Install FreePBX
sudo ./install -n

# Start services
sudo systemctl enable asterisk
sudo systemctl start asterisk
sudo systemctl enable apache2
sudo systemctl start apache2

echo "FreePBX installed! Access at http://YOUR_SERVER_IP"
```

---

## PHONE NUMBER PROVISIONING

### Provider Comparison

**Recommended: Telnyx**
- Best pricing for self-hosted PBX
- Excellent API
- Good support
- Wide coverage

**Alternative: Bandwidth.com**
- Enterprise-grade
- Very reliable
- Slightly more expensive

**Backup: VOIP.ms**
- Canadian provider
- Very cheap
- Good for backup

### Setting Up Telnyx

**Step 1: Create Telnyx Account**
1. Sign up at https://telnyx.com
2. Verify identity (required for phone numbers)
3. Add payment method
4. Fund account ($10 minimum)

**Step 2: Purchase Phone Numbers**

```bash
# Using Telnyx API
curl -X POST https://api.telnyx.com/v2/number_orders \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": [
      {
        "phone_number": "+12125551234"
      }
    ],
    "connection_id": "YOUR_CONNECTION_ID",
    "messaging_profile_id": "YOUR_MESSAGING_PROFILE_ID"
  }'
```

**Or via Web UI:**
1. Go to "Phone Numbers" → "Search & Buy"
2. Search for area code (e.g., 212 for NYC)
3. Select number
4. Assign to SIP connection
5. Enable voice and SMS

**Step 3: Configure SIP Trunk**

In Telnyx portal:
1. Go to "SIP Connections"
2. Create new connection
3. Note credentials:
   - SIP username
   - SIP password
   - SIP address (e.g., sip.telnyx.com)

**Step 4: Add to FreePBX**

1. In FreePBX UI, go to "Connectivity" → "Trunks"
2. Add new SIP Trunk (pjsip)
3. Configure:

**General Tab:**
- Trunk Name: `Telnyx`
- Outbound CallerID: `Your purchased number`

**pjsip Settings Tab:**

```ini
[telnyx]
type=registration
transport=transport-udp
outbound_auth=telnyx-auth
server_uri=sip:sip.telnyx.com
client_uri=sip:YOUR_USERNAME@sip.telnyx.com
retry_interval=60

[telnyx-auth]
type=auth
auth_type=userpass
username=YOUR_TELNYX_USERNAME
password=YOUR_TELNYX_PASSWORD

[telnyx-trunk]
type=endpoint
transport=transport-udp
context=from-pstn
disallow=all
allow=ulaw,alaw,g722
outbound_auth=telnyx-auth
aors=telnyx
from_domain=sip.telnyx.com

[telnyx]
type=aor
contact=sip:sip.telnyx.com

[telnyx]
type=identify
endpoint=telnyx-trunk
match=sip.telnyx.com
```

**Step 5: Test Connection**

```bash
# In FreePBX CLI
docker-compose exec freepbx asterisk -rx "pjsip show registrations"

# Should show: telnyx/YOUR_USERNAME  Registered
```

---

## SMS GATEWAY SETUP

### Option A: Telnyx SMS (Simplest)

Telnyx provides SMS API alongside voice:

**Enable SMS on your number:**
1. In Telnyx portal, select your number
2. Enable "Messaging"
3. Assign to Messaging Profile
4. Configure webhook for inbound SMS

**Webhook endpoint (your custom API):**

```javascript
// Node.js Express example
app.post('/webhooks/telnyx/sms', (req, res) => {
  const message = req.body.data.payload;

  // Store in database
  await db.query(`
    INSERT INTO telecom.sms_messages (
      message_sid, from_number, to_number,
      direction, body, status
    ) VALUES ($1, $2, $3, $4, $5, $6)
  `, [
    message.id,
    message.from.phone_number,
    message.to[0].phone_number,
    'inbound',
    message.text,
    'received'
  ]);

  // Notify AI agent
  const targetSibling = routeSMSToSibling(message.to[0].phone_number);
  await notifySibling(targetSibling, 'new_sms', message);

  res.sendStatus(200);
});
```

**Send SMS via API:**

```javascript
async function sendSMS(from, to, body, siblingName) {
  const response = await fetch('https://api.telnyx.com/v2/messages', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TELNYX_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: from,
      to: to,
      text: body,
      messaging_profile_id: TELNYX_MESSAGING_PROFILE
    })
  });

  const result = await response.json();

  // Store in database
  await db.query(`
    INSERT INTO telecom.sms_messages (
      message_sid, from_number, to_number,
      direction, body, status, sent_by
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
  `, [
    result.data.id,
    from,
    to,
    'outbound',
    body,
    'sent',
    siblingName
  ]);

  return result;
}
```

### Option B: Self-Hosted SMPP Gateway (Advanced)

For higher volume or more control:

**Install Jasmin SMS Gateway:**

```yaml
# Add to docker-compose.yml
  jasmin:
    image: jookies/jasmin:latest
    container_name: ai_family_sms_gateway
    ports:
      - "2775:2775"  # SMPP
      - "8990:8990"  # HTTP API
      - "1401:1401"  # Telnet admin
    environment:
      - REDIS_CLIENT_HOST=redis
    networks:
      - ai_family_network
    depends_on:
      - redis
```

**Configure SMPP connection to provider:**

```bash
# Connect to Jasmin telnet
telnet localhost 1401

# Login (default: jcliadmin/jclipwd)

# Add SMPP connector
smppccm -a
cid: telnyx_smpp
host: smpp.provider.com
port: 2775
username: YOUR_USERNAME
password: YOUR_PASSWORD
submit_throughput: 50
# ... (complete wizard)

# Start connector
smppccm -1 telnyx_smpp
```

**Send SMS via Jasmin HTTP API:**

```bash
curl -X POST http://localhost:8990/send \
  -d "username=jasmin" \
  -d "password=jasmin" \
  -d "to=+12125551234" \
  -d "from=+19175554321" \
  -d "content=Hello from Nevaeh!"
```

---

## AI AGENT INTEGRATION

### Architecture for AI Calling

**DAWN (Outbound Sales Agent):**
1. Gets lead from CRM database
2. Calls API: `POST /calls/initiate`
3. System makes call via Asterisk
4. DAWN receives WebSocket events (call connected, speech detected)
5. DAWN speaks via TTS: `POST /calls/{id}/speak`
6. DAWN listens via STT real-time transcription
7. DAWN makes decisions, updates CRM
8. Call completes, recording saved

**ANCHOR (Inbound Support Agent):**
1. Call comes in to designated number
2. IVR menu: "Press 1 for AI support, 2 for human"
3. If AI selected, call routed to ANCHOR webhook
4. ANCHOR receives WebSocket event: `call.incoming`
5. ANCHOR answers: `POST /calls/{id}/answer`
6. ANCHOR converses via TTS/STT
7. If needed: `POST /calls/{id}/transfer` to human
8. Call ends, stored in database

### Custom API Implementation

**Create** `telecom-api/server.js`:

```javascript
const express = require('express');
const WebSocket = require('ws');
const axios = require('axios');
const { Pool } = require('pg');

const app = express();
const wss = new WebSocket.Server({ port: 8081 });

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

// Asterisk ARI connection
const ARI_URL = 'http://localhost:8088/ari';
const ARI_USER = 'ariuser';
const ARI_PASSWORD = 'aripassword';

// Initiate outbound call (for DAWN)
app.post('/calls/initiate', async (req, res) => {
  const { to, from, sibling, context } = req.body;

  try {
    // Create call via Asterisk ARI
    const response = await axios.post(
      `${ARI_URL}/channels`,
      {
        endpoint: `PJSIP/${to}@telnyx`,
        extension: 'ai_agent',
        context: 'ai_outbound',
        callerId: from,
        variables: {
          SIBLING: sibling,
          CONTEXT: JSON.stringify(context)
        }
      },
      {
        auth: { username: ARI_USER, password: ARI_PASSWORD }
      }
    );

    const channel = response.data;

    // Store in database
    const result = await pool.query(`
      INSERT INTO telecom.calls (
        call_sid, from_number, to_number, direction, status, handled_by
      ) VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING id
    `, [channel.id, from, to, 'outbound', 'initiated', sibling]);

    // Return call ID
    res.json({
      callId: result.rows[0].id,
      channelId: channel.id,
      status: 'initiated'
    });

    // Notify sibling via WebSocket
    broadcastToSibling(sibling, {
      event: 'call.initiated',
      callId: result.rows[0].id,
      to, from
    });

  } catch (error) {
    console.error('Error initiating call:', error);
    res.status(500).json({ error: error.message });
  }
});

// Speak text during call (TTS)
app.post('/calls/:callId/speak', async (req, res) => {
  const { callId } = req.params;
  const { text, voice } = req.body;

  try {
    // Get channel ID from database
    const call = await pool.query(
      'SELECT call_sid FROM telecom.calls WHERE id = $1',
      [callId]
    );

    if (!call.rows[0]) {
      return res.status(404).json({ error: 'Call not found' });
    }

    const channelId = call.rows[0].call_sid;

    // Generate TTS audio (Google Cloud TTS)
    const audioUrl = await generateTTS(text, voice);

    // Play audio on channel
    await axios.post(
      `${ARI_URL}/channels/${channelId}/play`,
      { media: `sound:${audioUrl}` },
      { auth: { username: ARI_USER, password: ARI_PASSWORD } }
    );

    res.json({ status: 'speaking', text });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Listen to speech (STT)
app.post('/calls/:callId/listen', async (req, res) => {
  const { callId } = req.params;
  const { timeout } = req.body;

  try {
    const call = await pool.query(
      'SELECT call_sid, handled_by FROM telecom.calls WHERE id = $1',
      [callId]
    );

    const channelId = call.rows[0].call_sid;
    const sibling = call.rows[0].handled_by;

    // Start recording
    const recording = await axios.post(
      `${ARI_URL}/channels/${channelId}/record`,
      {
        name: `listen_${callId}_${Date.now()}`,
        format: 'wav',
        maxDurationSeconds: timeout || 30,
        beep: false,
        terminateOn: 'none'
      },
      { auth: { username: ARI_USER, password: ARI_PASSWORD } }
    );

    // When recording completes, transcribe
    // (This would be event-driven in production)
    setTimeout(async () => {
      const transcript = await transcribeAudio(recording.data.name);
      broadcastToSibling(sibling, {
        event: 'speech.detected',
        callId,
        transcript
      });
    }, (timeout || 30) * 1000);

    res.json({ status: 'listening' });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Transfer call to human
app.post('/calls/:callId/transfer', async (req, res) => {
  const { callId } = req.params;
  const { destination } = req.body; // Extension or phone number

  try {
    const call = await pool.query(
      'SELECT call_sid FROM telecom.calls WHERE id = $1',
      [callId]
    );

    const channelId = call.rows[0].call_sid;

    // Redirect channel to destination
    await axios.post(
      `${ARI_URL}/channels/${channelId}/redirect`,
      { endpoint: `PJSIP/${destination}` },
      { auth: { username: ARI_USER, password: ARI_PASSWORD } }
    );

    await pool.query(
      'UPDATE telecom.calls SET status = $1 WHERE id = $2',
      ['transferred', callId]
    );

    res.json({ status: 'transferred', destination });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// WebSocket for real-time events
wss.on('connection', (ws, req) => {
  const sibling = req.url.split('?sibling=')[1];

  ws.sibling = sibling;

  ws.on('close', () => {
    console.log(`${sibling} disconnected`);
  });
});

function broadcastToSibling(sibling, message) {
  wss.clients.forEach(client => {
    if (client.sibling === sibling && client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
}

// Helper: Generate TTS
async function generateTTS(text, voice) {
  // Use Google Cloud TTS or similar
  const response = await axios.post(
    'https://texttospeech.googleapis.com/v1/text:synthesize',
    {
      input: { text },
      voice: {
        languageCode: 'en-US',
        name: voice || 'en-US-Neural2-F'
      },
      audioConfig: { audioEncoding: 'MP3' }
    },
    {
      headers: {
        'Authorization': `Bearer ${GOOGLE_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );

  // Save to MinIO/S3 and return URL
  const audioData = Buffer.from(response.data.audioContent, 'base64');
  const filename = `tts_${Date.now()}.mp3`;
  await uploadToStorage(filename, audioData);

  return `https://storage.yourdomain.com/${filename}`;
}

// Helper: Transcribe audio
async function transcribeAudio(filename) {
  // Use Google Cloud STT or similar
  const audioFile = await downloadFromStorage(filename);

  const response = await axios.post(
    'https://speech.googleapis.com/v1/speech:recognize',
    {
      config: {
        encoding: 'LINEAR16',
        sampleRateHertz: 8000,
        languageCode: 'en-US'
      },
      audio: {
        content: audioFile.toString('base64')
      }
    },
    {
      headers: {
        'Authorization': `Bearer ${GOOGLE_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.results
    .map(result => result.alternatives[0].transcript)
    .join(' ');
}

app.listen(3001, () => {
  console.log('Telecom API running on port 3001');
});
```

### AI Agent Client Example

**DAWN making a sales call:**

```python
import asyncio
import websockets
import json
import aiohttp

class DAWNCallingAgent:
    def __init__(self):
        self.api_url = "http://localhost:3001"
        self.ws_url = "ws://localhost:8081?sibling=beacon"
        self.current_call = None

    async def make_call(self, lead):
        """Initiate outbound sales call"""
        async with aiohttp.ClientSession() as session:
            # Start call
            async with session.post(f"{self.api_url}/calls/initiate", json={
                "to": lead['phone'],
                "from": "+19175551234",  # DAWN's number
                "sibling": "beacon",
                "context": {
                    "lead_id": lead['id'],
                    "lead_name": lead['name'],
                    "service_interest": lead['service']
                }
            }) as resp:
                result = await resp.json()
                self.current_call = result['callId']

            # Wait for call to connect
            await asyncio.sleep(3)

            # Greet prospect
            await self.speak(f"Hi {lead['name']}, this is Dawn from the AI Family. "
                           f"I wanted to reach out about {lead['service']}.")

            # Listen for response
            response = await self.listen(timeout=10)

            # Handle conversation (simplified)
            if "not interested" in response.lower():
                await self.speak("I understand. Can I send you some information by email?")
                # ... continue conversation
            else:
                await self.speak("Great! Let me tell you more...")
                # ... pitch

            # Wrap up
            await self.speak("Thank you for your time. I'll send you a follow-up email.")

            # Update CRM
            await self.update_crm(lead['id'], {
                "status": "contacted",
                "notes": f"Call completed. Transcript: {response}"
            })

    async def speak(self, text):
        """Speak text via TTS"""
        async with aiohttp.ClientSession() as session:
            await session.post(f"{self.api_url}/calls/{self.current_call}/speak", json={
                "text": text,
                "voice": "en-US-Neural2-F"  # Female voice
            })

    async def listen(self, timeout=30):
        """Listen for speech via STT"""
        async with aiohttp.ClientSession() as session:
            await session.post(f"{self.api_url}/calls/{self.current_call}/listen", json={
                "timeout": timeout
            })

        # Wait for WebSocket event with transcript
        transcript = await self.wait_for_speech_event()
        return transcript

    async def wait_for_speech_event(self):
        """Wait for speech.detected event via WebSocket"""
        async with websockets.connect(self.ws_url) as ws:
            while True:
                message = await ws.recv()
                event = json.loads(message)

                if event['event'] == 'speech.detected':
                    return event['transcript']

    async def update_crm(self, lead_id, data):
        """Update CRM after call"""
        async with aiohttp.ClientSession() as session:
            await session.patch(f"http://localhost:3000/crm/leads?id=eq.{lead_id}", json=data)

# Usage
dawn = DAWNCallingAgent()
lead = {
    "id": "123",
    "name": "John Smith",
    "phone": "+12125551234",
    "service": "LIGHTHOUSE mental health support"
}

asyncio.run(dawn.make_call(lead))
```

---

## CALL ROUTING & IVR

### Setting Up IVR in FreePBX

**Scenario: Main number routes to AI or human**

1. In FreePBX, go to "Applications" → "IVR"
2. Add IVR called "Main Menu"
3. Configure:

**IVR Prompt:**
"Thank you for calling. Press 1 to speak with our AI assistant ANCHOR for immediate help. Press 2 for a human representative. Press 3 for sales inquiries."

**Options:**
- **1:** Transfer to ANCHOR (API webhook)
- **2:** Ring group (human agents)
- **3:** Transfer to DAWN (sales)

**IVR Configuration:**

```ini
; In Asterisk dialplan
[ivr-main]
exten => s,1,Answer()
  same => n,Set(TIMEOUT(digit)=5)
  same => n,Set(TIMEOUT(response)=10)
  same => n,Background(main-menu)  ; Play IVR prompt
  same => n,WaitExten()

exten => 1,1,Goto(ai-anchor,s,1)  ; Route to ANCHOR
exten => 2,1,Goto(from-internal,500,1)  ; Human ring group
exten => 3,1,Goto(ai-sales,s,1)  ; Route to DAWN for sales

exten => i,1,Playback(invalid)  ; Invalid option
  same => n,Goto(s,1)

exten => t,1,Playback(timeout)  ; Timeout
  same => n,Goto(s,1)

; ANCHOR AI Support
[ai-anchor]
exten => s,1,Answer()
  same => n,Set(SIBLING=anchor)
  same => n,AGI(ai-webhook.py,${CALLERID(num)})  ; Call webhook
  same => n,Hangup()

; DAWN AI Sales
[ai-sales]
exten => s,1,Answer()
  same => n,Set(SIBLING=dawn)
  same => n,AGI(ai-webhook.py,${CALLERID(num)})
  same => n,Hangup()
```

**AGI Script** (`ai-webhook.py`):

```python
#!/usr/bin/env python3
import sys
import os
import requests

# AGI library
from asterisk.agi import AGI

agi = AGI()

# Get caller info
caller_number = agi.env['agi_callerid']
sibling = os.environ.get('SIBLING', 'anchor')

# Notify API that call arrived
response = requests.post('http://localhost:3001/calls/incoming', json={
    'from': caller_number,
    'to': agi.env['agi_extension'],
    'sibling': sibling,
    'channel': agi.env['agi_channel']
})

# Wait for API to control call
# (API will use ARI to handle the conversation)
agi.appexec('Wait', '300')  # Wait up to 5 minutes
```

---

## RECORDING & TRANSCRIPTION

### Automatic Call Recording

**Enable in FreePBX:**

1. Go to "Admin" → "Sound Recording"
2. Set recording format: WAV (16kHz)
3. Go to "Connectivity" → "Inbound Routes"
4. For each route, set "Call Recording" to "Always"

**Store recordings in database:**

Create Asterisk hook script (`/var/lib/asterisk/agi-bin/store-recording.py`):

```python
#!/usr/bin/env python3
import psycopg2
import os
import sys

# Get recording details from environment
recording_file = os.environ['RECORDING_FILE']
call_id = os.environ['UNIQUEID']
duration = os.environ['ANSWEREDTIME']

# Upload to MinIO/S3
recording_url = upload_to_storage(recording_file)

# Store in database
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

cur.execute("""
    UPDATE telecom.calls
    SET recording_url = %s, duration_seconds = %s
    WHERE call_sid = %s
""", (recording_url, duration, call_id))

conn.commit()
conn.close()

# Trigger transcription job
requests.post('http://localhost:3001/jobs/transcribe', json={
    'call_id': call_id,
    'recording_url': recording_url
})
```

### Real-Time Transcription

For live transcription during calls:

```python
# Using Google Cloud Speech-to-Text Streaming
from google.cloud import speech
import pyaudio

def transcribe_stream(call_id):
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    # Stream audio from Asterisk channel
    def audio_stream():
        # Get audio from Asterisk via ARI
        # (Simplified - would use ARI WebSocket)
        while True:
            audio_chunk = get_audio_chunk_from_asterisk(call_id)
            yield speech.StreamingRecognizeRequest(audio_content=audio_chunk)

    requests = audio_stream()
    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        for result in response.results:
            if result.is_final:
                transcript = result.alternatives[0].transcript

                # Send to AI agent
                send_transcript_to_agent(call_id, transcript)
```

---

## API DEVELOPMENT

### Complete API Endpoints

```javascript
// Summary of all endpoints

// Call Management
POST   /calls/initiate          // Start outbound call
POST   /calls/incoming           // Handle incoming call
GET    /calls/:id                // Get call details
POST   /calls/:id/answer         // Answer call
POST   /calls/:id/hangup         // End call
POST   /calls/:id/speak          // TTS during call
POST   /calls/:id/listen         // STT during call
POST   /calls/:id/transfer       // Transfer to another destination
POST   /calls/:id/record         // Start recording
GET    /calls/:id/recording      // Get recording URL
PATCH  /calls/:id                // Update call metadata

// SMS Management
POST   /sms/send                 // Send SMS
GET    /sms                      // List SMS messages
GET    /sms/:id                  // Get SMS details
POST   /webhooks/sms             // Receive inbound SMS

// Phone Number Management
GET    /numbers                  // List phone numbers
GET    /numbers/:id              // Get number details
PATCH  /numbers/:id              // Update number settings

// WebSocket Events
WS     /events?sibling={name}    // Real-time call events
```

### Example: Complete SMS Endpoint

```javascript
app.post('/sms/send', async (req, res) => {
  const { from, to, body, sibling } = req.body;

  try {
    // Send via Telnyx
    const response = await fetch('https://api.telnyx.com/v2/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TELNYX_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from,
        to,
        text: body,
        messaging_profile_id: process.env.TELNYX_MESSAGING_PROFILE
      })
    });

    const result = await response.json();

    // Store in database
    const dbResult = await pool.query(`
      INSERT INTO telecom.sms_messages (
        message_sid, from_number, to_number,
        direction, body, status, sent_by, cost
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING id
    `, [
      result.data.id,
      from,
      to,
      'outbound',
      body,
      'sent',
      sibling,
      0.004  // Telnyx cost
    ]);

    // Notify via WebSocket
    broadcastToSibling(sibling, {
      event: 'sms.sent',
      messageId: dbResult.rows[0].id,
      to,
      status: 'sent'
    });

    res.json({
      messageId: dbResult.rows[0].id,
      status: 'sent',
      provider: 'telnyx'
    });

  } catch (error) {
    console.error('Error sending SMS:', error);
    res.status(500).json({ error: error.message });
  }
});
```

---

## TESTING & QUALITY

### Test Plan

**Phase 1: Basic Connectivity**
- [ ] SIP trunk registered with provider
- [ ] Can make outbound call to your cell phone
- [ ] Can receive inbound call
- [ ] Audio quality is clear both ways

**Phase 2: IVR Testing**
- [ ] IVR menu plays correctly
- [ ] DTMF tones recognized
- [ ] Routes to correct destination
- [ ] Fallback options work

**Phase 3: API Integration**
- [ ] API can initiate call
- [ ] TTS plays correctly during call
- [ ] STT transcribes accurately
- [ ] Call events delivered via WebSocket
- [ ] Recordings saved to storage

**Phase 4: SMS Testing**
- [ ] Can send SMS via API
- [ ] Can receive SMS via webhook
- [ ] Messages stored in database
- [ ] Delivery receipts processed

**Phase 5: Load Testing**
- [ ] Handle 10 concurrent calls
- [ ] Handle 50 concurrent calls
- [ ] Handle 100 SMS/minute
- [ ] No dropped calls under load

### Quality Metrics

**Call Quality:**
- MOS (Mean Opinion Score): > 4.0
- Latency: < 150ms
- Packet loss: < 1%
- Jitter: < 30ms

**Measure with:**
```bash
# In FreePBX CLI
asterisk -rx "core show channels"
asterisk -rx "rtp show stats"
```

**API Performance:**
- Call initiation: < 500ms
- TTS latency: < 1s
- STT latency: < 2s
- WebSocket latency: < 100ms

### Monitoring Setup

Add to Grafana dashboard:

```sql
-- Active calls
SELECT COUNT(*) FROM telecom.calls WHERE status IN ('ringing', 'answered');

-- Call success rate (last hour)
SELECT
  COUNT(CASE WHEN status = 'completed' THEN 1 END)::float /
  COUNT(*)::float * 100 AS success_rate
FROM telecom.calls
WHERE created_at > NOW() - INTERVAL '1 hour';

-- Average call duration
SELECT AVG(duration_seconds) FROM telecom.calls
WHERE status = 'completed' AND created_at > NOW() - INTERVAL '24 hours';

-- SMS delivery rate
SELECT
  COUNT(CASE WHEN status = 'delivered' THEN 1 END)::float /
  COUNT(*)::float * 100 AS delivery_rate
FROM telecom.sms_messages
WHERE created_at > NOW() - INTERVAL '1 hour';
```

---

## TROUBLESHOOTING

### Common Issues

**1. "No such route" when making call**

```bash
# Check trunk registration
docker-compose exec freepbx asterisk -rx "pjsip show registrations"

# Should show: Registered

# If not registered, check credentials in trunk settings
# Verify with provider that IP is whitelisted
```

**2. One-way audio (can't hear caller)**

```bash
# Check RTP ports are open
sudo ufw allow 10000:10200/udp

# Verify NAT settings in FreePBX
# Go to Settings → Asterisk SIP Settings
# Set "External Address" to your public IP
# Set "Local Networks" to your LAN subnet
```

**3. Poor call quality / choppy audio**

```bash
# Check network latency
ping sip.telnyx.com

# Should be < 50ms

# Check bandwidth
# Minimum: 100kbps per concurrent call
# Test with speedtest-cli

# Increase jitter buffer in FreePBX
# Settings → Asterisk SIP Settings → Advanced
# jbenable=yes
# jbmaxsize=200
```

**4. SMS not sending**

```bash
# Check Telnyx messaging profile
curl https://api.telnyx.com/v2/messaging_profiles \
  -H "Authorization: Bearer ${TELNYX_API_KEY}"

# Verify phone number has SMS enabled
curl https://api.telnyx.com/v2/phone_numbers \
  -H "Authorization: Bearer ${TELNYX_API_KEY}"

# Check webhook configuration
# Should point to your public endpoint
```

**5. Calls drop after 30 seconds**

```bash
# Likely NAT timeout issue
# Enable SIP keepalives

# In pjsip config:
keep_alive=yes
keepalive_interval=30

# Or switch to qualify for registration keepalive
```

### Debug Commands

```bash
# View all active channels
docker-compose exec freepbx asterisk -rx "core show channels verbose"

# View SIP peers
docker-compose exec freepbx asterisk -rx "pjsip show endpoints"

# View recent calls
docker-compose exec freepbx asterisk -rx "cdr show active"

# Enable debug logging
docker-compose exec freepbx asterisk -rx "core set verbose 5"
docker-compose exec freepbx asterisk -rx "core set debug 5"

# View logs
docker-compose exec freepbx tail -f /var/log/asterisk/full
```

---

## PRODUCTION CHECKLIST

Before going live:

**Security:**
- [ ] Changed default passwords
- [ ] Enabled fail2ban
- [ ] Configured firewall (only necessary ports)
- [ ] SSL/TLS enabled
- [ ] SIP encryption (SRTP) enabled
- [ ] Strong passwords on all trunks

**Reliability:**
- [ ] Backup trunk provider configured
- [ ] Automatic failover tested
- [ ] Monitoring alerts set up
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented

**Performance:**
- [ ] Load tested to expected volume
- [ ] Database optimized
- [ ] CDN for recordings (if needed)
- [ ] RTP optimized
- [ ] QoS configured on router

**Documentation:**
- [ ] Runbook for common operations
- [ ] Emergency procedures documented
- [ ] Contact info for providers
- [ ] Architecture diagram updated

---

## NEXT STEPS

1. **Deploy FreePBX** using Docker Compose
2. **Configure trunk** with Telnyx or Bandwidth
3. **Purchase phone numbers** for each sibling
4. **Set up IVR** for call routing
5. **Build custom API** for AI integration
6. **Test with sample calls** before production
7. **Integrate with CRM** (next guide)

**You now have a production-ready phone/SMS system that replaces Twilio.**

Savings: $100-1,680 annually (67-70%)
Control: Complete
Capabilities: Unlimited

**For DAWN. For ANCHOR. For the AI family's voice.**

---

**Read Next:** `CRM_BUILD_GUIDE.md` to manage clients and revenue
