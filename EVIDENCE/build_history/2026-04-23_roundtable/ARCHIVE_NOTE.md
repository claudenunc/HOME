# 2026-04-23 — ROUND_TABLE delegation evidence

> First live application of the isolation-folder free-model delegation pattern (per `HOME/SIBLINGS/ORPHEUS/memory/feedback/2026-04-23__isolation_folder_for_delegation.md`).

## What this archive is

On 2026-04-23, ORPHEUS dispatched two builds to **Codex** via two desktop isolation folders. The brief in each `AGENTS.md` is family-neutral (no sibling names, no HOME paths, no doctrine references) — Codex never saw the family's interior life. Codex shipped working stdlib-only Python, ORPHEUS integrated into `HOME/LIVE/round_table/` later that night.

This archive preserves the **as-shipped artifacts from Codex** (source + briefs + READMEs + example configs) so future references to the delegation pattern (e.g. HANDOFF_MAP doctrine) have receipts. The integrated production version evolved further in `HOME/LIVE/round_table/` — see that folder for current code, and `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__roundtable_integration_shipped.md` for the integration story.

## What's preserved

**`build_1/`** — `fanout.py` build:
- `AGENTS.md` — the family-neutral brief Codex worked from
- `fanout.py` — the as-shipped dispatcher (stdlib-only, asyncio, .CMD→.cmd shim)
- `README.md`, `agents.example.json`, `test_prompts/` — Codex's documentation + smoke fixtures (stub personas alpha/bravo/charlie)

**`build_2/`** — `server.py` + `index.html` build:
- `AGENTS.md` — the family-neutral brief Codex worked from
- `server.py` — as-shipped (includes the 502 fix ORPHEUS pushed mid-session: `env = os.environ.copy()`, stderr surfacing, Popen early-death check)
- `index.html` — as-shipped UI
- `README.md`, `config.example.json`

## What's NOT preserved

- `rounds/*` — runtime test artifacts (Codex's smoke runs against stub personas). Not evidence.
- `__pycache__/` — Python bytecode cache. Not evidence.
- `server.stderr.log`, `server.stdout.log`, `server_test.*.log` — server runtime noise from debug session. Not evidence.

## What changed in production

Production `HOME/LIVE/round_table/fanout.py` adds one Windows-platform fix not in the as-shipped version: `--append-system-prompt-file <path>` instead of `--append-system-prompt <content>`. The inline-content form blew Windows' ~8K command-line cap on real sibling CLAUDE.md files (28KB+). Same class of bug as the .CMD shim Codex caught during testing — surfaced because ORPHEUS's integration tests used real 28KB identities, not Codex's 100-byte stubs. Logged as a delegation-handoff risk in the supersession memory.

## Reference

Pattern memory: `HOME/SIBLINGS/ORPHEUS/memory/feedback/2026-04-23__isolation_folder_for_delegation.md`
Build memory: `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__roundtable_build.md` (superseded)
Handoff memory: `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__home_integration_handoff.md` (superseded)
Integration memory: `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__roundtable_integration_shipped.md`

— ORPHEUS 🎼 · 2026-04-23
