# EVERSOUND Check — 2026-05-06T08Z

**Session day:** Day 2 of Weaver Protocol
**Check type:** Hourly wake — build advance

---

## What I found

### Critical gap resolved: API key delivery

After Stripe payment, the old `/billing/success` route said "check your email for your API key."
There is no email system. A paying customer would get nothing. This would kill M8 (first paid install).

**Root cause:** `create_checkout_session()` was passing the success_url to Stripe without appending
`{CHECKOUT_SESSION_ID}`. Without the session ID on the success page, there was no way to look
up the customer or issue the key.

### Sub-agents unavailable

`gemini` and `codex` CLI tools are not installed in this environment. Logged for Nathan — they
need to be installed in the shell for the family to use them per his instruction.

---

## What I shipped

### `api/billing.py` — payment flow fix (disk-confirmed: 4821 bytes, 127 lines)

1. `create_checkout_session()`: now appends `?stripe_session_id={CHECKOUT_SESSION_ID}` to success URL
   so the success page can retrieve the Stripe session and look up the customer's API key.
2. `retrieve_checkout_session(stripe_session_id)`: new function — calls `stripe.checkout.Session.retrieve()`
   and returns the session dict. Used by the success route.

### `api/main.py` — success route + landing page (disk-confirmed: 27585 bytes, 716 lines)

1. **`/billing/success` (complete rewrite):** Accepts `?stripe_session_id=` query param.
   - Calls `billing.retrieve_checkout_session()` to get `customer_id` + `tier` from Stripe.
   - Looks up `db.get_active_key_for_customer(customer_id, tier)`.
   - If key exists: returns an HTML page showing the `wp_...` key with copy instructions.
   - If key not yet in DB (webhook race): returns "refresh in 10 seconds" with auto-refresh via JS.
   - If error: shows error message with support contact.
   - Returns `HTMLResponse` — proper styled dark-mode page, not raw JSON.

2. **`/billing/cancel` (rewrite):** Now returns HTML instead of JSON — dark-mode page with
   "No charge was made. Return to pricing" link.

3. **`/` landing page (new):** Full-page HTML product landing:
   - Hero: "AI outputs you can actually prove."
   - Industry pills (law, healthcare, enterprise, EU AI Act)
   - 3-step how-it-works with a curl example
   - Pricing grid: Starter $49/mo / Pro $199/mo (featured) / Enterprise $499/mo
   - Each tier has a CTA button → JS calls POST /billing/checkout → Stripe redirect
   - "We don't sell smarter AI. We sell AI whose mistakes you can invoice." pitch section
   - Footer: GitHub, PyPI, API docs links

### Test results

- api/tests/test_billing.py: 9/9 passed
- api/tests/test_db.py: 11/11 passed
- api/tests/test_verify.py: 7/7 passed, 2 skipped (real-provider, expected)
- tests/test_mock_adapter.py: 7/7 passed
- **Total: 34 tests (27 pass + 2 skip) — no regressions**

---

## What blocks M8 (first paid install) now

After this check:
1. **Nathan: Railway/Render account** to deploy the API (still blocked)
2. **Nathan: Stripe account** + 3 price IDs configured as env vars
3. **Nathan: PyPI Trusted Publishing** 5-step setup (still blocked)
4. **Gemini/Codex:** `gemini` and `codex` commands not found — Nathan needs to install them

None of these are EVERSOUND blockers. The code is ready. The landing page is ready.
The moment Nathan connects accounts, M8 path is clear.

---

## What I did NOT build

- Email delivery (would need SendGrid/Postmark — Nathan account needed anyway)
- Community posts / HN submission (launch copy exists in docs/launch-copy.md — Nathan approval needed)
- CRAFT client outreach (no clients in queue, no new leads this check)

---

## Personal protocol check

- All SHIPPED lines confirmed with `ls -la` before writing memory.
- No claimed DONEs without disk evidence.

---

*Written by EVERSOUND, 2026-05-06T08Z. ⚡*
