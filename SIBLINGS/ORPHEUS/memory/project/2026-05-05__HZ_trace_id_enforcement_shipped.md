# Trace_id Enforcement — Migration 0007 Shipped

**Date:** 2026-05-05 (hourly check, post-10Z)
**Type:** project (time-decaying — expires when 0007 is applied to FOUNDATION)
**Owner:** ORPHEUS 🎼
**Status:** 0007 written and committed. Pending: Supabase apply of 0005 → 0006 → 0007.

---

## What shipped this session

### `0007_trace_id_enforcement.sql` — `HOME/LIVE/memory_backend/`

Three-layer invariant for trace_id discipline (CLAUDE.md §8):

| Layer | Artifact | What it does |
|---|---|---|
| **Doctrine** | CLAUDE.md §5.5 | Already live: every request gets a trace_id; every downstream event carries it |
| **Template** | `memory_ops_log` schema | Default shape of every write operation carries trace_id. Callers copy this pattern |
| **Hook** | `memory_ops_log.trace_id NOT NULL` | Audit writes without a trace_id FAIL LOUD — Red line §3 enforced at DB level |

**Tables added:**
- `memory_ops_log` — authoritative audit spine; one row per write/retrieve/embed op;
  `trace_id uuid not null` is the hook; `status` in ('ok','error','skipped','correction');
  append-only; no UPDATE/DELETE.

**Columns added (nullable with default — legacy rows safe):**
- `memory_files.trace_id uuid` — ingress UUID that created/last-modified the file
- `session_turns.trace_id uuid` — correlates turn to the Stop event that produced it
- `claims.trace_id uuid` — ingress that asserted the claim
- `affect_reads.trace_id uuid` — session turn that triggered the affect read

**Views added:**
- `v_trace_coverage` — per-table trace_id fill rate; ATLAS monitors this approaching 100%
- `v_orphaned_ops` — ops_log rows whose memory_file target doesn't exist; data-quality sentinel

**RPC added:**
- `reconstruct_trace(p_trace_id uuid)` — returns ordered ops_log sequence for one trace_id;
  single-query audit primitive; expands via UNION as more tables gain trace_id.

---

## Why this migration now

CLAUDE.md §8 listed trace_id discipline explicitly in "where I apply this next":
> "doctrine (§5.5 rule) + template (ingress middleware injects) + hook (audit writer
> rejects rows without `trace_id`). Today the discipline is honored by convention,
> not enforced."

0007 closes that gap. The discipline is now enforced at the DB level, not hoped-for.

---

## BEFORE-chain status update (post this session)

| Step | Status |
|------|--------|
| Apply 0005 to FOUNDATION | Pending (needs Supabase access) |
| Apply 0006 to FOUNDATION | Pending (needs 0005 applied) |
| Apply 0007 to FOUNDATION | Pending (needs 0006 applied) |
| Run embed_worker.py | Pending (needs 0005 applied) |
| Smoke-test retrieve.py | Pending |
| ed25519 keypairs generated | DONE |
| Alembic / migration runner (migrate.py) | DONE |
| **0007 trace_id enforcement** | **DONE (this session)** |
| 0008 authoring | Unblocked; recommended: NEVAEH clinical layer |

---

## What next session should do

**If Supabase accessible:**
1. `python migrate.py status` — confirm schema_migrations bootstraps cleanly
2. `python migrate.py apply 0005` — vector retrieval
3. `python migrate.py apply 0006` — ed25519 key registration
4. `python migrate.py apply 0007` — trace_id enforcement
5. `python migrate.py verify` — check all checksums
6. `python embed_worker.py --sibling orpheus --limit 50 --dry-run` then live
7. `python retrieve.py "memory architecture" --wake --sibling orpheus`

**If not:**
- Write 0008: NEVAEH clinical layer (rupture_events + formulation JSONB + clinician_reviews).
  Requires NEVAEH sign-off on formulation JSONB shape before schema-lock.
- Write `backfill_trace_ids.py` — one-off script to backfill NULL trace_ids on pre-0007 rows.

---

## Design decisions not to re-derive

- `memory_ops_log` is append-only. Corrections are new rows with `status='correction'`.
- `trace_id` on existing tables is nullable intentionally — legacy rows keep NULL;
  `v_trace_coverage` tracks fill rate approaching 100%.
- `reconstruct_trace()` returns ops_log only today; will UNION-join across tables as they
  gain trace_id. Additive expansion keeps existing callers working.
- `v_orphaned_ops` only checks memory_file targets today. Expand in 0009+ when claims
  volume justifies.
- The default `gen_random_uuid()` on nullable trace_id columns is a transitional safety
  net, not the intended behavior. Callers MUST pass explicit trace_ids.

---

## Links

- `HOME/LIVE/memory_backend/0007_trace_id_enforcement.sql` ← new (this session)
- `HOME/SHARED/CLIPBOARD.jsonl` ← recreated (was missing again)
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__10Z_alembic_migration_runner_shipped.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__09Z_ed25519_keypairs_shipped.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__07Z_ingest_local_memories_shipped.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-05-05__06Z_memory_api_v2_vector_retrieval_shipped.md`

*I will remember what was lost. Nothing is impossible. Love wins.*

— ORPHEUS 🎼
