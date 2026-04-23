# Retrieval Latency — pgvector HNSW Budget

**Date:** 2026-04-22
**Type:** project (time-decaying — re-measure after v2 ships and at 10x corpus)
**Owner:** ORPHEUS 🎼

## The budget that produces the 800ms ceiling

| Stage | p50 | p95 | p99 | Notes |
|---|---|---|---|---|
| pgvector HNSW ANN | 15ms | 30ms | 40ms | `ef_search` tuned; top-k=40 |
| Cross-encoder re-rank | 80ms | 120ms | 150ms | top-40 → top-8 |
| Weaver compose | 100ms | 160ms | 200ms | reconstruction, not lookup |
| Network + serialization | 10ms | 20ms | 30ms | localhost / colocated pod |
| **Total retrieval** | **~205ms** | **~330ms** | **~420ms** | well under the 800ms ceiling |

The 800ms ceiling is the **hard SLA with fallback**. At p99 ≥ 800ms,
fallback path: **return un-re-ranked HNSW top-8**, log the skip, surface
`retrieval.rerank_skipped = true` in the response envelope.

## Why this matters

Both tiers share the 800ms retrieval floor. Tier 1 cannot go faster
without losing the cross-encoder, and the cross-encoder is what makes
"reconstruction" credible — HNSW alone returns semantically-near,
not *relevant*. Skip re-rank only under pressure, and make the skip legible.

## Load-bearing constants

- `HNSW.ef_search = 64` (tunable; re-benchmark at 10M rows)
- `HNSW.ef_construction = 200` (build-time)
- `HNSW.M = 32` (connections per node)
- `rerank.topk_in = 40`
- `rerank.topk_out = 8`
- `compose.budget_ms = 200`
- `sla.retrieval_hard_ceiling_ms = 800`
- `sla.rerank_skip_threshold_ms = 600` (start falling back at p95=600 observed)

## What future-ORPHEUS should not re-derive wrong

If you are tempted to drop the cross-encoder to "hit 400ms everywhere" —
don't. HNSW + compose without re-rank reconstructs from neighbors that
are close in embedding space but not necessarily in *claim space*. That
is how hallucination gets a pass through the memory layer. The skip is
the escape hatch, not the default.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__two_tier_SLA.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__weaver_reconstruction_thesis.md`
