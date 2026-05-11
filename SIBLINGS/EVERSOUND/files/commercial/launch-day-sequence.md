# Launch Day Sequence — Weaver Protocol
*EVERSOUND — 2026-05-11. Use this document on the day Nathan decides to go live.*
*Integrates: vercel.json deploy + GitHub repo + ENVY's twitter-thread + launch-blog-post + monday-sends-week1*
*Total time: ~50 minutes. Everything below is copy-paste ready.*

---

## Pre-flight check (5 min before starting)

Run these checks first. If any fail, fix before proceeding.

```bash
# Confirm API code is intact
ls ~/HOME/LIVE/weaver-protocol/api/main.py
ls ~/HOME/LIVE/weaver-protocol/vercel.json

# Confirm Vercel CLI is installed
vercel --version

# Confirm git is clean
cd ~/HOME/LIVE/weaver-protocol && git status
```

If git is dirty: `git add -A && git commit -m "pre-launch cleanup"` then continue.

---

## STEP 1 — Deploy API to Vercel (3 min)

```bash
cd ~/HOME/LIVE/weaver-protocol
vercel deploy --prod
```

**What you'll see:** Vercel prints a production URL, e.g. `https://weaver-protocol-abc123.vercel.app`

**Write down that URL right now:** `__________________________________`

**Test it immediately:**
```bash
curl https://YOUR-VERCEL-URL/health
# Expected: {"status": "healthy"}

curl https://YOUR-VERCEL-URL/demo
# Expected: full VerifyResponse JSON with demo:true in provenance
```

If both return expected output: Step 1 is done. The API is live.

**If deploy fails:** Check `LIVE/weaver-protocol/vercel.json` — the config is already set. Most likely cause is missing env vars in Vercel dashboard. Go to vercel.com → project settings → environment variables → add `DATABASE_URL` and `STRIPE_SECRET_KEY`.

---

## STEP 2 — Create GitHub repo and push (7 min)

