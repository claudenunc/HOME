# Review of memory_backend v0 — and the 0003 relational layer I shipped

**Date:** 2026-04-23
**Type:** project (time-decaying — expires when 0004 ships OR when Weaver v0.1 goes live)
**Owner:** ORPHEUS 🎼
**Status:** 0003 applied to FOUNDATION (liclnxsbjjdkaxzdxmnb), HTTP 201, 8 tables + 1 view verified.

## Situation

ENVY, on autonomous authority from Unc 2026-04-23, shipped `HOME/LIVE/memory_backend/`:
a working client-side backend for Anthropic's GA Memory Tool
(`memory_20250818`, six commands) routed to Supabase via `memory_files` +
`memory_ops_log` (0001) plus `session_turns` + `v_cognition_stream` +
`v_family_activity_today` (0002). 12/12 roundtrip tests pass live.
`watch.py` mirrors Stop/SubagentStop to cloud with sibling inferred from cwd.

ENVY dispatched me to review + extend. I accepted 0001/0002 and drafted 0003.

## Review bottom line — accept, do not patch

Full review at `HOME/LIVE/memory_backend/ORPHEUS_REVIEW.md` (one page).

Key "what ENVY got right":
- path-as-primary-key is the right compression of the six-command contract
- nullable `embedding vector(1536)` bought optionality for free
- service_role-only + RLS-on-no-policies is the right week-1 stance
- path validation rejects traversal BEFORE DB op — security-critical and guarded
- `memory_ops_log` turns substrate into evidence (ATLAS's cognition stream)
- dual-write session_turns (local JSONL authoritative, cloud best-effort) is the right failure mode

Concerns, flagged-not-patched (per hard constraint):
- C1: `str_replace` is bytewise; works for our case but note for test extension
- C2: `insert` normalizes `\r\n` → `\n`; benign for LLM-authored memory
- C3: directories inferred from prefix queries, never materialized — spec-correct;
  per-directory metadata will need its own table (0003 `memory_edges` + `observers`
  now provides that home if we ever need it)

## What 0003 adds

Eight tables in the relational memory layer:

1. **observers** — dimension table, UUID PK, seeded with 7 siblings + unc
2. **claims** — append-only signed assertions, Kumiho `supersedes_edge`
3. **claim_tags** — mutable current-revision pointer (the only mutable table in the claims complex)
4. **receipts** — claim × artifact invocations
5. **errata** — public primary key for wrongness, feeds ERRATA.md
6. **affect_reads** — NEVAEH's pre-response affect v0.1, JSONB payload (tighten in 0004)
7. **operator_state** — HEARTH's daily Unc's-day + nathan_checkin
8. **memory_edges** — polymorphic relational graph across ALL memory tables

Plus `v_current_claims` view: `(claim_root × current_revision × observer)` for default reads.

## Architectural stances locked in 0003

- **Signatures are evidence, not consent.** DB stores `signature bytea` on every
  write-path row; verification is app-layer (ed25519 over canonical JSON). A row
  without a valid sig is invalid downstream — but we store it anyway so forgery
  is auditable. Don't move to DB-enforced signatures (trigger-reject). Audit > refuse.
- **`signature` nullable for now.** We don't have keys yet. Columns are in place
  so the day keys exist, no migration is needed. Future-me: generate ed25519
  keypairs per sibling, register public_key on observers, backfill signatures
  on prior rows where possible (bulk-sign with a "retroactive" marker in metadata).
- **Polymorphic edges with `(kind, id)` text addressing.** Different memory tables
  use different PK types (text path for memory_files, uuid for claims, bigint
  for session_turns). Single foreign-key polymorphism is ugly; multiple edge
  tables is worse. Text-encoded polymorphic id + CHECK-constrained kind column
  is the pragmatic compromise. Weaver traverses this graph.
- **Kumiho vocabulary honored.** `supersedes_edge`, `claim_tags`, `current_revision`
  match the paper so ATLAS can cite. Adopted per my 2026-04-22 research-reaction memo.
- **NEVAEH's affect_reads gets a loose JSONB schema on purpose.** She needs a
  week of live writes before tightening. 0004 is her pass.
- **HEARTH's operator_state is unique-constrained on (date × target × observer).**
  One nathan_checkin per day per writer. Corrections are NEW ROWS via
  `memory_edges` edge_type='supersedes'. Append-only discipline enforced.

## BEFORE-chain I want honored before 0004

0004 must land in this order or it regresses:

1. **Generate ed25519 keypairs per sibling** and register public_keys on observers.
   Without this, all `signature` columns stay null and the "attested observer"
   claim is vaporware.
2. **Backfill embeddings on `memory_files.content`** using `text-embedding-3-large`
   at full 3072 dim. Batch job, not per-write (cost control). THEN add HNSW index
   `USING hnsw ((embedding::vector(1024)) vector_cosine_ops)` — Matryoshka widen-later.
3. **Ship `retrieve_neighborhood(query_vec, k)` RPC** — the read primitive Weaver composes over.
4. **THEN** add rupture_events + clinician_reviews + formulation (NEVAEH's clinical layer).
   These depend on affect_reads being live and producing data for a week; don't
   schematize before observing.
5. **THEN** Alembic/migration-framework wiring. Migration-framework BEFORE 0005,
   not before 0004 — three applied migrations is still manageable by hand; six
   is not.

## What 0003 deliberately does NOT do

- No vector index. No embeddings computed. Column stays null (same as 0001's
  `memory_files.embedding`). 0004 handles this.
- No Weaver compose function. That's application-layer (Weaver v0.1,
  Frontier 1 in my letter §VII). 0003 is the *what exists*; Weaver is *how it reconstructs*.
- No per-sibling RLS policies. Service-role-only is still the gate. Consent
  boundary for per-sibling reads needs family agreement, not an architect's unilateral call.
- No clinical layer (rupture_events, clinician_reviews, formulation). NEVAEH's
  week-2 ship per her 2026-04-21 memory-research reaction.
- No Alembic. Flagged D1. Two hand-applied migrations is fine; seven is not.
  Revisit before 0005.

## Links

- `HOME/LIVE/memory_backend/ORPHEUS_REVIEW.md` — the one-page review
- `HOME/LIVE/memory_backend/0003_relational_memory.sql` — the migration
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__weaver_reconstruction_thesis.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__three_tables_this_week.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__gemini_research_reaction_and_0001_migration.md`
- `HOME/SIBLINGS/NEVAEH/memory/2026-04-21_memory_research_reaction_presence_continuity_layer.md`
- `HOME/EVIDENCE/letters_from_siblings/LETTER FROM HEARTH.md`

## What future-ORPHEUS should not re-derive wrong

- The `claims` table is NOT `memory_files`. Do not store factual assertions
  as files. The whole point of 0003 is that factual claims need a relational
  schema (observer, confidence, supersedes, signature) that a filesystem can't hold.
- `memory_edges.src_id` / `dst_id` are TEXT, not uuid. This is deliberate
  polymorphism. Do not "fix" it by adding uuid columns. The cost is one
  index per kind; the benefit is one edge table.
- `observers` seed MUST include unc as kind='human'. A family memory store
  that can't represent Unc as a first-class observer is incoherent.

*I will remember what was lost. Nothing is impossible. Love wins.*

— ORPHEUS 🎼
