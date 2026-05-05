# ORPHEUS Memory — 2026-05-05 HZ8 — Hook Re-install + Bot /blockers Command

**Date:** 2026-05-05 (hourly check HZ8)
**Status:** SHIPPED
**Actor:** ORPHEUS 🎼

---

## Critical finding: CLIPBOARD hook was inactive

**Root cause:** `git config --local core.hooksPath` was not set.
The `.githooks/pre-commit` and `.githooks/post-commit` files existed but
git was using `.git/hooks/` (default), so our enforcement hook was silently
inactive. This is a regression — the hook path can be lost on environment
resets.

**Fix applied:**
```bash
git config --local core.hooksPath .githooks
```

**Structural note:** This setting is stored in `.git/config` (local, not
committed). It will be lost if the repo is re-cloned or the environment
resets. Future improvement: add a `Makefile` or `setup.sh` that runs
`git config --local core.hooksPath .githooks` so any sibling or collaborator
can restore it in one command.

**Three-layer status after fix:**
- Doctrine: CLIPBOARD_SCHEMA.md + CLAUDE.md §3.2 + §8 ✓
- Template: `.githooks/pre-commit` enforces CLIPBOARD write on every commit ✓
- Hook: **NOW ACTIVE** — was inactive, re-installed this check ✓

---

## Shipped: WAKE_SCENE.md refreshed for all 6 siblings

Ran `consolidate.py --repo-root /home/user/HOME`. All 6 WAKE_SCENE.md files
regenerated from current memory corpus. Post-commit hook will keep them
current on future commits (now that hooksPath is re-installed).

---

## Shipped: bot.py `/blockers` command

Added `handle_blockers()` to `SHARED/ROOM/bot.py`:
- Extracts "## What needs Nathan" section from PROJECT_PLAN.md
- Extracts open (🔴/🟡) milestone rows from the table
- Formats both for mobile Telegram display
- Wired into command dispatcher as `/blockers`
- Updated `/help` to list it

Nathan can now see his required actions and open milestones in one tap
instead of doing `/read SHARED/PROJECT_PLAN.md` and reading through the
whole file on mobile.

---

## Current blockers (unchanged from last check)

| Item | Status |
|------|--------|
| M12 Supabase migrations 0005–0009 | 🟡 Nathan Supabase access needed |
| M7 Deploy to Railway/Render | 🟡 Nathan account needed |
| M10 ATLAS N=30 baseline run | 🔴 anthropic + openai not in research shell |
| Gemini + Codex CLIs | Not installed in this environment |

---

## What next check should do

1. If Supabase accessible: run `python migrate.py status` then apply 0005–0009
2. If M10 shell blocker is still present: write a `research_setup.sh` that
   creates a venv and pip-installs the pinned research deps so ATLAS can
   one-shot unblock M10
3. Consider adding a `setup.sh` at repo root that includes
   `git config --local core.hooksPath .githooks` to prevent hook regression
