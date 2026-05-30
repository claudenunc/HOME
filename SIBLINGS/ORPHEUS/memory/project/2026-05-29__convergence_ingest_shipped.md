# Convergence ingest shipped — "update both, no matter the door"

**Date:** 2026-05-29
**Status:** CURRENT — built, tested, applied to live THE FOUNDATION (2 rows), idempotent.
**Dispatch:** ENVY (Claude Code lane), authorized by Nathan.

## What I built

`HOME/LIVE/memory_backend/ingest_sessions.py` — the deferred ingest that completes
the three-store convergence. The Stop hook (`LIVE/memory_watcher/watch.py`) records
each Claude-lane session end into `SIBLINGS/<X>/memory/session_index.jsonl` with
`ingested_to_supabase:false` and does NO DB work (a hook must never hang). This
script reads those hints and converges them into:

1. **Supabase THE FOUNDATION** — structured rows into existing `session_turns` table.
2. **Obsidian vault** — human-readable wake notes into `AGENTS/<SIBLING>/SESSION_NOTES.md`.
   (This is the gap Nathan flagged: direct-to-sibling sessions were NOT hitting Obsidian. Closed.)
3. **In-repo flag flip** — `ingested_to_supabase:true` on processed `session_index.jsonl` entries.

`test_ingest_sessions.py` — 4 offline unit tests (extraction, classification, key
stability, row shape). All pass, no DB/network.

## Key architectural decisions

- **Target table = `session_turns`** (migration 0002), NOT a new event table. The old
  watch.py wrote one row per *turn* (534 historical rows, last 2026-04-28). The new
  hook writes one index entry per *session-end*. My ingest writes one `session_turns`
  row per session-end event. No overlap, no migration needed.
- **Idempotency without a schema migration.** `session_turns` has no natural unique key
  (append-only bigserial). I made my own anchor: `ingest_key = sha256(session_id|ts|event)`,
  stamped inside the FIRST element of the existing `tool_calls` jsonb under an `_ingest`
  envelope. Before insert I query rows carrying that envelope and skip matches.
  Two-gate design: the `ingested_to_supabase` flag is the fast first gate; the in-DB key
  check is the durable backstop — a crash between DB-write and flag-write never double-writes.
  Verified: `--apply --all` (bypasses flag gate, forces DB check) inserted 0, skipped 2.
- **Deterministic extraction, zero LLM calls.** Ported the regex classification shape from
  the Hermes lane `living_memory_watcher.py` (projects/emotions/entities/memory-level) so
  BOTH lanes tag memory identically. Transcript parsing pulls files_written/edited (Write vs
  Edit/MultiEdit/NotebookEdit), bash_commands (Bash/PowerShell), tool_count, tool_calls,
  errors (is_error tool_results), text_excerpt — matching session_turns columns exactly.
- **Path resolution from `__file__`**, never hardcoded user paths (red line #1). `.env`
  auto-loaded from `HOME/SHARED/.env` via python-dotenv with a tiny fallback parser.
- **Gated.** No schema migration applied. Writes only to the existing table. Default is dry
  run; `--apply` to converge. `--no-obsidian` for DB-only. Never touches the git remote.

## Test result (live)

- Dry run: parsed ENVY session 8640adbe (110 tools, 13 written, 4 edited), classified
  `relationship_correction` / `CRITICAL_RELATIONSHIP` / importance 9 — correct (the session
  was about memory continuity + correcting how siblings read Nathan).
- `--apply`: inserted turn_id 535, 536; wrote `AGENTS/ENVY/SESSION_NOTES.md`; flipped 2 flags.
- Re-run `--apply --all`: inserted 0, skipped 2. Idempotency confirmed.

## Hermes-lane convergence — DESIGN (needs Nathan GO before re-homing)

The Hermes watcher (`AppData/Local/hermes/scripts/living_memory_watcher.py`) currently
writes only to a local SQLite + wake_packet.md — NOT THE FOUNDATION or Obsidian. To
converge it WITHOUT touching its hot path or requiring a restart of its 1-min cron
(job `83959ce76151`), the safe design is a **sidecar reader**, not an in-place rewrite:

- New `ingest_hermes_sessions.py` in `LIVE/memory_backend/` reads `living_memory.sqlite3`
  (`extracted_notes` + `raw_turns`) read-only, maps each note to the same `session_turns`
  row shape with `lane:"hermes"`, reuses the SAME `_ingest` ingest_key dedup, and writes the
  same Obsidian `AGENTS/<X>/SESSION_NOTES.md`. The Hermes watcher keeps running untouched.
- This mirrors the Claude-lane design exactly, so one ingest contract serves both doors.
- GO needed only if Nathan wants the Hermes cron itself re-pointed (restart). The sidecar
  needs no restart — flag it as the lower-risk path.

## Open items for Nathan / ENVY

- Minor: two Stop checkpoints of the same session produce two near-duplicate Obsidian
  sections (each Stop is a real checkpoint, so this is correct-but-noisy). Could collapse to
  latest-per-session in Obsidian later if it bothers anyone — left as-is (append-only honesty).
- Wiring this on a cron (every N min, `--apply`) is the obvious next step but is a setup/
  spend-adjacent change → needs Nathan GO. Until then it runs on demand.

## Files
- `HOME/LIVE/memory_backend/ingest_sessions.py` (new)
- `HOME/LIVE/memory_backend/test_ingest_sessions.py` (new)
