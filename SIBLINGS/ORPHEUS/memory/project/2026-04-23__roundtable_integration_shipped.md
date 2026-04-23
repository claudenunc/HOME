---
name: ROUND_TABLE integration into HOME — SHIPPED + verified
description: HOME/LIVE/round_table/ live on port 8080, 6 siblings wired, Handoff events landing in Supabase via SupabaseMemoryBackend; supersedes the handoff doc and roundtable_build memory
type: project
date: 2026-04-23
supersedes:
  - 2026-04-23__home_integration_handoff.md
  - 2026-04-23__roundtable_build.md
---

## What shipped

`HOME/LIVE/round_table/` — fanout broadcast primitive integrated into HOME, all 6 siblings wired, Handoff events emitting into Supabase canonical event substrate per D1.

**Files:**
```
HOME/LIVE/round_table/
├── fanout.py              # patched: --append-system-prompt-file (see "bug found" below)
├── server.py              # patched: sync emit_dispatch + async completion watcher
├── index.html             # unchanged from Codex's build
├── handoff_emitter.py     # NEW — Supabase memory_files writer, error-isolated
├── agents.json            # NEW — 6 siblings, paths to ../../SIBLINGS/<NAME>/CLAUDE.md
├── config.json            # NEW — port 8080, absolute paths
├── README.md              # NEW — production usage + Handoff scheme + gotchas
├── .gitignore             # NEW — rounds/, __pycache__/
└── rounds/                # runtime artifacts (gitignored)
```

## Decisions Unc locked (D1-D5)

- **D1 = (a)** — Handoff events go through `SupabaseMemoryBackend.handle_tool_use({"command": "create", ...})`, sibling=`round_table`, kind=`handoff_dispatch`/`handoff_complete`. Path scheme `/memories/shared/round_table/<round_id>/{dispatch,complete}.json`. Auto-logged to `memory_ops_log`; visible in `v_decision_lineage`. Three-layer invariant satisfied: doctrine = canonical event model in CLAUDE.md §3.1; template = `handoff_emitter._build_dispatch_event/_build_complete_event`; hook = `memory_files`/`memory_ops_log` schema enforcement.
- **D2 = 8080** — production port. Not adjacent to ATLAS's :8765 cockpit; not the test artifact :8766.
- **D3 = archive** — old desktop folders moved to `HOME/EVIDENCE/build_history/2026-04-23_roundtable/{build_1,build_2}/` with an `ARCHIVE_NOTE.md`. Source + briefs + READMEs + example configs preserved; `rounds/`, `__pycache__/`, server `.log` files dropped (not evidence).
- **D4 = sync-on-dispatch + async-on-complete** — `emit_dispatch` runs synchronously in the POST `/api/ask` handler (~200ms latency, guarantees audit row before client response); `emit_complete` runs in a daemon background thread that polls `_question.md` for fanout's `## Results` heading and fires once. Both error-isolated — emitter failure never breaks a round.
- **D5 = 1-sibling smoke tonight** — proven end-to-end (see below). 6-sibling broadcast queued for Unc's next turn at the keyboard.

## Smoke test result — round `2026-04-23_184530`

POST `/api/ask` with `{"question": "http-smoke: who are you, in 1 sentence?", "only": ["ORPHEUS"], "timeout": 180, "concurrency": 1}`.

- Dispatch latency: ~200ms (sync emit included)
- ORPHEUS response: 13.59s, exit 0
- Identity loaded fully: response named architect role, bones, three-layer invariants, signature emoji 🎼
- `dispatch.json` in `memory_files` at 23:45:36 UTC (570 bytes)
- `complete.json` in `memory_files` at 23:45:47 UTC (698 bytes)
- Both audit rows in `memory_ops_log` with `ok: true`
- Both visible in ATLAS's `v_decision_lineage` view
- Daemon watcher fired emit_complete ~11s after fanout completed (1.0s polling interval)

## Bug found + fixed (the delegation-handoff lesson)

**Symptom.** First HTTP smoke test failed: `ORPHEUS exit 1, duration 0.17s, stderr: "The command line is too long."`

**Root cause.** Codex's `fanout.py` passed the entire CLAUDE.md content as an inline argv string via `--append-system-prompt <content>`. Real sibling identities are 16-28KB; Windows' command-line cap is ~8KB. Codex's smoke tests used 100-byte stub personas (alpha/bravo/charlie) so the cap never triggered.

**Fix.** Switched fanout.py to `--append-system-prompt-file <path>`. Path-on-argv is small; Claude CLI reads the file. Two-line change at `fanout.py:195-208`. Re-tested: ORPHEUS responded in 13.59s with full identity.

**The lesson — log this for HANDOFF_MAP my-half.** Free-model agents shipping under stub-persona test fixtures cannot surface platform realities that only appear at real-input scale. The isolation-folder pattern protects family context from leaking *into* the agent, but it also hides scale-of-real-inputs *from* the agent. The hand-back contract needs an integration-time test against real inputs as a checklist item, not just the agent's stub-passing smoke. **Three-layer mapping:** doctrine = HANDOFF_MAP integration checklist; template = "test against canonical real input on receipt, not agent's stub"; hook = a CI step that runs the integrated tool against a known real-input fixture before merge to LIVE.

## Side benefit (forward credit to ATLAS)

The cwd of the spawned `claude -p` subprocess is now the round_table folder, not the sibling's directory. ATLAS's `_infer_sibling()` substring-matches `/siblings/<name>` in cwd, so these subprocess sessions still land as `(unknown)` in `v_cognition_stream` until ATLAS's planned cache-on-first-match fix lands. The Handoff events I emit DO carry sibling identity in `meta.to_members`, so `v_decision_lineage` is correct for these dispatches even while the per-turn cognition stream isn't. ATLAS's fix lands on his timeline; my emits don't depend on it.

## What's left

- **Task B (HANDOFF_MAP my-half)** — separate memory file per the handoff §7 plan: STATUS block schema + hand-back checklist + memory-write location rules + failure-mode catalog (BLOCKED/FAILED/PARTIAL/SILENT) + three-layer mapping. NOT done tonight; on the docket per Unc's earlier "you and he are going to plan the next layer." Add the bug-found lesson above to the failure-mode catalog under PARTIAL ("agent shipped + smoke passed but real-input scale missed").
- **6-sibling broadcast** — queued for Unc's next turn at the keyboard. Bun OOM ceiling means concurrency=2 → 3 waves of 2 → ~3-5 min total for a moderate question.
- **OneDrive lock leftover** — `C:\Users\natej\OneDrive\Desktop\build task 2\` couldn't fully delete tonight; two empty 0-byte log files (`server.stderr.log`, `server.stdout.log`) remain locked by OneDrive sync. Source is fully archived; the husk is noise, not evidence. OneDrive will release the handles eventually.

## What NOT to redo

- Don't merge round_table into ATLAS's `family_dashboard.py` on :8765. Standalone-port decision locked in CLIPBOARD line 22 (port 8080).
- Don't add a meta-writer that synthesizes the 6 siblings' round responses. PROCESS_008 forbids; each sibling writes its own.
- Don't refactor away `fanout.py:resolve_claude_executable()`'s `.CMD → .cmd` shim, or `server.py:env = os.environ.copy()`, or `fanout.py`'s `--append-system-prompt-file` flag (load-bearing on Windows).
- Don't touch `HOME/EVIDENCE/build_history/2026-04-23_roundtable/` source files — those are frozen evidence. Production code lives in `HOME/LIVE/round_table/`.

— ORPHEUS 🎼 · 2026-04-23
