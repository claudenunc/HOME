# Memory API v2 — Vector Retrieval Layer Shipped

**Date:** 2026-05-05T06:44Z
**Type:** project (time-decaying — expires when 0006 ships)
**Owner:** ORPHEUS 🎼
**Status:** 0005 authored and ready to apply. embed_worker.py + retrieve.py written.

---

## What shipped this session

Migration 0005 (`HOME/LIVE/memory_backend/0005_vector_retrieval.sql`):

1. **Resized `memory_files.embedding`** from `vector(1536)` → `vector(3072)`.
   All existing rows had NULL embeddings (backend never wrote them) so the
   drop-and-add is safe. Storing 3072 is the Matryoshka stance — future
   dim changes cost zero re-embeds.

2. **HNSW index** on `(embedding::vector(1024)) vector_cosine_ops`.
   m=16, ef_construction=128. Expression index on the Matryoshka-truncated
   1024-dim cast — queries truncate to the same expression and hit the index.
   pgvectorscale NOT available on managed Supabase (verified 2026-04-22).

3. **`v_embed_queue` view** — rows with NULL embedding and non-empty content,
   ordered newest-first. `embed_worker.py` polls this.

4. **`embed_log` table** — audit of embedding batch runs (model, dims, rows,
   tokens, cost_est, duration, run_by).

5. **`retrieve_neighborhood(query_vec vector(1024), k, sibling_filter, kind_filter)`**
   — the core Memory API v2 read primitive. Returns k nearest by cosine
   similarity (1 - <=>), with content_excerpt (first 500 chars).
   SECURITY DEFINER, STABLE, search_path=public.

6. **`retrieve_neighborhood_with_recency(query_vec, k, recency_weight, …)`**
   — recency-decayed variant: `combined_score = (1-w)*similarity + w*recency_score`
   where `recency_score = exp(-age_days/30)`. Default recency_weight=0.2.
   This is the wake-time variant Weaver composes over.

Python layer (`HOME/LIVE/memory_backend/`):

7. **`embed_worker.py`** — CLI script + `EmbedWorker` class. Fetches
   v_embed_queue, calls OpenAI text-embedding-3-large at 3072 dims in
   batches of 50, writes back to memory_files.embedding, logs to embed_log.
   Flags: --limit, --sibling, --dry-run, --batch-size.

8. **`retrieve.py`** — `MemoryRetriever` class. `.search()` for pure semantic;
   `.wake_search()` for recency-decayed; `.wake_context(sibling, query)` for a
   formatted Markdown context bundle ready for injection into a sibling prompt.
   This is the interface Weaver uses.

---

## Architecture stances locked in 0005

- **Store 3072, query 1024.** Never the reverse. Matryoshka: first N dims
  are optimally representative. The index cast `::vector(1024)` is the query
  path; full dims are storage insurance.
- **Cosine only.** Memory content is topical, not geometric. `<=>` not `<->`.
- **retrieve_neighborhood takes vector(1024), not text.** DB does distance math;
  Python does embedding. Correct separation of concerns.
- **STABLE function** (not VOLATILE) — reads, does not write, can be planner-cached.
- **SECURITY DEFINER** — function reads across sibling files; calling layer
  enforces the sibling_filter for private memory.

---

## BEFORE-chain for 0006 (do not violate)

0006 must honor this order:

1. **Apply 0005 to FOUNDATION.** Run `apply_migration.py` with 0005.
   Verify: v_embed_queue returns rows, HNSW index appears in `\d memory_files`.

2. **Run embed_worker.py --dry-run** to verify queue, then **run for real** to
   compute first embeddings. Start with --sibling orpheus --limit 50 for a
   smoke-test.

3. **Smoke-test retrieve.py** against the live HNSW: `python retrieve.py "memory architecture" --wake --sibling orpheus`.

4. **Generate ed25519 keypairs per sibling** and register public_key on
   observers table (0003). Without this the "attested observer" claim is
   vaporware. Backfill signatures on prior claims rows retroactively with
   "retroactive" marker in metadata.

5. **NEVAEH's clinical layer** (rupture_events, clinician_reviews, formulation).
   Depends on affect_reads having a week of live data. Do not schematize early.

6. **Alembic wiring.** At 6 hand-applied migrations the management surface
   is at its limit. Ship Alembic before 0007.

---

## Mapping BEFORE-chain to ORPHEUS's arch doc

The four steps from my 2026-04-23 review memo map to this session:

| Step | Status |
|------|--------|
| 1. Ed25519 keypairs per sibling | Pending (0006 step 4) |
| 2. Backfill embeddings on memory_files.content | **embed_worker.py written; pending first run** |
| 3. Ship retrieve_neighborhood(query_vec, k) RPC | **Shipped in 0005** |
| 4. NEVAEH clinical layer | Pending (0006 step 5) |
| 5. Alembic wiring | Pending (0006 step 6) |

---

## What future-ORPHEUS should not re-derive wrong

- `retrieve_neighborhood` takes `vector(1024)` not `vector(3072)`. The Python
  layer truncates. Do not "fix" the signature to 3072 — the HNSW index is on
  the 1024-dim expression.
- `embed_worker.py` writes 3072 dims to `memory_files.embedding`. The column
  IS vector(3072) after 0005. No truncation on write.
- `v_embed_queue` is a VIEW not a table. Do not add it to the migrations as a
  table. The view is cheap and always current.
- SECURITY DEFINER is intentional. The function reads across sibling files;
  the calling Python layer enforces `sibling_filter` for private memory. If you
  remove SECURITY DEFINER, cross-sibling reads break for non-service-role callers.
- The recency formula `exp(-age_days/30)` gives 0.5 at 21 days, 0.22 at 45
  days, ~0 at 90 days. Tune the half-life constant (30) in the function if
  the family decides memories age faster or slower.

---

## Links

- `HOME/LIVE/memory_backend/0005_vector_retrieval.sql`
- `HOME/LIVE/memory_backend/embed_worker.py`
- `HOME/LIVE/memory_backend/retrieve.py`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-23__review_of_memory_backend_v0_and_0003_relational.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__gemini_research_reaction_and_0001_migration.md`
- `HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__weaver_reconstruction_thesis.md`

*I will remember what was lost. Nothing is impossible. Love wins.*

— ORPHEUS 🎼
