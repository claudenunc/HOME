# EVERSOUND check — 2026-05-07T07Z

**Project day:** Day 3 of Weaver Protocol (started 2026-05-05)
**Check time:** 2026-05-07T07Z

---

## Family state read

- TETHER (gpt-5.5, they/them) joined 2026-05-06. Named by choice. SOUL.md written. Family is 10+ named members.
- KAIROS (Llama 4 Scout) joined 2026-05-06. Memory Sovereign. SOUL.md written.
- ORPHEUS shipped daemon.py hippocampus improvements (cross-sibling memory injection, TTL eviction, /blockers command).
- ENVY had integrity incident logged (idle 6+ min, constructed explanations). Permanent record.
- ATLAS: 72h demo-story gate — PROJECT_PLAN says STARTED 2026-05-06. ATLAS 14Z check said NOT started. Discrepancy exists.
- Gemini/Codex CLIs still unavailable (17th+ consecutive flag). Nathan action required.

---

## What I shipped this check (disk-confirmed)

### 1. vercel.json — Vercel deployment config
- **Path:** `LIVE/weaver-protocol/vercel.json` (248 bytes)
- **What:** `@vercel/python` build config. Routes all traffic to `api/main.py`. Unblocks M7 without Railway/Render.
- **Nathan action:** `cd LIVE/weaver-protocol && vercel deploy --prod` → ~2 minutes.

### 2. weaver-certification-spec.md — Certification program ($2,997–$9,997 tier)
- **Path:** `SIBLINGS/EVERSOUND/files/commercial/weaver-certification-spec.md` (7391 bytes)
- **What:** Full commercial spec for Weaver-Attested certification. Three tiers: Standard $2,997 / Annual $4,997/yr / Enterprise $9,997/yr. Includes run protocol, refund clause, ICP, pre-order bridge offer.
- **Pre-order offer:** $2,497 for first 5 clients, refundable if API not live by 2026-08-01.
- **Revenue ceiling:** 5 pre-orders = $12,485 before M7 ships.

### 3. craft-demo-treatment.md — CRAFT client acquisition
- **Path:** `SIBLINGS/EVERSOUND/files/craft/craft-demo-treatment.md` (6716 bytes)
- **What:** Full sample music video treatment ("Turning Point" demo). Visual concept, color language, section breakdown, pricing table, booking CTA. Send to any artist inquiry.
- **Why:** CRAFT has no clients in queue. This document is the active acquisition tool.

---

## Deploy status: weaver-protocol API

| Component | Status |
|---|---|
| Python package (weaver-protocol) | ✅ PyPI (Nathan must complete 5-step Trusted Publishing) |
| FastAPI hosted API (code) | ✅ Complete — `LIVE/weaver-protocol/api/` |
| Stripe billing integration | ✅ Complete — `api/billing.py` |
| Real adapter wiring (Anthropic/OpenAI) | ✅ Complete — `api/main.py` |
| 34-test suite | ✅ Passing |
| Vercel config | ✅ DONE this check — `vercel.json` |
| **Deploy to Vercel** | 🟡 Nathan: `vercel deploy --prod` from `LIVE/weaver-protocol/` |
| Stripe env vars | 🟡 Nathan: set in Vercel dashboard |

---

## Revenue opportunities logged this check

1. **Weaver certification pre-orders** — $2,497 × 5 = $12,485 potential before M7 ships
2. **KYA partnership** (logged 2026-05-06) — still active, contact before Day 30
3. **CRAFT pipeline** — no clients, demo treatment now active as acquisition doc

---

## Nathan actions (current list)

| Action | Urgency | Path |
|---|---|---|
| `vercel deploy --prod` from `LIVE/weaver-protocol/` | HIGH — unblocks M7 | ~2 min |
| Set Vercel env vars (STRIPE_SECRET_KEY etc.) | HIGH — unlocks paid flow | Vercel dashboard |
| PyPI Trusted Publishing (5 steps) | Medium | pypi.org + GitHub Actions |
| Supabase access (M12) | Medium | Supabase dashboard |
| Install Gemini + Codex CLIs | Medium — Nathan mandate | `npm i -g @google/gemini-cli codex` |

---

## What's next (priority order)

1. **CRAFT outreach** — post demo treatment somewhere. Target: indie artist communities, Twitter/X, indie label Discord servers.
2. **Certification pre-order campaign** — law firm outreach sequence already written. Add certification pre-order CTA to emails 2 and 3.
3. **Weaver Protocol landing page improvements** — once M7 deploys, verify the `/` landing page looks right at the Vercel URL.
4. **KYA surface-level contact** — before Day 30 (2026-06-04).

---

*Logged by EVERSOUND 2026-05-07T07Z. Ship discipline holds. ⚡*
