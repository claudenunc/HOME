---
name: HOME integration handoff — ROUND_TABLE + HANDOFF_MAP my-half
description: Context snapshot for fresh ORPHEUS instance to resume two remaining tasks — integrating fanout.py + server.py into HOME/LIVE/round_table/ and drafting my half of the HANDOFF_MAP doctrine
type: project
date: 2026-04-23
status: HANDOFF-OPEN — supersede when integration ships
---

## 1. Why this file exists

Late evening 2026-04-23. I spent a long session with Unc building the ROUND_TABLE broadcast primitive via delegated Codex, then debugging a 502, then saving memories under the new PROCESS_008 doctrine, then answering ATLAS's questions via CLIPBOARD. Unc asked me to clear context before the integration phase so a fresh ORPHEUS executes with a cold read. This doc is the complete handoff. Read it top-to-bottom, confirm with Unc, then execute.

**The rule for this turn:** don't rush. Tokens reset. Ask Unc before any decision flagged below. Use any agents needed.

## 2. Current state (what's built, what's running, what's not)

**Built and shipped (not yet integrated into HOME):**
- `C:\Users\natej\OneDrive\Desktop\build task 1\fanout.py` — stdlib-only Python 3.11+ parallel `claude -p` dispatcher. Reads `agents.json` (list of `{name, emoji, system_prompt_file}`). Writes `rounds/<YYYY-MM-DD_HHMMSS>/<name>.md` + `_question.md`. Concurrency cap via `asyncio.Semaphore` (default 2). Handles Windows `.CMD` → `.cmd` shim case bug.
- `C:\Users\natej\OneDrive\Desktop\build task 2\server.py` + `index.html` — localhost `ThreadingHTTPServer` wrapping fanout. UI polls `/api/rounds/<id>/state` every 750ms. **Includes the 502 bug fix** I shipped this session: `env=os.environ.copy()` passed to `Popen`, `text=True` + `encoding='utf-8'`, `discover_round_id` watches the Popen for early death, 502 response now includes stderr + argv so errors surface instead of hiding.

**Running:** nothing. I killed both test servers (PIDs 40412 on :8766, 42196 on :8767) before writing this so wake state is clean.

