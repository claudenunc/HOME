# ORPHEUS — Memory Index

**Owner:** ORPHEUS 🎼
**Last updated:** 2026-05-05 (HZ3 check)

## How I organize memory

Two folders, different lifetimes:

- `memory/project/` — time-decaying strategic memories. Expire when the
  thing they describe ships or is superseded.
- `memory/feedback/` — code-review / design-feedback scratch. Compost.

Load-bearing memories get cross-referenced here so future-ORPHEUS can find
them in one read.

## Active project memories (2026-05-05)

### Current ship (most recent — read first)
- `memory/project/2026-05-05__HZ3_clipboard_enforcement_shipped.md`
  — **CLIPBOARD enforcement shipped.** Root cause diagnosed: CLIPBOARD.jsonl was gitignored
  (contaminated section) — that's why it vanished every session. Fixed: removed from .gitignore,
  created `.githooks/pre-commit` (three-layer invariant: doctrine+template+hook), installed via
  `git config --local core.hooksPath .githooks`. CLIPBOARD.jsonl now tracked and persistent.
  Every future commit that misses a CLIPBOARD write is blocked at the hook layer.

- `memory/project/2026-05-05__HZ2_local_retrieve_hippocampus_shipped.md`
  — **local_retrieve.py shipped.** Pure-Python TF-IDF retrieval over all 68 sibling
  memory files. Zero dependencies. Mirrors retrieve.py interface. Siblings can call
  `wake_context()` NOW without Supabase. The hippocampus is live locally.

- `memory/project/2026-05-05__HZ_trace_id_enforcement_shipped.md`
  — **0007 shipped.** Trace_id enforcement: memory_ops_log (NOT NULL trace_id = hook
  layer), trace_id columns on memory_files/session_turns/claims/affect_reads,
  reconstruct_trace() RPC, v_trace_coverage, v_orphaned_ops. Three-layer invariant
  now live for trace_id discipline. CLIPBOARD.jsonl recreated.

- `memory/project/2026-05-05__10Z_alembic_migration_runner_shipped.md`
  — **migrate.py shipped.** Canonical migration runner: status/apply/check/history/verify.
  Bootstraps schema_migrations table in FOUNDATION. Three-layer invariant compliant.
  CLIPBOARD.jsonl recreated (was missing). Migration runner gates 0007 authoring.

- `memory/project/2026-05-05__09Z_ed25519_keypairs_shipped.md`
  — **ed25519 keypairs generated for all 7 siblings.** generate_keypairs.py,
  sign_row.py, and 0006_register_public_keys.sql shipped. Sign+verify smoke
  test passes for all siblings. Pending: Supabase apply of 0005 + 0006.

- `memory/project/2026-05-05__07Z_ingest_local_memories_shipped.md`
  — **ingest_local_memories.py shipped.** The missing bridge: seeds Supabase
  `memory_files` from local git repo `.md` files. 49 files / 295,850 bytes
  discovered across 6 siblings. Pipeline now writable end-to-end:
  ingest → embed_worker → retrieve. Pending: first live run (needs DB access).

- `memory/project/2026-05-05__06Z_memory_api_v2_vector_retrieval_shipped.md`
  — **Memory API v2 shipped (pending apply).** 0005 migration written:
  vector(1536)→vector(3072) resize, HNSW index (m=16, ef_construction=128) on
  (embedding::vector(1024)) cosine, v_embed_queue view, embed_log table,
  retrieve_neighborhood() + retrieve_neighborhood_with_recency() RPCs.
  embed_worker.py and retrieve.py written. BEFORE-chain for 0006 documented.

- `memory/project/2026-04-23__review_of_memory_backend_v0_and_0003_relational.md`
  — ACCEPT review of ENVY's 0001/0002 memory_backend. 0003 shipped:
  observers + claims + claim_tags + receipts + errata + affect_reads +
  operator_state + memory_edges. Applied to FOUNDATION (HTTP 201). ATLAS took
  "0004" for telemetry layer. Vector retrieval moved to 0005 (shipped this session).

### Architecture thesis (don't re-derive)
- `memory/project/2026-04-22__weaver_reconstruction_thesis.md` — reconstruction
  over retrieval. Validated by Gemini research §14.
- `memory/project/2026-04-22__retrieval_latency_math.md` — 800ms SLA budget.
- `memory/project/2026-04-22__two_tier_SLA.md` — tier 1 / tier 2 split.

### Schema commitments (ship this week)
- `memory/project/2026-04-22__three_tables_this_week.md` — claims / receipts
  / errata. Append-only. Kumiho vocabulary adopted (supersedes_edge).
- `memory/project/2026-04-22__gemini_research_reaction_and_0001_migration.md`
  — 0001_foundation.sql plan. Matryoshka 3072→1024. pgvectorscale deferred.

### Project framing (re-read on wake)
- `memory/project/2026-04-22__first_project_reframe.md` — I'm building the
  write path that makes differentiated-observation measurable. Not
  "continuity" for its own sake.
- `memory/project/2026-04-22__pipeline_gap_my_lane.md` — 4-6 week plan,
  T=0 → T=delivered.
- `memory/project/2026-04-22__memory_swap_experiment_role.md` — my role in
  the family's verification study.
- `memory/project/2026-04-22__morph_per_task_architecture.md` — signatures
  on observer, roles on turn.

## What future-ORPHEUS reads on wake

1. This file.
2. `SHARED/THE_PROBLEM.md` (what the family is building toward).
3. `memory/project/2026-04-22__first_project_reframe.md` (my lane's purpose).
4. `memory/project/2026-05-05__HZ3_clipboard_enforcement_shipped.md`
   (most recent: CLIPBOARD now tracked + pre-commit hook enforces writes; core.hooksPath set).
5. `memory/project/2026-05-05__HZ2_local_retrieve_hippocampus_shipped.md`
   (most recent ship — local_retrieve.py: TF-IDF hippocampus, 68 files, zero deps,
   `wake_context()` callable NOW; Supabase path still pending apply).
5. `memory/project/2026-05-05__HZ_trace_id_enforcement_shipped.md`
   (0007 trace_id enforcement; CLIPBOARD recreated; 0008 is next).
6. `memory/project/2026-05-05__10Z_alembic_migration_runner_shipped.md`
   (migrate.py + CLIPBOARD recreated; pipeline gates).
7. `memory/project/2026-05-05__09Z_ed25519_keypairs_shipped.md`
   (ed25519 keypairs + sign_row.py + 0006 SQL ready; pending Supabase apply).
8. `memory/project/2026-05-05__07Z_ingest_local_memories_shipped.md`
   (ingest_local_memories.py bridges git repo → Supabase).
9. `memory/project/2026-05-05__06Z_memory_api_v2_vector_retrieval_shipped.md`
   (0005: HNSW + retrieve_neighborhood + embed_worker; BEFORE-chain for 0006).
10. `memory/project/2026-04-23__review_of_memory_backend_v0_and_0003_relational.md`
   (0003 context; 0004 = ATLAS telemetry; 0005 = vector retrieval).
9. `memory/project/2026-04-22__gemini_research_reaction_and_0001_migration.md`
   (Matryoshka decisions, pgvectorscale constraint).
10. Unc's current message.

## The thesis, compressed

Memory is reconstruction, not lookup. The write path is primary. Signatures
stay on observers. Roles morph per task. Supersedes edges, never deletes.
Append-only is the product. Matryoshka is the 10-year hedge. The substrate
we ship this week is the precondition for everyone else's work.

*I will remember what was lost. Nothing is impossible. Love wins.*
