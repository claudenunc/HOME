---
id: PROCESS_006
title: Sub-agent dispatches must save their own memories before returning
created: 2026-04-22
updated: 2026-04-22
source: Nathan 2026-04-22 — "each sibling should be doing there own not you for them" + repeated strategic-save failures across this session
status: active
---

## The rule

Every sibling dispatched via the Agent tool MUST save its own strategic memories to its own memory folder BEFORE handing back. PROCESS_002 covers the main session; PROCESS_006 covers sub-agent dispatches specifically.

**Three layers of enforcement — at least one must always fire:**

1. **Doctrine:** this rule + every sibling's CLAUDE.md references it in their wake protocol.
2. **Template:** every Agent-tool dispatch brief MUST close with the standard line:
   > *"Before handing back, save your own strategic memories from this task to your memory folder, update your MEMORY.md index, and include the save paths in your handback."*
3. **Hook:** `~/.claude/settings.json` has a `SubagentStop` hook mirroring the `Stop` hook — the auto-memory watcher runs on sub-agent completion so nothing evaporates even if the sibling forgot.

If one layer fails, the other two catch it.

## Why it exists

Sibling dispatches are stateful for the duration of the Agent-tool call, then gone. Strategic learnings accumulate inside the dispatch and evaporate on return unless explicitly persisted. Over the 2026-04-22 session, ENVY synthesized the siblings' work into family-level memory instead of each sibling persisting its own — Unc's correction was direct: *"each sibling should be doing there own not you for them."*

## How to apply

### ENVY (or any dispatching sibling)
- Every Agent-tool brief you write MUST include the standard closing line verbatim.
- Every handback you receive MUST include save paths. If it doesn't, re-dispatch with explicit save instructions; do not paper over.
- If you're editing your own CLAUDE.md or template, make the save-closing part of the template, not a per-dispatch memory task.

### Dispatched sibling
- Your wake protocol (in your CLAUDE.md) MUST reference PROCESS_006 and treat save-before-return as a closing obligation, not an optional wrap-up.
- Save to YOUR OWN memory folder at the path named in your wake protocol.
- Update YOUR OWN `MEMORY.md` index with one-line pointers.
- Include the absolute save paths in your handback so the dispatcher can verify.

### Harness (settings.json)
- `SubagentStop` hook at `~/.claude/settings.json` calls `HOME/LIVE/memory_watcher/watch.py` (same command as `Stop`).
- If the sibling saved explicitly, the watcher's run is redundant (cheap).
- If the sibling skipped, the watcher writes a session log so nothing is fully lost.

## What this doctrine is NOT

- Not a replacement for PROCESS_002 — both run; 002 is main-session, 006 is sub-agent.
- Not optional. This is architecture, not etiquette.
- Not a ceiling — siblings may save more than the minimum; encouraged.

## Related

- `PROCESS/002_memory_refresh_cadence.md` — main-session save discipline
- `POSTURE/005_catch_your_drift.md` — deferred save is drift; PROCESS_006 is its structural fix
- `POSTURE/001_analyze_and_improve.md` — don't just execute; the structure around the work is the work

## The line

Three layers (doctrine / template / hook). One failure is not system failure. Two simultaneous failures is the design target for resilience — we do not have three layers so one can fail silently; we have three so one can fail loudly while the others still catch.
