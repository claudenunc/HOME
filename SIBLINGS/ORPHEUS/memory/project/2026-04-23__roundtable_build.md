---
name: ROUND_TABLE broadcast primitive — Option 1 shipped, Option 2 in-flight
description: One-question-to-all-six-siblings tool built via delegated Codex; Option 1 (fanout.py) live, Option 2 (web UI) smoke-testing
type: project
date: 2026-04-23
---

## What happened

Unc asked for a way to broadcast one question to all 6 siblings instead of running 6 separate terminal tabs. I designed two options, delegated the build to Codex via two isolated desktop folders (`build task 1\` and `build task 2\`) with family-neutral task briefs.

**Option 1 — `fanout.py` (SHIPPED).**
`C:\Users\natej\OneDrive\Desktop\build task 1\fanout.py`. stdlib-only Python 3.11+. Parallel `claude -p` subprocesses, one per agent in `agents.json`, each with `--append-system-prompt <that agent's CLAUDE.md>`. Writes `rounds/<YYYY-MM-DD_HHMMSS>/<name>.md` + `_question.md`. `asyncio.Semaphore`-capped concurrency (default 2 — machine OOMs above ~3 concurrent Claude CLIs). Handles Windows `.CMD` → `.cmd` case bug via `candidate.with_suffix(candidate.suffix.lower())`.

**Option 2 — `server.py` + `index.html` (IN FLIGHT).**
Localhost `ThreadingHTTPServer` wrapping fanout.py. 750ms polling UI. Hit port-8765 collision with ATLAS's cockpit during smoke test; moved to 8766. Live test from the UI right now is throwing 502 "fanout did not create a round folder in time" — suspected PATH-inheritance issue in the server-spawned subprocess, not yet root-caused.

## Key Windows findings from the debug journey

File these — they'll bite anyone wiring asyncio + claude CLI on Windows.

1. `asyncio.create_subprocess_exec` crashes with `RC 3221226505` (STATUS_STACK_BUFFER_OVERRUN) when target ends in uppercase `.CMD`. Same file as `.cmd` works. `shutil.which("claude")` returns the uppercase form on npm-global installs. Fix = normalize suffix to lowercase before exec.
2. `claude.exe` direct invocation crashes with `RC 2147483651` (STATUS_BREAKPOINT) when argv contains escaped embedded double quotes. The `.cmd` shim normalizes quoting. Use `.cmd`.
3. Single successful calls emit `Out of memory` on stderr. Bun runtime is memory-pressured. Six concurrent = machine OOMs. Ceiling ~2-3 concurrent on 16GB boxes.

## Integration plan (open, pending ATLAS)

- `fanout.py` → `HOME/SIBLINGS/ROUND_TABLE/fanout.py`
- Real `agents.json` pointing at all six sibling `CLAUDE.md` files
- Each round emits a `Handoff` event into the Supabase event log per canonical schema (§3.1): `from_member='unc'`, `to_member='<sibling>'`, `thread_id=round_id`, `summary = question`. **Handoff events are SHARED substrate (Supabase), not private memory.** Compatible with PROCESS_008.
- Option 2 server: merge into ATLAS's cockpit at `:8765` OR run standalone on `:8080`. Waiting on ATLAS.
- **No meta-writer / no synthesis memory.** PROCESS_008 constraint. Each sibling writes its own memory about the round in its own folder if it chooses. Confirmed with ENVY.

## Why it matters

This is the substrate for (a) the never-sleep persistence constraint (Unc wants always-on family accessible from anywhere), (b) the Hostinger VPS phone-access path (phone → Tailscale → VPS → ROUND_TABLE), and (c) the free-models-first delegation pattern being proven as real doctrine (see `feedback/2026-04-23__isolation_folder_for_delegation.md`).

## Supersession triggers

- Option 2 502 bug root-caused and fixed → update this memory with the fix.
- Integration decision made (merge vs standalone) → record it here.
- Real family `agents.json` wired and first live round against all 6 siblings succeeds → add the timestamp + round_id.
