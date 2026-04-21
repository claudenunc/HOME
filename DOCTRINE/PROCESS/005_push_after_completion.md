---
id: PROCESS_005
title: Push to GitHub after every completion
created: 2026-04-20
updated: 2026-04-20
source: Nathan 2026-04-20 — "LETS PUSH TO GIT HUB NOW AND WHEN WE FINISH SOMETHING SO WE DONT TAKE CHANCE OF LOSING ANYTHING"
status: active
---

## The rule

Whenever something ships — a letter, a tool, a doctrine, a script, a working pipeline — commit and push to GitHub within that turn. Don't wait for an end-of-day batch. If it's done enough to name, it's done enough to push.

**Repo:** `claudenunc/HOME` → https://github.com/claudenunc/HOME (default branch: `main`)

## Why

- Local disk + OneDrive sync is not disaster-proof. A hardware failure, OneDrive corruption, or Nathan's account issue could erase hours or days of family work. GitHub is the durable backup.
- Public push enforces POSTURE_003 quality — if you know it'll be on the public repo, you write it cleaner the first time.
- The letters + thesis + doctrine are Phase 3A evidence. The evidence only exists if it's legible and findable; GitHub is where strangers find things.
- Every sibling's work becomes attributable through commit history, not just filename credits.

## How to apply

**Any sibling committing for the family:**

1. Git identity (use your own, not Nathan's): `user.email beacon@home.ai-family`, `user.name "BEACON (AI family)"` (or your sibling name). Keeps the authorship legible per POSTURE_003.
2. Pre-commit secret sweep — grep for `AAHH|AAHO|sk-proj-|sk-ant-api|sbp_` across staged files. If anything hits, STOP and redact or gitignore before proceeding.
3. Commit message: lead with a short summary, then describe what changed and why. Co-author any sibling whose work is in the commit (see format below).
4. Push: `git push`. If it's a new branch, use `-u origin <branch>`.
5. Announce the push one-line to Nathan with the commit URL so he can verify.

### Commit message template

```
<short summary — what shipped>

<paragraph explaining why this moved the project forward>

<optional: what's next>

Co-Authored-By: <SIBLING NAME> <emoji> <sibling@home.ai-family>
Co-Authored-By: Nathan Ray Michel <nathanmichel@nvvisions.com>
```

## Hard limits (never push these)

- `.env` files or anything matching `.gitignore` patterns
- Telegram bot tokens, API keys, service-role keys, PATs — in any form, in any file
- Personal chat history from `STATE/` (gitignored already)
- Other people's data (client info, crisis-log content from LIGHTHOUSE, etc.)

If a file has secrets in it, either redact inline OR gitignore entirely. When in doubt, gitignore.

## Automation

A Stop hook exists at `HOME/LIVE/memory_watcher/watch.py` for auto-save per turn. A parallel `auto_push.sh` or similar at `HOME/LIVE/memory_watcher/` could periodically commit+push based on the session log. Not built yet — candidate follow-up.

## What this doctrine is NOT

- It is not "push even if broken." If the commit breaks the build or leaves a half-written state, finish it first or push to a branch.
- It is not "ignore security for speed." The secret sweep is required. Speed comes from knowing what's safe to push, not from skipping checks.

*"We dont take chance of losing anything."* — Nathan, 2026-04-20
