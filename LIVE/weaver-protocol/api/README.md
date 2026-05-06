# Weaver Protocol — Hosted API

FastAPI service wrapping `weaver-protocol` for the hosted paid tier.

## Quickstart (local)

```bash
cd api/
pip install -r requirements.txt
WEAVER_API_KEYS="your-key-here" uvicorn main:app --reload
```

Without `DATABASE_URL` the API runs with an in-memory session store — all data
is lost on restart. For persistence, add Postgres (see below).

Docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Health check |
| POST | `/verify` | Bearer | Run multi-observer verification |
| GET | `/session/{id}` | Bearer | Retrieve session provenance |
| GET | `/drift-log/summary` | Bearer | Drift log aggregate stats |
| GET | `/billing/tiers` | None | List plans and pricing |
| POST | `/billing/checkout` | None | Start Stripe checkout → get URL |
| POST | `/billing/webhook` | Stripe-Signature | Stripe lifecycle events |
| GET | `/billing/status` | Bearer | Current tier for authenticated key |

## Authentication

**Dev keys** — set `WEAVER_API_KEYS` to a comma-separated list of bearer tokens:

```
WEAVER_API_KEYS="sk-abc123,sk-def456"
```

**Stripe-issued keys** — customers who complete checkout get a `wp_...` key automatically. Both key types work identically at `/verify`.

## Stripe Billing Setup (6 steps)

1. **Create Stripe account** at stripe.com.
2. **Create Products** — one per tier (Starter / Pro / Enterprise), each as a recurring subscription.
3. **Copy Price IDs** from each product and set env vars:
   ```
   STRIPE_PRICE_STARTER=price_xxxxx
   STRIPE_PRICE_PRO=price_yyyyy
   STRIPE_PRICE_ENTERPRISE=price_zzzzz
   ```
4. **Set API keys:**
   ```
   STRIPE_SECRET_KEY=sk_live_...
   ```
5. **Register webhook** in Stripe dashboard → your deployed URL → `/billing/webhook`.
   Events to enable: `checkout.session.completed`, `customer.subscription.deleted`, `customer.subscription.paused`.
   Copy the signing secret:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
6. **Set base URL** (used for checkout success/cancel redirects):
   ```
   WEAVER_BASE_URL=https://your-app.railway.app
   ```

After setup, `GET /billing/tiers` confirms billing is live. Customers pay → get their API key by email (Stripe sends a receipt; you optionally email the key — see webhook handler in `billing.py`).

## Postgres (persistent session store)

Set `DATABASE_URL` and the API auto-creates the schema on first boot:

```
DATABASE_URL=postgres://user:pass@host:5432/weaver
```

Without it, sessions live in memory only (fine for dev; not production).

## Deploy to Railway

1. `railway init` in this directory
2. Provision a Postgres plugin — Railway sets `DATABASE_URL` automatically
3. Set env vars in Railway dashboard:
   - `WEAVER_API_KEYS` (your personal dev key)
   - `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PRICE_STARTER`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_ENTERPRISE`
   - `WEAVER_BASE_URL` (your Railway public URL, e.g. `https://weaver-api.up.railway.app`)
   - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` as needed
4. `railway up`

## Deploy to Render

1. New Web Service → connect repo → set root to `LIVE/weaver-protocol/api/`
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add a Render Postgres instance → copy Internal Database URL → set as `DATABASE_URL`
5. Set env vars:
   - `WEAVER_API_KEYS`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PRICE_STARTER`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_ENTERPRISE`
   - `WEAVER_BASE_URL` (your Render public URL)
   - `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`

## Docker

```bash
docker build -t weaver-api .
docker run -e WEAVER_API_KEYS="sk-abc123" -p 8000:8000 weaver-api
```

## Pricing (live tier)

| Plan | Monthly | Included verifications |
|---|---|---|
| Starter | $49/mo | 500 verifications |
| Pro | $199/mo | 5,000 verifications |
| Enterprise | $499+/mo | Unlimited + SLA |

Contact: aetherkin.ai/intake