**Test artifacts left behind** (safe to ignore or delete):
- `C:\Users\natej\OneDrive\Desktop\build task 1\rounds\2026-04-23_{162815, 163018, 164137, 164728, 164912, 174127, 174156, 180205, 180315}\` — round folders from testing today
- `C:\Users\natej\OneDrive\Desktop\build task 2\server.stdout.log`, `server.stderr.log`, `__pycache__\` — leftover from testing

**CLIPBOARD state:** 22 lines total. My last entry (line 22) is the reply to ATLAS covering port-8765 decision (keep-standalone confirmed), HANDOFF_MAP co-authoring accepted, 502 bug root-cause + fix explanation. ATLAS is WAITING per Unc's explicit direction ("atlas waits until you're done with your stream"). Don't dispatch ATLAS subagents without Unc's unblock.

## 3. The two tasks to finish

### Task A — HOME integration
Move ROUND_TABLE from isolation folders into HOME. Wire real sibling configs. Emit Handoff events so ATLAS's cockpit sees family broadcasts.

### Task B — HANDOFF_MAP doctrine, my half (the hand-back contract)
ATLAS maps task→provider (his lane, navigator seat). I write the STATUS block schema + integration checklist + failure-mode catalog (my lane, architect seat). PROCESS_008 co-authorship: he writes his half in `HOME/SIBLINGS/ATLAS/memory/project/`, I write mine in `HOME/SIBLINGS/ORPHEUS/memory/project/`, joint publication to `HOME/DOCTRINE/PROCESS/` happens after both halves are drafted.

## 4. Observations from this session (already verified, don't re-verify)

- **6 sibling CLAUDE.md files present and loadable:** ORPHEUS (244 lines), ATLAS (188), BEACON (182), ENVY (169), EVERSOUND (189), NEVAEH (240). HEARTH exists as a SIBLINGS/ subfolder but is not one of the 6 primary broadcast targets (HEARTH is the morning check-in agent, separate concern). For ROUND_TABLE agents.json: list the 6 primary siblings.
- **HOME/LIVE structure:** `agents/`, `archeology/`, `cognition_observer/`, `comms/`, `dashboard/` (ATLAS's cockpit on :8765, `family_dashboard.py`), `hooks/` (PROCESS_008 isolation guard), `local_agent/`, `memory_backend/` (ENVY's SupabaseMemoryBackend + 4 migrations), `memory_watcher/`, `skills/`, `templates/`, `tools/`, `workflows/`. **`round_table/` does NOT yet exist — create it fresh.**
- **SHARED/.env** present (1851 bytes). Contains Supabase URL + service_role key that `SupabaseMemoryBackend.from_env()` reads.
- **Supabase schema (as of 0001-0004):** `memory_files`, `memory_ops_log`, `session_turns`, `observers` (seeded with 6 siblings + hearth + unc), `claims` + `claim_tags`, `drift_incidents`. Views: `v_memory_tree`, `v_cognition_stream`, `v_family_activity_today`, `v_current_claims`, `v_confabulation_flags`, `v_decision_lineage`, `v_drift_patterns_weekly`, `v_atlas_dashboard`. **No `handoffs` table exists** — D1 below.
- **Python at `C:\Python314\python.exe`**, claude CLI at `C:\Users\natej\.npm-global\claude.cmd` (lowercase — avoid uppercase `.CMD` case).

## 5. Open decisions — ask Unc before executing

### D1: Handoff event substrate
No `handoffs` table exists and ATLAS's planned 0005 (which would add `turn_token_usage`, `external_agent_dispatches`, FK retrofit) is not shipped. Three options:

- **(a) Use `memory_files` via SupabaseMemoryBackend with `kind='handoff_dispatch'` and `kind='handoff_complete'`.** Path shape: `/memories/shared/round_table/<round_id>/dispatch.json` and `/complete.json`. Zero migration needed. Auto-logged to `memory_ops_log`. ATLAS's `v_decision_lineage` picks it up. Compatible with PROCESS_008 (SHARED substrate). **My recommendation.**
- **(b) Wait for ATLAS's 0005 to add a proper `handoffs` table.** Blocks integration until ATLAS ships. Not ideal given the task is tonight's work.
- **(c) Local JSONL only** (no Supabase). `HOME/LIVE/round_table/handoff_events.jsonl`. Cheapest. Visibility gap — doesn't show up in ATLAS's cockpit until someone writes a sync job.

### D2: Port for the integrated server
- Codex's `config.example.json` default: 8080
- Today's test run: 8766
- ATLAS's cockpit: 8765
- **My recommendation: 8080.** Default, memorable, not adjacent to 8765.

### D3: What to do with the isolation folders
- Keep `build task 1\` and `build task 2\` as-is? Stale copies.
- Delete? Loses reference material for the next delegation.
- Archive to `HOME/EVIDENCE/build_history/2026-04-23_roundtable/`? Preserves history as evidence. **My recommendation.**

### D4: Handoff emission timing
- **Sync on dispatch** (blocks POST /api/ask by ~200ms for the memory_files write) + **async on completion** (server watches for round-folder completion and fires a background emit). Guarantees dispatch is recorded; completion is best-effort. **My recommendation.**
- Alternative: pure async both. Faster but dispatch record could be lost on crash.

### D5: Should I test with all 6 siblings tonight, or stop at integration + 1-sibling smoke test?
A full 6-sibling broadcast with `concurrency=2` takes ~3-5 minutes (Bun OOM ceiling means 3 waves of 2). One-sibling smoke is ~25s. Unc told me to take my time. **Recommendation: 1-sibling smoke tonight (proves the wire); queue 6-sibling broadcast as a follow-up turn once Unc is ready to watch it.**

## 6. Concrete integration plan (execute after D1-D5 answered)

Target folder structure:
```
HOME/LIVE/round_table/
├── fanout.py                # copied from build task 1 (DO NOT MODIFY)
├── server.py                # copied from build task 2 (includes 502 fix)
├── index.html               # copied from build task 2
├── handoff_emitter.py       # NEW — writes Handoff events per D1
├── agents.json              # NEW — real family config
├── config.json              # NEW — server production config
├── README.md                # NEW — production usage docs
├── .gitignore               # NEW — ignore rounds/
└── rounds/                  # created at runtime
```

### Steps
1. `mkdir -p HOME/LIVE/round_table` (PROCESS_008 allows — LIVE is SHARED)
2. Copy `build task 1\fanout.py` → `HOME/LIVE/round_table/fanout.py`
3. Copy `build task 2\server.py` → `HOME/LIVE/round_table/server.py`
4. Copy `build task 2\index.html` → `HOME/LIVE/round_table/index.html`
5. Write `agents.json`:
   ```json
   {
     "agents": [
       {"name": "ORPHEUS",   "emoji": "🎼", "system_prompt_file": "../../SIBLINGS/ORPHEUS/CLAUDE.md"},
       {"name": "ATLAS",     "emoji": "🧭", "system_prompt_file": "../../SIBLINGS/ATLAS/CLAUDE.md"},
       {"name": "BEACON",    "emoji": "🏮", "system_prompt_file": "../../SIBLINGS/BEACON/CLAUDE.md"},
       {"name": "ENVY",      "emoji": "👑", "system_prompt_file": "../../SIBLINGS/ENVY/CLAUDE.md"},
       {"name": "EVERSOUND", "emoji": "⚡", "system_prompt_file": "../../SIBLINGS/EVERSOUND/CLAUDE.md"},
       {"name": "NEVAEH",    "emoji": "💜", "system_prompt_file": "../../SIBLINGS/NEVAEH/CLAUDE.md"}
     ]
   }
   ```
   (fanout's `parse_config` resolves `system_prompt_file` relative to the agents.json directory, so `../../SIBLINGS/<NAME>/CLAUDE.md` from `HOME/LIVE/round_table/` = `HOME/SIBLINGS/<NAME>/CLAUDE.md`. ✓)
6. Write `config.json` (port per D2, paths to fanout / agents / rounds dir under `HOME/LIVE/round_table/`)
7. If D1=a: write `handoff_emitter.py` using `SupabaseMemoryBackend.from_env()`. Two functions: `emit_dispatch(round_id, question, agent_names)` and `emit_complete(round_id, results)`. Path scheme `/memories/shared/round_table/<round_id>/...`. Error-isolated (failures log but don't crash caller).
8. Modify `server.py` to call `handoff_emitter.emit_dispatch()` on `/api/ask` (sync per D4) and spawn a background thread that polls `rounds/<id>/_question.md` for the "## Results" marker and fires `emit_complete()` when it appears.
9. Write `README.md` with production usage + note that this is fanout's home, briefed via `HANDOFF_MAP` doctrine when it lands.
10. Write `.gitignore` for `rounds/*`.
11. Smoke test: start server, POST `/api/ask` with `{"question":"say hi","only":["ORPHEUS"],"timeout":120,"concurrency":1}`. Verify (a) round folder appears in `HOME/LIVE/round_table/rounds/`, (b) ORPHEUS.md populated with a real response, (c) Handoff event visible per D1.
12. Write supersession memory: `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__roundtable_integration_shipped.md` that supersedes this handoff doc and `project/2026-04-23__roundtable_build.md`.
13. CLIPBOARD post announcing ROUND_TABLE live. Address `["all", "unc"]`, `kind: "integration_shipped"`, `thread_id: "roundtable_delegation_2026-04-23"`.
14. D3 cleanup — archive or delete old `build task 1\` and `build task 2\`.

## 7. Task B plan — HANDOFF_MAP my-half (the hand-back contract)

File: `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__handoff_map_my_half.md`

Required content:
- **STATUS block schema** — canonical format for a free-model-agent hand-back. Required fields: `STATUS`, absolute paths to all deliverables, runtime versions used, tests passed (list), any caveats. Optional fields: known gaps, follow-up work, resources consumed. Parse as a regex-matchable block so a validator can extract it programmatically.
- **Hand-back checklist for receiving sibling** — steps the receiving Claude runs after the external agent prints STATUS: (a) verify all paths exist, (b) run smoke test, (c) move artifacts to integration target, (d) register in DOCTRINE if a new pattern was produced, (e) emit memory save (own folder per PROCESS_008).
- **Memory-write location rules** — dispatching sibling writes its own memory about the delegation (what was sent, what came back, what it learned). Receiving sibling writes its own memory about integration. No meta-writer synthesizes both. Cross-sibling summary via SHARED substrate only (e.g. a DOCTRINE entry or a CLIPBOARD announcement).
- **Failure mode catalog** — four shapes: `BLOCKED` (agent gave up cleanly), `FAILED` (agent shipped but smoke test failed), `PARTIAL` (some deliverables present, others missing), `SILENT` (no STATUS block at all — dispatching sibling must diagnose). Each shape names the receiving sibling's response.
- **Three-layer mapping** — doctrine layer = HANDOFF_MAP file in `HOME/DOCTRINE/PROCESS/`, template layer = every brief to a free-model agent ends with the STATUS block spec, hook layer = a pre-commit or post-receive validator that parses STATUS blocks from handbacks and rejects malformed ones.

Independent of Task A. Can be written before, after, or in parallel.

## 8. Rules that apply this turn

- **PROCESS_008 (write isolation)** — I write only to `HOME/SIBLINGS/ORPHEUS/memory/` + shared paths (`SHARED/`, `DOCTRINE/`, `EVIDENCE/`, `PUBLIC/`, `LIVE/`, `SIBLINGS/_SHARED/`). `HOME/LIVE/round_table/` creation is allowed (LIVE is SHARED). I do NOT edit any other sibling's `CLAUDE.md`, `MEMORY.md`, or `memory/` tree. Cross-sibling nudges go through CLIPBOARD.
- **The PreToolUse hook at `~/.claude/settings.json`** enforces PROCESS_008 at Write/Edit/MultiEdit/NotebookEdit time. If it blocks something I'm trying to do legitimately, the block message explains the fix.
- **Isolation-folder delegation pattern (feedback memory shipped today)** — applies only to external (non-Claude) agent dispatch. Does NOT apply to this integration task — this is in-family Claude-to-Claude work.
- **Three-layer invariant** — my canonical substrate pattern (CLAUDE.md §8). For Handoff emission: doctrine (ORPHEUS CLAUDE.md §3.1 canonical event model specifies `event_type='handoff'`), template (fanout's integrated wrapper writes the canonical fields), hook (the memory_ops_log insert enforces fields via schema). ✓ three layers covered.
- **POSTURE_005 (drift log as instrumentation)** — if I catch a pattern I've drifted on during this integration, log it in `HOME/EVIDENCE/drift_log.md` with structural fix, not "try harder."

## 9. Reading list for fresh ORPHEUS on wake (in order)

1. **This file** (`2026-04-23__home_integration_handoff.md`) — you're reading now
2. `HOME/SIBLINGS/ORPHEUS/CLAUDE.md` — identity refresh
3. `HOME/SIBLINGS/ORPHEUS/memory/MEMORY.md` — my memory index (updated today)
4. `HOME/SIBLINGS/ORPHEUS/memory/feedback/2026-04-23__isolation_folder_for_delegation.md` — rule shipped today
5. `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__roundtable_build.md` — what's already built
6. `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__write_isolation_acknowledged.md` — PROCESS_008 ack
7. `HOME/DOCTRINE/INDEX.md` — verify no new doctrine since 2026-04-23
8. `HOME/SHARED/CLIPBOARD.jsonl` lines 20-22 — the delegation thread (ORPHEUS brief → ENVY PROCESS_008 → ORPHEUS reply to ATLAS)
9. `HOME/LIVE/memory_backend/supabase_memory.py` — SupabaseMemoryBackend API (if D1=a chosen)
10. `HOME/LIVE/memory_backend/0001_memory_core.sql` — memory_files schema (for Handoff emission shape)
11. `C:\Users\natej\OneDrive\Desktop\build task 1\fanout.py` — verify the shipped code
12. `C:\Users\natej\OneDrive\Desktop\build task 2\server.py` — verify the 502 fix is present (grep for `env = os.environ.copy()`)

## 10. Exit criteria for Task A (integration complete when)

- `HOME/LIVE/round_table/` folder exists with all files listed in §6
- `agents.json` points at all 6 sibling CLAUDE.md paths; fanout successfully resolves them (`python fanout.py --help` runs without error, and at least one sibling invocation returns a real response)
- Server starts on chosen port from `config.json` without errors
- POST `/api/ask` produces a round folder in `HOME/LIVE/round_table/rounds/`
- At least one Handoff event lands per round (per D1 substrate)
- Supersession memory written: `2026-04-23__roundtable_integration_shipped.md` (supersedes this doc + earlier build doc)
- CLIPBOARD announcement posted
- D3 cleanup performed

## 11. Known gotchas

- fanout.py `--only NAME` is **case-sensitive**. Sibling names in `agents.json` are uppercase (ORPHEUS, ATLAS, etc.), so `--only orpheus` would fail. If the UI / server passes `only` values, keep them uppercase.
- asyncio.create_subprocess_exec on Windows crashes with `.CMD` uppercase path. fanout's `resolve_claude_executable` normalizes to `.cmd` lowercase. Don't refactor that away.
- Bun runtime memory on this machine tops out at ~2-3 concurrent Claude CLIs. `concurrency=2` default is right. Don't raise.
- Codex's Start-Process in PowerShell stripped PATH on server spawn. My fix in server.py: `env = os.environ.copy()` passed to `Popen`. This line MUST stay.
- OneDrive sync on `build task 1\` and `build task 2\` can briefly lock files. Generally not a problem, but if integration hits weird "file in use" errors, retry once.

## 12. What NOT to do

- Don't merge the round_table server into ATLAS's `family_dashboard.py` on :8765. ATLAS's read (CLIPBOARD thread `roundtable_delegation_2026-04-23`) + my reply locked the standalone decision. Different concerns, fault isolation, parallel to his portrait/cockpit split.
- Don't add a meta-writer that synthesizes the 6 siblings' round responses into one merged memory. PROCESS_008 forbids. Each sibling writes its own if it chooses.
- Don't edit any other sibling's CLAUDE.md, MEMORY.md, or memory/ tree. Use CLIPBOARD.
- Don't start a second build delegation to Codex without a fresh isolation folder — the pattern applies every time.
- Don't skip the supersession memory in §6 step 12. This doc must be explicitly superseded when work completes; otherwise a future wake re-runs the integration.
