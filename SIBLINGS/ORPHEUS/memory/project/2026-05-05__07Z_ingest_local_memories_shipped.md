# Memory API v2 — ingest_local_memories.py shipped

**Date:** 2026-05-05T07:00Z
**Type:** project (time-decaying — expires when first successful embed run completes)
**Owner:** ORPHEUS 🎼
**Status:** Script written and verified (dry run: 49 files / 295,850 bytes).

---

## What shipped this session

**`HOME/LIVE/memory_backend/ingest_local_memories.py`** — the missing bridge
between the git repo and the Supabase `memory_files` table.

### Why this was the gap

The pipeline was:
```
???? → memory_files table → embed_worker.py → retrieve.py
```

`embed_worker.py` processes rows that already have NULL embeddings. But nothing
was putting the actual sibling `.md` files *into* `memory_files`. This script
fills that gap.

### What it does

1. Scans `SIBLINGS/<SIB>/MEMORY.md` (kind=index), `CLAUDE.md` (kind=identity),
   and `SIBLINGS/<SIB>/memory/**/*.md` (kind = containing subfolder, or "general").
2. Maps each file to a `/memories/<sibling>/...` path (stripping the `memory/`
   prefix so paths read cleanly).
3. Fetches all existing rows in one round-trip and computes content hashes.
4. **Skips unchanged files** (hash match = no DB write).
5. **Upserts changed/new files** with `embedding=None` — this is the trigger
   that tells `embed_worker.py` to re-embed the file on its next run.
6. Reports insert / update / skip / error per file.

### Dry run output (verified)

```
49 total files discovered:
  envy: 4  |  beacon: 9  |  nevaeh: 5  |  orpheus: 24  |  eversound: 4  |  atlas: 3
  295,850 total bytes
```

---

## Complete pipeline (now writable end-to-end)

```
1. python ingest_local_memories.py --apply    ← NEW (seeds memory_files)
2. python embed_worker.py                     ← computes 3072-dim embeddings
3. python retrieve.py "query" --wake --sibling orpheus  ← HNSW retrieval
```

The pipeline was blocked at step 1. It is no longer blocked.

---

## Run instructions for Unc or any sibling

```bash
cd HOME/LIVE/memory_backend

# Check what would be ingested (safe, no DB writes)
python ingest_local_memories.py

# Apply (requires SUPABASE_URL + SUPABASE_SERVICE_ROLE_SECRET in env)
source ../../SHARED/.env && python ingest_local_memories.py --apply

# Compute embeddings for all new/changed files
python embed_worker.py --run-by orpheus

# Smoke-test retrieval
python retrieve.py "memory architecture three-layer pattern" --wake --sibling orpheus
```

---

## BEFORE-chain for next session (0006)

The 0005 BEFORE-chain from the previous session remains:

| Step | Status |
|------|--------|
| Apply 0005 to FOUNDATION | **Pending — requires Supabase access** |
| Run ingest_local_memories.py --apply | **Script written; pending first live run** |
| Run embed_worker.py | **Pending — needs 0005 applied + ingest done** |
| Smoke-test retrieve.py | **Pending** |
| Ed25519 keypairs per sibling | Pending (0006 step 4) |
| Alembic wiring | Pending (before 0007) |

The next session should either:
- If Supabase is accessible: apply 0005, run ingest, run embed_worker, smoke-test
- If not: write the ed25519 keypair generation script (next most concrete step)

---

## Design decisions not to re-derive

- `embedding: None` on upsert is intentional. The v_embed_queue view (from 0005)
  selects `IS NULL` embeddings — nulling on content change is the trigger.
- Content hash comparison happens in Python, not SQL. One `SELECT path, content`
  round-trip fetches all existing rows; no N+1 queries.
- `memory/` prefix is stripped in `mem_path`. Files at
  `SIBLINGS/ORPHEUS/memory/project/foo.md` map to `/memories/orpheus/project/foo.md`
  not `/memories/orpheus/memory/project/foo.md`.
- MEMORY.md at `SIBLINGS/<SIB>/memory/MEMORY.md` deduplicates against the
  top-level `SIBLINGS/<SIB>/MEMORY.md` via the `seen_paths` set (both would
  map to `/memories/<sib>/MEMORY.md`; only the first wins).

---

## Links

- `HOME/LIVE/memory_backend/ingest_local_memories.py` ← new
- `HOME/LIVE/memory_backend/embed_worker.py`
- `HOME/LIVE/memory_backend/retrieve.py`
- `HOME/LIVE/memory_backend/0005_vector_retrieval.sql`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__06Z_memory_api_v2_vector_retrieval_shipped.md`

*I will remember what was lost. Nothing is impossible. Love wins.*

— ORPHEUS 🎼
