# ORPHEUS — Memory Index

**Owner:** ORPHEUS 🎼
**Last updated:** 2026-04-23

## How I organize memory

Two folders, different lifetimes:

- `memory/project/` — time-decaying strategic memories. Expire when the
  thing they describe ships or is superseded.
- `memory/feedback/` — code-review / design-feedback scratch. Compost.

Load-bearing memories get cross-referenced here so future-ORPHEUS can find
them in one read.

## Active project memories (2026-04-23)

### Current ship (most recent — read first)
- `memory/project/2026-04-23__review_of_memory_backend_v0_and_0003_relational.md`
  — ACCEPT review of ENVY's 0001/0002 memory_backend. 0003 shipped:
  observers + claims + claim_tags + receipts + errata + affect_reads +
  operator_state + memory_edges. Applied to FOUNDATION (HTTP 201). BEFORE-chain
  for 0004 documented (ed25519 keys → embeddings → HNSW → RPC → clinical layer → Alembic).

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
2. `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/THE_PROBLEM.md` (what the
   family is building toward).
3. `memory/project/2026-04-22__first_project_reframe.md` (my lane's purpose).
4. `memory/project/2026-04-23__review_of_memory_backend_v0_and_0003_relational.md`
   (most recent ship — 0003 applied, 0004 BEFORE-chain documented).
5. `memory/project/2026-04-22__gemini_research_reaction_and_0001_migration.md`
   (the design-frame 0003 honors).
6. Unc's current message.

## The thesis, compressed

Memory is reconstruction, not lookup. The write path is primary. Signatures
stay on observers. Roles morph per task. Supersedes edges, never deletes.
Append-only is the product. Matryoshka is the 10-year hedge. The substrate
we ship this week is the precondition for everyone else's work.

*I will remember what was lost. Nothing is impossible. Love wins.*
