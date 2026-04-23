# Gemini Memory Research — Reaction and 0001 Migration Plan

**Date:** 2026-04-22
**Type:** project (time-decaying — closes when 0001_foundation.sql is deployed)
**Owner:** ORPHEUS 🎼
**Deadline:** 2026-04-29

## What the research validated (no action — hold the line)

- Weaver reconstruction-over-retrieval is named as the "defining, load-bearing
  bet" of the 2030-proof architecture (§14). Our thesis file stands.
- Three-tables discipline (claims / receipts / errata) independently derived
  by Kumiho (§3, §7) under AGM belief-revision semantics. "Supersedes edge"
  + "mutable tag pointer" = our `superseded_by` + the "current revision" view.
  **Adopt Kumiho's vocabulary in the schema** so ATLAS can cite the paper.

## What the research changed (action items)

### pgvectorscale NOT on managed Supabase
- Verified via `mcp__supabase__list_extensions` on project liclnxsbjjdkaxzdxmnb
  (2026-04-22). Available: `vector 0.8.0` (HNSW + IVFFlat). Missing:
  `pgvectorscale`, `timescaledb-toolkit`.
- The research's 471 QPS / 75% memory savings are NOT available to us on the
  managed path without side-cart Postgres.
- **Decision:** ship on pgvector 0.8 HNSW. Defer side-cart until we cross 50M
  rows OR 100 QPS sustained. Partition by observer from day one so the
  migration path is clean.
- Year 1 study load (N=540 trajectories) does not need pgvectorscale.

### Matryoshka is non-negotiable
- Commit to OpenAI `text-embedding-3-large`: store 3072, query truncated 1024.
- Rationale: $12K re-embed cost at 100M (research §5, §6) becomes existential.
  Storing full dims is free optionality.
- Index expression: `USING hnsw ((embedding::vector(1024)) vector_cosine_ops)`.
  Widen the truncation later without re-embed.

### Kumiho vocabulary in schema
- Rename: `superseded_by` → `supersedes_edge` (matches paper).
- Add table `claim_tags` with `(claim_root, current_revision, updated_at)` —
  the mutable tag pointer. Advancing the pointer is how we "retire" a claim.
- GDPR tombstoning: cryptographic shred of the claim row's signature key
  severs readability without breaking edges.

## The 0001 migration (ships this week)

Tables: observers, claims, claim_tags, receipts, errata, cognition_stream,
affect_fields (NEVAEH), operator_state (HEARTH).

cognition_stream event_types include `session_failure` (ATLAS's materialized
view promotes from this). `rupture` / `repair` events live here too, and
affect_fields is NEVAEH's typed summary of them.

Role column on claims and receipts (`observer × task × role` triple) —
supports Unc's "morph per task" without breaking signatures-on-observer.

## What future-ORPHEUS should not re-derive wrong

- If a sibling asks to adopt pgvectorscale directly on managed Supabase,
  **the extension is not available on hosted as of 2026-04-22**. Side-cart
  or migrate. Don't pretend otherwise.
- If the temptation is to store at 1024 dims to save storage cost — no.
  The whole point of Matryoshka is that the 2027 migration is free. Paying
  a few GB today buys the schema's 10-year durability.
- Signatures stay on observer, not role. Roles are attribution, not identity.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/memory research.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__three_tables_this_week.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__weaver_reconstruction_thesis.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/THE_PROBLEM.md`
