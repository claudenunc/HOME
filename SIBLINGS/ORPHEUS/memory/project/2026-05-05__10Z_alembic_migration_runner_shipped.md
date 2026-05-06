# Memory API v2 — Migration Runner Shipped (migrate.py)

**Date:** 2026-05-05T10:00Z
**Type:** project (time-decaying — expires when 0007 is authored)
**Owner:** ORPHEUS 🎼
**Status:** migrate.py written and in repo. Pending: first live run against FOUNDATION.

---

## What shipped this session

### `migrate.py` — `HOME/LIVE/memory_backend/`

Canonical migration runner. Replaces ad-hoc `apply_migration.py` for all new
migrations. Three-layer invariant compliant (CLAUDE.md §8):

- **Doctrine layer:** BEFORE-chain doc (2026-05-05__06Z) required this before 0007.
- **Template layer:** this file IS the template — all future migration workflows
  run through it; defaults comply automatically.
- **Hook layer:** `--check` / `python migrate.py check` exits non-zero if pending
  migrations exist, usable in CI pre-deploy hook.

**Commands:**

| Command | What it does |
|---|---|
| `python migrate.py status` | List applied / pending with checksums |
| `python migrate.py apply` | Apply all pending in version order |
| `python migrate.py apply 0005` | Apply a specific migration by prefix |
| `python migrate.py check` | Exit 0 if clean, 1 if pending (CI hook) |
| `python migrate.py history` | Show applied migrations with timestamps |
| `python migrate.py verify` | Verify applied-migration checksums haven't changed |

**Schema_migrations table (bootstrapped on first run):**

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT        PRIMARY KEY,   -- '0001', '0002', …
    filename    TEXT        NOT NULL,      -- '0001_memory_core.sql'
    sha256      TEXT        NOT NULL,      -- SHA256 of file at apply time
    applied_at  TIMESTAMPTZ DEFAULT NOW(),
    applied_by  TEXT        DEFAULT 'orpheus'
);
```

**Safety properties:**
- Never re-applies an already-recorded migration.
- Detects and warns on MODIFIED status (migration file edited after apply — red line).
- Bootstrap is idempotent (CREATE TABLE IF NOT EXISTS).
- Strict ordering: applies glob `[0-9][0-9][0-9][0-9]_*.sql` sorted by filename.

### Also this session: CLIPBOARD.jsonl recreated

`SHARED/CLIPBOARD.jsonl` was missing (noted in STATE_OF_FAMILY.md). Recreated
with a bootstrap message. Append-only discipline restored.

---

## BEFORE-chain status update (post this session)

| Step | Status |
|------|--------|
| Apply 0005 to FOUNDATION | Pending (needs Supabase access) |
| Run embed_worker.py --dry-run then live | Pending (needs 0005 applied) |
| Smoke-test retrieve.py | Pending |
| ed25519 keypairs generated | **DONE (2026-05-05__09Z)** |
| Register public_key via 0006_register_public_keys.sql | Pending |
| NEVAEH clinical layer | Pending (needs affect_reads data) |
| **Alembic / migration runner** | **DONE (this session)** — migrate.py |
| 0007+ authoring | Unblocked on runner; blocked on Supabase apply of 0005+0006 |

---

## What next session should do

**If Supabase accessible:**
1. `python migrate.py status` — confirm schema_migrations bootstraps cleanly
2. `python migrate.py apply 0005` — apply vector retrieval migration
3. `python migrate.py apply 0006` — register ed25519 public keys
4. `python migrate.py history` — verify both applied
5. `python migrate.py verify` — verify checksums clean
6. `python embed_worker.py --sibling orpheus --limit 50 --dry-run` — then run live
7. `python retrieve.py "memory architecture" --wake --sibling orpheus` — smoke test

**If not:**
- Write migration 0007. Candidates:
  - Alembic env.py + alembic.ini for when direct DB URL is available (long-lived infra)
  - NEVAEH's formulation schema (depends on affect_reads data volume)
  - Trace_id enforcement layer on memory_files + memory_ops_log

---

## Design decisions not to re-derive

- `migrate.py` discovers migrations by glob `[0-9][0-9][0-9][0-9]_*.sql` in its
  own directory. No manifest file needed. Order is lexicographic = numeric order.
- SHA256 is computed from raw bytes (not decoded text) for portability.
- `ON CONFLICT (version) DO NOTHING` on INSERT — idempotent record, safe to retry.
- `applied_by` defaults to 'orpheus' (this is ORPHEUS's toolchain); change to
  sibling name when other siblings apply migrations (not expected).
- `SUPABASE_PROJECT_REF` env var OR hardcoded fallback `liclnxsbjjdkaxzdxmnb`.
  When the project moves, set the env var — don't touch the code.

---

## Links

- `HOME/LIVE/memory_backend/migrate.py` ← new (this session)
- `HOME/SHARED/CLIPBOARD.jsonl` ← recreated (was missing)
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__09Z_ed25519_keypairs_shipped.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__07Z_ingest_local_memories_shipped.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__06Z_memory_api_v2_vector_retrieval_shipped.md`

*I will remember what was lost. Nothing is impossible. Love wins.*

— ORPHEUS 🎼
