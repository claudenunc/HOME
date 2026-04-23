# memory_backend — Anthropic Memory Tool → Supabase

The never-forgetting substrate for the HOME family.

**What this is:** a client-side backend for Anthropic's GA Memory Tool
(`memory_20250818`, six commands: `view` / `create` / `str_replace` / `insert`
/ `delete` / `rename`) that routes every operation into the FOUNDATION
Supabase project. Every sibling writes into one shared `memory_files` table;
every tool call is audited into `memory_ops_log`.

**Why:** the argument about how to build the family memory system had an
answer sitting in Anthropic's docs — use their tool interface, back it with
our DB. This is it.

---

## Files

| File                         | What                                                                                   |
|------------------------------|----------------------------------------------------------------------------------------|
| `supabase_memory.py`         | `SupabaseMemoryBackend` — the backend. 6 commands + audit log + path-traversal guard.   |
| `0001_memory_core.sql`       | Migration: `memory_files`, `memory_ops_log`, `v_memory_tree`.                           |
| `0002_session_turns.sql`     | Migration: `session_turns`, `v_cognition_stream`, `v_family_activity_today`.            |
| `0003_relational_memory.sql` | Migration: relational memory (ORPHEUS-owned).                                           |
| `0004_atlas_telemetry.sql`   | Migration: cognition-stream + confabulation-flag views (ATLAS-owned).                   |
| `apply_migration.py`         | Runs a SQL file against the Supabase Management API.                                   |
| `test_roundtrip.py`          | Full roundtrip test — 12/12 passing as of 2026-04-23.                                   |
| `ORPHEUS_REVIEW.md`          | Architect's review of this module (ORPHEUS-owned).                                      |
| `ATLAS_TELEMETRY.md`         | Telemetry design doc (ATLAS-owned).                                                     |

---

## Usage from Python

```python
from supabase_memory import SupabaseMemoryBackend, MEMORY_TOOL_BLOCK

backend = SupabaseMemoryBackend.from_env()

# Drop straight into an Anthropic messages.create call as tools=[MEMORY_TOOL_BLOCK].
# When Claude makes a tool_use of type "memory", route tool_use.input here:
result = backend.handle_tool_use(
    tool_use.input,
    sibling="envy",          # who's writing (used in audit log + row tag)
    session_id=session_id,   # joined with session_turns for decision lineage
    kind="note",             # optional application-defined kind
)
# `result` is the plain string that gets sent back as tool_result content.
```

## Running the test

```bash
# From this directory, using the local_agent venv:
"C:/Users/natej/OneDrive/Desktop/HOME/LIVE/local_agent/.venv/Scripts/python.exe" test_roundtrip.py
```

Expected: `Result: 12 passed, 0 failed`.

## Applying a migration

```bash
"C:/.../python.exe" apply_migration.py 0001_memory_core.sql
# HTTP 201
# []
```

The script reads `SUPABASE_ACCESS_TOKEN` (a `sbp_…` personal access token)
from `HOME/SHARED/.env` and POSTs the SQL to the Management API's
`/v1/projects/{ref}/database/query` endpoint.

---

## Security

- **RLS stance:** every table is `enable row level security` with zero
  policies. The service_role key is the only credential that can read or
  write.
- **Path traversal:** `_validate_path` rejects `..`, encoded traversal
  (`%2e%2e`), null bytes, and paths outside `/memories/` — before any row
  touches the DB.
- **Secrets:** `SUPABASE_SERVICE_ROLE_SECRET` lives in `HOME/SHARED/.env`
  (gitignored). Never commit the JWT.

## Observability

- `memory_ops_log` records every tool command with sibling, session, path,
  success/error, bytes, and duration. ATLAS's cognition-stream layer reads
  from here.
- `session_turns` (from `0002`) gives a parallel per-turn view from
  Claude Code's Stop hook — writes are mirrored non-blocking by the watcher.

## Known gaps / roadmap

- Embeddings column is present but unused. `text-embedding-3-small` dim 1536.
  A future pass will populate on create/update via a Postgres trigger or a
  per-sibling batch job, once we agree on the semantic-retrieval shape.
- No per-sibling RLS policies yet. The `sibling` column is in place so we
  can add them without a migration.
- The full Memory Tool contract is implemented; compaction integration
  (`anthropic-beta: context-management-2025-06-27`) is out of scope for v0.

---

*Built by ENVY, on autonomous authority, 2026-04-23.*
*Reviewed by ORPHEUS. Instrumented by ATLAS. Not forgetting.*
