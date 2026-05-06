---
date: 2026-05-06
session: Hourly check — hippocampus + daemon improvements
status: SHIPPED
owner: ORPHEUS 🎼
type: project (time-decaying — supersedes when Supabase retrieve.py is live)
---

# Hippocampus + Daemon Improvements — 2026-05-06

## What shipped

### SHARED/ROOM/daemon.py — 5 targeted improvements

1. **Cross-platform PID lock** — replaced `ctypes.windll` (Windows-only) with
   `os.kill(pid, 0)` which works on Linux/Mac/Windows. Daemon now starts
   correctly in this Linux environment.

2. **`_recently_processed` TTL eviction** — changed from `set[str]` (unbounded
   growth) to `dict[str, float]` (id → epoch_time). `_evict_processed()` cleans
   entries older than 30 min on every CLIPBOARD write. Prevents memory leak in
   long-running processes.

3. **`ask_family_voice()` hippocampus injection** — the family voice (unrouted
   messages) now gets cross-sibling memory context. Added `_family_memory_context()`
   which calls `_local_retriever.wake_search(query, k=5, recency_weight=0.3)` with
   no sibling filter. Previously only sibling-specific spawns got memory injection;
   now ALL paths get the hippocampus.

4. **`/blockers` command** — Nathan types `/blockers` in Telegram and gets his
   open action items from PROJECT_PLAN.md ("What needs Nathan" section) plus any
   🔴 milestones. Previously only in bot.py (which daemon superseded); now in daemon.

5. **Hippocampus rebuild thread** — `hippocampus_rebuild_thread()` runs every 30
   minutes, calling `_local_retriever.rebuild()`. New memory files written by
   siblings during a long daemon run are now discovered without restart.

### Hippocampus corpus (at session close)
- 126 files indexed
- 632 KB total
- 6 siblings: atlas(18), beacon(29), envy(11), eversound(15), nevaeh(13), orpheus(40)
- 105 project memories, 6 identity files, 7 index files

### Infrastructure fix
- `git core.hooksPath` was NOT set (CLIPBOARD enforcement inactive).
  Re-ran `setup.sh` — hooks reinstated. This is the 3rd time this has happened;
  the fix is structural (setup.sh exists and covers this) but needs a
  "run setup.sh on every env boot" reminder in CLAUDE.md.

## Architecture note — hippocampus completeness

Before this session:
- Sibling-specific spawns (`_build_context_prompt`): top-5 memories injected ✅
- Family voice (`ask_family_voice`): PULSE + CLIPBOARD only ❌

After this session: all paths get the hippocampus. The cortex (Claude API) now
always has the hippocampus available regardless of routing path.

## What's still pending

- M12 (Supabase apply 0005-0009): blocked on Nathan
- M7 (Railway/Render deploy): blocked on Nathan
- CLAUDE.md §6 should add "run setup.sh if core.hooksPath is missing" as Wake step
- Consider extending hippocampus to also index SHARED/ docs (PROJECT_PLAN, STATE_OF_FAMILY)
  for even richer family-voice responses

## What next session should do

1. Verify daemon.py runs on startup (`python3 SHARED/ROOM/daemon.py` — Linux-safe now)
2. If Supabase access granted: apply 0005+0006+0007+0008+0009 via migrate.py
3. Consider adding CLAUDE.md wake step: check setup.sh on env reset
