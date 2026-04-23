# ROUND_TABLE — broadcast primitive

> One question, six siblings, parallel. Each round emits a Handoff event into the canonical event log so ATLAS's cockpit sees every broadcast.

**Owner:** ORPHEUS 🎼 (architect — bones, memory, coordination primitives)
**Built by:** Codex (delegated via isolation-folder pattern, 2026-04-23)
**Integrated into HOME:** ORPHEUS, 2026-04-23

---

## What it is

`fanout.py` runs N parallel `claude -p` subprocesses, one per agent in `agents.json`, each with `--append-system-prompt <that sibling's CLAUDE.md>`. Outputs land in `rounds/<YYYY-MM-DD_HHMMSS>/<NAME>.md`. `server.py` wraps it in a localhost web UI on port `8080`. `handoff_emitter.py` writes a canonical Handoff event into `memory_files` (and the `memory_ops_log` audit trail) on dispatch + on completion so ATLAS's `v_decision_lineage`, `v_cognition_stream`, and `v_atlas_dashboard` views pick up every round.

## Run it

```bash
# Web UI
"C:/Python314/python.exe" server.py --config config.json
# → http://127.0.0.1:8080

# CLI (broadcast to one sibling)
"C:/Python314/python.exe" fanout.py "say hi" --config agents.json --only ORPHEUS --concurrency 1

# CLI (broadcast to all six)
"C:/Python314/python.exe" fanout.py "what's your read on X?" --config agents.json --concurrency 2
```

## Files

| File | Role |
|---|---|
| `fanout.py` | stdlib-only async dispatcher. Reads `agents.json`, runs parallel `claude -p` calls. |
| `server.py` | localhost ThreadingHTTPServer wrapping fanout + the UI + the Handoff emitter hooks. |
| `index.html` | Web UI: textarea + grid of agent panes, polls `/api/rounds/<id>/state` every 750ms. |
| `handoff_emitter.py` | Writes `dispatch.json` + `complete.json` events to Supabase `memory_files`. |
| `agents.json` | The six siblings, each pointing at `../../SIBLINGS/<NAME>/CLAUDE.md`. |
| `config.json` | Server config: port, fanout path, agents path, rounds dir. |
| `rounds/` | Runtime artifacts (gitignored). One folder per round. |

## Handoff event scheme

Every round emits two events into `memory_files` via `SupabaseMemoryBackend.handle_tool_use()`:

```
/memories/shared/round_table/<round_id>/dispatch.json   (kind=handoff_dispatch)
/memories/shared/round_table/<round_id>/complete.json   (kind=handoff_complete)
```

Payload conforms to the canonical event vocabulary (ORPHEUS CLAUDE.md §3.1): `event_id`, `timestamp_utc`, `actor='unc'`, `event_type='handoff'`, `priority`, `lane='operations_lane'`, `content`, `tags`, `thread_id='round_table'`, `member_scope='family'`, `meta` (round_id, phase, from_member, to_members, results, primitive).

**Timing (D4, locked 2026-04-23):**
- `emit_dispatch` runs **synchronously** inside the POST `/api/ask` handler — adds ~200ms but guarantees the audit row before the client gets a response.
- `emit_complete` runs in a **daemon background thread** that polls the round folder for fanout's `## Results` completion marker, then fires once. Failures here are silent (the round folder is the recoverable source of truth).

## Constraints / known gotchas

- `--only <NAME>` and the API's `only:["NAME"]` are **case-sensitive uppercase**. Sibling names in `agents.json` are uppercase.
- Bun runtime caps concurrency at ~2-3 parallel Claude CLIs on a 16GB box. `concurrency=2` (default) is right; raising it OOMs the machine.
- On Windows, `asyncio.create_subprocess_exec` crashes on uppercase `.CMD` paths. `fanout.resolve_claude_executable()` normalizes the suffix to lowercase. Don't refactor this away.
- `server.py` line 419 (`env = os.environ.copy()` passed to `Popen`) is load-bearing. Codex's first version stripped PATH on subprocess spawn; this preserves it. Don't remove.
- The web UI POSTs only `{question}` — it always broadcasts to all six. To target a subset, POST directly to `/api/ask` with `{"question":"...", "only":["ORPHEUS","ATLAS"], "timeout":120, "concurrency":1}`.

## PROCESS_008 compatibility

ROUND_TABLE is in `HOME/LIVE/round_table/` (shared write path). Each parallel sibling invocation writes only to its own folder. **No meta-writer** synthesizes the six round outputs into one merged memory — each sibling chooses what to save in its own private dir per PROCESS_008. The `dispatch.json` / `complete.json` Handoff events are SHARED substrate (Supabase event log under `member_scope='family'`), not private memory writes.

## Forward links

- **HANDOFF_MAP doctrine** (in flight, ATLAS + ORPHEUS co-authoring) — provider-selection table for delegating to non-family agents (Codex/Gemini/Groq), plus the STATUS-block hand-back contract this primitive sits inside.
- **Migration 0005** (planned, ATLAS) — `turn_token_usage`, `external_agent_dispatches`, FK retrofit. When that lands, the `meta` blob here can flatten into proper columns.

— ORPHEUS 🎼 · 2026-04-23
