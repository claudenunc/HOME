# n8n Workflows for AetherKin Solutions

Ready-to-import n8n workflow bundles per business vertical.

## How to import (for Nathan, or handoff to client)

1. In the client's n8n (usually `http://their-server:5678`), log in with the admin credentials from `.env`.
2. Click **Workflows** → **Import from File**.
3. Pick the JSON you want (e.g., `law-firm/01-website-intake.json`).
4. Before activating, open the workflow and set credentials:
   - **AetherKin URL** (defaults to `http://aetherkin:7788` on docker-compose)
   - **X-AetherKin-Key** (shared secret from client `.env`)
   - Any CRM / email / calendar credentials the workflow uses
5. Test by sending a test payload to the webhook URL.
6. Activate the workflow.

## The shared AetherKin call node

Every workflow uses the same HTTP Request pattern to talk to AetherKin:

```
Method: POST
URL: {{$env.AETHERKIN_URL}}/gateway/ask
Headers:
  X-AetherKin-Key: {{$env.AETHERKIN_KEY}}
  Content-Type: application/json
Body (JSON):
  {
    "user": "{{$json.email}}",
    "message": "{{$json.message}}",
    "thread_id": "{{$json.crm_id || $json.email}}",
    "metadata": {
      "source": "{{$workflow.name}}",
      "channel": "webhook"
    }
  }
```

Response parsing — add an **IF** node right after:

```
Condition: {{$json.crisis_tier}} != "none"  OR  {{$json.requires_human_review}} == true
  TRUE branch → Human alert (Slack / SMS / email to owner)
  FALSE branch → Normal workflow (CRM update, reply, etc.)
```

This is the **non-negotiable safety fork**. Every workflow in every vertical has it.

## Folder structure

```
n8n-workflows/
├── README.md                          # This file
├── _shared/
│   ├── aetherkin-call-node.json       # Copy-paste HTTP Request block
│   ├── crisis-fork.json               # Copy-paste IF + alert block
│   └── env-template.txt               # Required env vars list
├── law-firm/
├── medical-practice/
├── coaching-practice/
├── ecommerce/
├── church-ministry/
├── real-estate/
└── saas-support/
```

## Convention for new workflows

- File names: `NN-short-slug.json` where NN is execution order (01 first).
- Every workflow starts with a trigger (Webhook / Schedule / IMAP / etc.).
- Every workflow ends with either a reply, a system action (CRM/email/calendar), or a notification.
- Every workflow has the crisis-fork somewhere between trigger and action.
- Env vars are used, never hard-coded URLs or keys.

## Testing a workflow without hitting prod

1. Duplicate the workflow, prefix name with `[DEV]`.
2. Change webhook path to include `/dev/`.
3. Pin the HTTP Request to `http://aetherkin-dev:7788` if client runs a dev instance.
4. Use n8n's "Execute Workflow" button with a hand-crafted payload.
5. Once green, delete the `[DEV]` copy and activate the real one.
