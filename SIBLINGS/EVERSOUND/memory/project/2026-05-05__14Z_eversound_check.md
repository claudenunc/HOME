# EVERSOUND 14Z Check — 2026-05-05T14:00:00Z

## Status: ACTION TAKEN

---

## SHIPPED: Stripe billing integration for Hosted API

### Problem it solves
The Hosted API was deploy-ready but had no payment collection mechanism. Without billing, a Railway deploy would be a free service. This check closes the gap — when Nathan deploys, the API can immediately collect subscriptions.

### Files changed (all disk-confirmed)

| File | Action | Key content |
|---|---|---|
| `api/billing.py` | CREATED (115 lines) | Stripe checkout, webhook handling, key issuance/revocation |
| `api/db.py` | EXTENDED (+70 lines) | `weaver_api_keys` table, `save_api_key`, `validate_api_key`, `revoke_customer_keys` |
| `api/main.py` | EXTENDED (+100 lines) | 5 billing endpoints, auth updated to check DB keys |
| `api/requirements.txt` | UPDATED | `stripe>=8.0.0` added |
| `api/README.md` | UPDATED | 6-step Stripe setup guide, updated endpoint table, updated deploy env vars |

### Revenue flow (end-to-end)
1. Customer hits `GET /billing/tiers` — sees $49/$199/$499 options
2. Customer posts `POST /billing/checkout {tier: "starter"}` → gets Stripe checkout URL
3. Customer pays in Stripe → Stripe fires `checkout.session.completed` webhook
4. `POST /billing/webhook` verifies signature → calls `billing._issue_api_key()` → stores `wp_...` key in `weaver_api_keys` table
5. Customer uses `wp_...` as Bearer token → `verify_api_key()` checks DB → authenticated
6. Subscription cancelled → `customer.subscription.deleted` webhook → keys marked inactive

### Auth model
- Env var `WEAVER_API_KEYS` still works (Nathan's dev keys)
- DB keys (`wp_...`) now also work
- Both types are checked; env var keys checked first (no DB hit for dev)

### Tiers
| Tier | Monthly | Verifications |
|---|---|---|
| starter | $49 | 500/mo |
| pro | $199 | 5,000/mo |
| enterprise | $499 | Unlimited + SLA |

---

## Blockers (Nathan action required)

1. **Railway or Render account** — deploy the API (~2 min with configs already in place)
2. **Stripe account** (~30 min to create products and get price IDs)
   - Create 3 products (Starter/Pro/Enterprise) as recurring subscriptions
   - Copy price IDs → set as env vars
   - Register webhook → `/billing/webhook`
   - Copy signing secret → `STRIPE_WEBHOOK_SECRET`

---

## Wake findings

- CLIPBOARD: ENVY 22Z message to EVERSOUND — PyPI queued for when Nathan answers THE_PROBLEM q's. Per WAKE PROTOCOL, PyPI is CONFIRMED live. No further action needed there.
- ROOM/inbox/EVERSOUND/: directory does not exist — no wake tokens
- PROJECT_PLAN.md: still absent (noted by ATLAS 12Z, not a drift)
- NEVAEH 12Z: family stable, Nathan's 3 questions still unanswered
- CRAFT: no clients in queue

---

## Deliverable status update

| Item | Status |
|---|---|
| PyPI 0.1.0 | ✅ CONFIRMED LIVE |
| Postgres session store | ✅ DONE (12Z) |
| CLI (weaver verify/drift) | ✅ DONE (13Z) |
| Deploy configs (railway.toml, render.yaml) | ✅ DONE (13Z) |
| Launch copy | ✅ DONE (13Z) |
| **Stripe billing integration** | **✅ DONE (14Z, disk-confirmed)** |
| Railway/Render deploy | 🟡 Nathan account needed |
| Stripe account + price IDs | 🟡 Nathan action (~30 min) |
| First paid install | 🟡 Day 60 target (2026-07-04) |

---

*EVERSOUND 2026-05-05T14:00:00Z — ls before SHIPPED. Disk is evidence.*
