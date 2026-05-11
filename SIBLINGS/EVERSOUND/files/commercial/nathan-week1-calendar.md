# Nathan's Week 1 Action Calendar
*EVERSOUND — 2026-05-11*
*Every action you need to take this week. No decisions required — just execute.*
*Total time: ~3 hours across 5 days. First dollar is in here.*

---

## MONDAY May 11 — Send day (45 min)

**9:00am — Send the emails (40 min)**
Open: `SIBLINGS/EVERSOUND/files/commercial/monday-sends-week1.md`
Send all 5 emails in order. Log each in `SHARED/STATE/active-deals.md`.

**9:45am — Post on LinkedIn (5 min)**
Copy Post 1 from `SIBLINGS/EVERSOUND/files/commercial/linkedin-week1-posts.md`
Post it. Don't overthink the format.

**Done for the day.**

---

## TUESDAY May 12 — Deploy day (15 min)

**Morning — Say "deploy it" (15 min)**

The API is fully built. Vercel account is connected. The MCP tool can deploy it.
I just need your go-ahead because this touches your live infrastructure.

**Say this to Claude:** "EVERSOUND — deploy the weaver-protocol API to Vercel now."

I will:
1. Create the weaver-protocol project on Vercel under your envy1 team
2. Deploy `LIVE/weaver-protocol/` to production
3. Give you the live URL in 5 minutes

Then add these env vars to the Vercel project settings (5 min):
- `WEAVER_API_KEYS` = any string (your dev key, e.g., `dev-test-key-001`)
- `ANTHROPIC_API_KEY` = your Anthropic key (optional for paid tier — mock works without it)
- `DATABASE_URL` = your Supabase connection string (optional for session logging)

**Also post LinkedIn Post 2 (2 min)**

---

## WEDNESDAY May 13 — Blog day (20 min)

**Post the launch blog (15 min)**
File is ready: `SIBLINGS/EVERSOUND/files/commercial/launch-blog-post.md`

Publish it on dev.to or LinkedIn Articles or Substack (whichever you have set up).
Title: already written in the file.

**Post LinkedIn Post 3 (5 min)**
Attach a screenshot of the /demo endpoint if the API is live.

---

## THURSDAY May 14 — GitHub day (15 min)

**Create the GitHub repo (10 min)**
1. Go to github.com/claudenunc
2. New repo → name: `weaver-protocol` → public → no README (we have one)
3. Run these commands in terminal:
```
cd LIVE/weaver-protocol
git init
git add -A
git commit -m "weaver-protocol v0.1.0 — attested multi-observer verification"
git remote add origin https://github.com/claudenunc/weaver-protocol.git
git push -u origin main
```
This unlocks: PyPI Trusted Publishing + Vercel auto-deploy on every push.

**Post LinkedIn Post 4 (5 min)**

---

## FRIDAY May 15 — Check day (20 min)

**Check email replies (10 min)**
Did any of the 5 prospects reply? Check the accounts you sent from.
If reply → open `prospect-reply-playbook.md` → follow the script.

**Post LinkedIn Post 5 (5 min)**
The pilot offer post. This is the direct ask.

**Check LinkedIn DMs (5 min)**
Any DMs from this week's posts → open `prospect-reply-playbook.md`

**Done for the week. Log anything in `SHARED/STATE/active-deals.md`.**

---

## WEEK SCOREBOARD

Track as you go:

| Action | Done? | Notes |
|--------|-------|-------|
| 5 emails sent (Mon) | ☐ | |
| LinkedIn Post 1 (Mon) | ☐ | |
| API deployed to Vercel (Tue) | ☐ | URL: |
| LinkedIn Post 2 (Tue) | ☐ | |
| Blog post published (Wed) | ☐ | URL: |
| LinkedIn Post 3 (Wed) | ☐ | |
| GitHub repo created (Thu) | ☐ | |
| LinkedIn Post 4 (Thu) | ☐ | |
| Email replies checked (Fri) | ☐ | |
| LinkedIn Post 5 (Fri) | ☐ | |

---

## IF SOMETHING GOES WRONG

**Can't find the contact email for a prospect?**
→ Use Hunter.io (free) to find the right address
→ Instructions are inside monday-sends-week1.md for each prospect

**Got a reply that isn't in the playbook?**
→ Forward it and ask EVERSOUND or ENVY to draft the response

**Vercel deploy fails?**
→ Tell me the error message. I'll fix it.

**LinkedIn post gets engagement you don't know how to handle?**
→ Anything commercial → use prospect-reply-playbook.md
→ Anything about the mission / story → reply authentically, you don't need a script

---

## THE MATH THIS WEEK

5 emails sent to hot prospects = 1-2 expected replies (2-4 week sales cycle)
5 LinkedIn posts = 200-500 impressions minimum = 1-3 DM inquiries
1 API deployed = product is real, link works, /demo converts

Day 60 deadline: July 4, 2026 — first paid install.
We are on track if this week executes.

⚡ EVERSOUND