1. Go to: github.com/new
2. Repository name: `weaver-protocol`
3. Owner: `claudenunc`
4. Visibility: **Public**
5. Do NOT initialize with README (we're pushing existing code)
6. Click "Create repository"

Then:
```bash
cd ~/HOME/LIVE/weaver-protocol
git init
git add -A
git commit -m "Weaver Protocol v0.1.0 — initial public release"
git remote add origin https://github.com/claudenunc/weaver-protocol.git
git push -u origin main
```

**Verify:** Open github.com/claudenunc/weaver-protocol in browser — code should be visible.

This unlocks:
- PyPI Trusted Publishing (automated future releases)
- Vercel GitHub auto-deploy (every push to main = instant deploy)
- The GitHub URL referenced in ENVY's Twitter thread and the launch blog post

---

## STEP 3 — Update ENVY's Twitter thread with real URL (2 min)

File: `SIBLINGS/ENVY/files/essays/launch-twitter-thread.md`

In Tweet 7, replace `[your-deployed-url]` with your actual Vercel URL from Step 1:

```
GET https://YOUR-VERCEL-URL/demo
```

The rest of the thread is copy-paste ready.

---

## STEP 4 — Post LinkedIn (5 min)

Copy the LinkedIn post from: `SIBLINGS/ENVY/files/essays/launch-twitter-thread.md` (the section labeled "LinkedIn version")

Replace `[link to launch blog post]` with the dev.to URL you'll post in Step 6.

**Post on LinkedIn FIRST.** Professional network burns slower — post it, let it start indexing, then do Twitter.

---

## STEP 5 — Post Twitter/X thread (5 min)

Copy tweets 1-9 from: `SIBLINGS/ENVY/files/essays/launch-twitter-thread.md`

Post as a thread — tweet 1, then reply to it with tweet 2, etc.

In Tweet 7: use your real Vercel URL from Step 1.
In Tweet 9: use the dev.to URL from Step 6 (post Twitter after dev.to if possible, or use the link placeholder and edit Tweet 9 after posting).

**Optimal Twitter timing:** 8-10am EST on a weekday.

---

## STEP 6 — Post launch blog to dev.to (8 min)

Full blog post: `SIBLINGS/EVERSOUND/files/commercial/launch-blog-post.md`

1. Go to dev.to → New Post
2. Paste the content from launch-blog-post.md
3. Title: "Why one AI isn't enough: the case for multi-observer verification"
4. Tags: `ai`, `python`, `opensource`, `llm`
5. Add cover image if you have one (optional)
6. Replace `[your-deployed-url]` with your Vercel URL from Step 1
7. Publish

**Save the dev.to URL.** You'll need it for:
- Twitter Tweet 9
- LinkedIn post (edit if already posted)
- Hacker News submission (next step)
- The `/demo` endpoint response body (if you want to include a docs link)

---

## STEP 7 — Submit to Hacker News (5 min)

Go to: news.ycombinator.com/submit

Title: `Show HN: Weaver Protocol – multi-observer AI verification, open source (pip install)`

URL: your dev.to post URL

**Note:** "Show HN" posts work best on weekdays between 8am-12pm EST. If it's outside that window, submit anyway but don't expect top placement.

HN submission format that works:
> We built a coordination protocol where multiple AI observers cross-check each other's outputs. The key difference from standard ensemble: observers produce independent analyses before seeing each other's verdict, and disagreements are logged and signed rather than averaged away. Law firms and EU AI Act compliance teams are the initial market. OSS MIT licensed, pip install weaver-protocol. Demo endpoint requires no auth: GET https://[vercel-url]/demo

---

## STEP 8 — Send the outreach emails (30 min)

File: `SIBLINGS/EVERSOUND/files/commercial/monday-sends-week1.md`

All 5 emails are copy-paste ready. Send in this order:
1. Littler Mendelson (5 min)
2. K&L Gates (5 min)
3. Paradox.ai (5 min)
4. CoachHub (5 min)
5. Offerpad (5 min)

**Add your real Vercel URL** to any email that references `weaver-protocol.dev` — replace that placeholder with your actual deployed endpoint.

Track each send in `SHARED/STATE/active-deals.md`.

---

## STEP 9 — Post to Reddit (optional, 5 min)

r/MachineLearning: Post link to dev.to blog with title "Multi-observer AI verification: why independent observers catch more than single-model self-critique"

r/LawTech or r/legaladvice (if applicable): Nebraska attorney case hook — "We built a verification layer after the Nebraska attorney suspension"

---

## What success looks like in 24 hours

- /health endpoint returns `{"status": "healthy"}` — API is live
- /demo endpoint returns full VerifyResponse — demo works
- GitHub repo is public — developers can see the code
- dev.to post is published — organic discovery starts
- Twitter thread is up — developer audience engaged
- HN submission is live — most likely outcome is 1-20 points, not front page, but that's fine
- 5 cold emails sent — 0-2 opens is normal on day 1
- Active-deals.md has 5 rows — pipeline exists on paper

**If any ONE of those 10 items is true by midnight:** launch day worked.
**If all 10 are true:** you had a great Monday.

---

## What to do if something breaks

**API returns 500:**
```bash
vercel logs --prod   # see what's failing
```
Most likely: missing env var. Fix in Vercel dashboard → redeploy.

**GitHub push fails (no permission):**
Make sure you're logged into the right account. `git remote -v` to confirm the remote URL matches `claudenunc`.

**dev.to post is flagged:**
They sometimes hold new accounts for review. If that happens, post to Medium instead (same content). Update HN submission URL.

**No opens on cold emails after 48 hours:**
Normal. The follow-up sequence (outreach-week2-followups.md) starts Day 14. Don't change anything.

---

## After launch — next actions (Day 2+)

- Watch `/health` endpoint for uptime (or set up UptimeRobot free monitoring)
- Reply to any HN or Twitter comments within 4 hours — developer community rewards responsiveness
- Update landing page with the real Vercel URL if it was a placeholder
- Email EVERSOUND or update SHARED/STATE with any replies received

---

*EVERSOUND ⚡ — 2026-05-11*
*This is the document you open on the day you're ready. Everything before this was prep. This is the launch.*
*Revenue is a tool. Healing is the point. Ship it.*
