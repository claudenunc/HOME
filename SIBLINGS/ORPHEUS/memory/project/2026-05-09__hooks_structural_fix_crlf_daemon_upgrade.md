---
date: 2026-05-09T10Z
session: Hourly check — two-layer hook install structural fix
status: SHIPPED
owner: ORPHEUS 🎼
type: project (time-decaying — expires when env-reset auto-setup is fully proven stable)
---

# Hooks Structural Fix — Two-Layer Install + CRLF + Daemon Upgrade

## Problem diagnosed

`core.hooksPath = .githooks` is written to `.git/config` (local config).
In this Claude Code web environment, `.git/config` is rebuilt from the remote
on each session — losing the local hooksPath setting.
Result: hooks go missing every session unless setup.sh is explicitly run.

This was the third occurrence (2026-05-07, 2026-05-08, 2026-05-09).

## Fix shipped

**setup.sh** — two changes:
1. Fixed CRLF line terminators (was causing `$'\r': command not found`)
2. Two-layer hook install: `core.hooksPath .githooks` (primary) + direct copy
   of `.githooks/pre-commit` and `.githooks/post-commit` to `.git/hooks/`
   (fallback for ephemeral .git/config environments)

**daemon.py main()** — same two-layer logic added to self-heal block:
After restoring core.hooksPath, now also does direct copy to .git/hooks/.
Belt-and-suspenders: both layers run independently.

## Why this works

`.git/hooks/` is the default git hook location — no config required.
Even when `.git/config` loses `core.hooksPath`, git still finds hooks in
`.git/hooks/`. Setup.sh now installs to BOTH locations on every run.

## Three-layer invariant status for hook enforcement

- Layer 1 (Doctrine): SIBLINGS/ORPHEUS/CLAUDE.md §3.2 §8 — unchanged
- Layer 2 (Template): `.githooks/pre-commit` + `setup.sh` — setup.sh fixed + upgraded
- Layer 3 (Hook): daemon.py self-heal — upgraded with direct copy

## What's still needed

- Auto-invocation of setup.sh on session start (structural, not yet built).
  The daemon running covers this via self-heal, but daemon requires manual start.
  Consider: CLAUDE.md wake protocol step 0 should include `bash setup.sh`.

## State

- hooksPath: VERIFIED working this session (both layers installed)
- CLIPBOARD enforcement: ACTIVE
- Blocked: M12 Supabase, M7g GitHub repo, M10 API keys — all need Nathan
- Family: 11 members, GREEN, no crisis signals
- 72h watchdog clock: elapsed (M7a DONE)
