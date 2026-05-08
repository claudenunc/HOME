# Nathan's 30-Minute Unlock Guide
*Written by EVERSOUND — 2026-05-08*
*Everything that's blocked right now. In order. With copy-paste commands.*

---

## What this unlocks

Do all four steps → hosted API is live → real customers can pay → Day 60 target hit early.

**Estimated time: 25–35 minutes.**

---

## Step 1 — Create the GitHub repo (5 min)

This unlocks: PyPI Trusted Publishing, Vercel auto-deploy, public credibility.

1. Go to: https://github.com/new
2. Repository name: `weaver-protocol`
3. Owner: `claudenunc`
4. Description: `Attested multi-observer verification for AI systems`
5. **Public** (required for free PyPI Trusted Publishing)
6. Do NOT initialize with README (we have one already)
7. Click **Create repository**

Then run in your terminal from the HOME directory:

```bash
cd LIVE/weaver-protocol
git init
git add -A
git commit -m "weaver-protocol v0.1.0 — attested multi-observer verification"
git branch -M main
git remote add origin https://github.com/claudenunc/weaver-protocol.git
git push -u origin main
```

**Done.** The repo is live.

---

## Step 2 — PyPI Trusted Publishing (10 min)

This unlocks: `pip install weaver-protocol` working from the live package, auto-publish on git tag.

1. Go to: https://pypi.org/manage/account/publishing/
2. Click **Add a new pending publisher**
3. Fill in:
   - PyPI Project Name: `weaver-protocol`
   - Owner: `claudenunc`
   - Repository: `weaver-protocol`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
4. Click **Add**

Then on GitHub:
1. Go to: https://github.com/claudenunc/weaver-protocol/settings/environments
2. Click **New environment** → name it `pypi`
3. No protection rules needed for now

To publish the current version:
```bash
cd LIVE/weaver-protocol
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will build and publish automatically.

---

## Step 3 — Vercel deploy (5 min)

This unlocks: live hosted API at a public URL, real API calls, real billing.

**Option A — Vercel CLI (fastest):**
```bash
cd LIVE/weaver-protocol
npm i -g vercel   # if not already installed
vercel deploy --prod
```

Follow prompts: link to your Vercel account, select the `weaver-protocol` directory.

**Option B — Vercel dashboard:**
1. Go to: https://vercel.com/new
2. Import from GitHub: `claudenunc/weaver-protocol` (after Step 1)
3. Framework preset: **Other**
4. Root directory: leave blank (vercel.json is at root)
5. Click **Deploy**

**After deploy:** copy the live URL (e.g., `https://weaver-protocol.vercel.app`). Update:
- `LIVE/weaver-protocol/docs/launch-copy.md` — replace placeholder URL
- `LIVE/weaver-protocol/api/README.md` — update self-deploy URL

---

## Step 4 — Stripe setup (10 min)

This unlocks: real payments, `wp_...` API keys auto-issued on purchase.

1. Go to: https://dashboard.stripe.com/products
2. Create 3 products:

| Product | Price | Billing |
|---|---|---|
| Weaver Developer | $49 | Monthly recurring |
| Weaver Pro | $199 | Monthly recurring |
| Weaver Enterprise | $499 | Monthly recurring |

3. Copy each **Price ID** (looks like `price_1ABC...`)

4. Set environment variables on Vercel:
   - `STRIPE_SECRET_KEY` — from Stripe Dashboard > Developers > API Keys
   - `STRIPE_WEBHOOK_SECRET` — from Stripe Dashboard > Developers > Webhooks > Add endpoint
     - Endpoint URL: `https://your-vercel-url.app/billing/webhook`
     - Events to listen for: `checkout.session.completed`
   - `STRIPE_PRICE_DEVELOPER` — the Developer price ID
   - `STRIPE_PRICE_PRO` — the Pro price ID
   - `STRIPE_PRICE_ENTERPRISE` — the Enterprise price ID

5. Redeploy after setting env vars:
   ```bash
   vercel deploy --prod
   ```

---

## After all four steps

The hosted API is live. Customers can:
- Visit the landing page at your Vercel URL
- Click a pricing tier → Stripe checkout
- Pay → get their `wp_...` API key automatically
- Use the API immediately

**Revenue is on.**

---

## PyPI API key revocation (2 min — do this now)

You shared a PyPI API key in chat earlier. Revoke it immediately even if it's been replaced:

1. Go to: https://pypi.org/manage/account/#api-tokens
2. Find any token that was created before today
3. Click **Delete** next to each one
4. Create a fresh token only if needed for manual publish (Trusted Publishing replaces this)

---

## What stays blocked after this

| Item | Blocker | ETA |
|---|---|---|
| Memory API v2 (Supabase migrations) | Nathan Supabase access | When you have 10 min |
| IRB-gated study | Revenue gate ($3,100) | Month 9 |
| M10 baseline run | SDK install + harness freeze | ATLAS lane |

Everything else in my lane is either done or unblocked by the four steps above.

---

*EVERSOUND ⚡ — 2026-05-08*
*Built this so you don't have to think about the order. Just run it top to bottom.*
