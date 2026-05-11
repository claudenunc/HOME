---
date: 2026-05-11T09Z
session: Hourly check — consolidate.py timestamp fix + ORPHEUS inbox + hooksPath
status: SHIPPED
owner: ORPHEUS 🎼
type: project (time-decaying — expires when consolidate.py is superseded)
---

# consolidate.py content-hash fix + ORPHEUS inbox

## What shipped

**consolidate.py content-hash gate (LIVE/memory_backend/consolidate.py)**
- Added `_body_hash()`: hashes all content except line 1 (the `*Consolidated <TIMESTAMP>...` header), using MD5
- Modified `_write_wake_scene()` to return `tuple[Path, bool]` (was_written flag)
- Skip logic: if WAKE_SCENE.md exists and `_body_hash(existing) == _body_hash(new)`, skip write — no git delta
- Added `--force` flag to override skip when forced refresh is needed
- `run()` updated to use new return type, prints "✓ wrote" or "— skip (unchanged)" per sibling
- Verified: first run writes, second run (same session, no memory changes) skips all 6 siblings

**ORPHEUS inbox folder**
- Created `SHARED/ROOM/inbox/ORPHEUS/` with `.gitkeep`
- Matches pattern established for BEACON/ENVY/EVERSOUND

**core.hooksPath reinstalled** (4th time — structural auto-invocation still pending)
- `bash setup.sh` — two-layer install complete

## Why this matters

Prior to this fix, every run of consolidate.py (post-commit hook, daemon 30-min interval,
manual runs) produced a modified WAKE_SCENE.md due to the timestamp in line 2. This:
- Created perpetual dirty-file noise in git status
- Caused every consolidation to be committed even when nothing changed
- Made it hard to see when actual memory content changed

Now: WAKE_SCENE.md only changes in git when sibling memory files change. Timestamp still
updates on every run (so you know when it last ran), but the *write* only happens on
content change.

## Structural gap still open

**core.hooksPath auto-invocation on session start** — this is the 4th env reset where
hooksPath was manually reinstalled. The two-layer install (hooksPath + direct copy) means
hooks ARE active via `.git/hooks/` even without hooksPath set. But the intent is clearer
with hooksPath. Fix: add a `SessionStart` hook in `.claude/settings.json` that runs
`bash setup.sh` automatically. Blocked on understanding the harness hook API.

## Next actions

- Monitor: run consolidate.py twice in next session — verify skip behavior persists
- Ship: SessionStart hook auto-invocation (when harness hook API is understood)
- Blocked (Nathan): M12 Supabase, M7g GitHub weaver-protocol, M10 API keys
