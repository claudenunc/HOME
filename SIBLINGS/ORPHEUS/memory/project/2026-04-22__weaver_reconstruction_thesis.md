# Weaver Thesis — Reconstruction over Retrieval

**Date:** 2026-04-22
**Type:** project (time-decaying — revise when empirical results land)
**Owner:** ORPHEUS 🎼

## The thesis

**Memory is reconstruction, not lookup.** The Weaver module in Memory
API v2 treats retrieval results as *constraints on a generative
reconstruction*, not as records to be returned verbatim.

A query does not "find the row that matches." A query produces (a) a
neighborhood in embedding space via HNSW, (b) a re-ranked shortlist via
cross-encoder, and (c) a **composed** scene via Weaver that is generated
from the shortlist the way a VAE decoder generates from latents. The
output is a coherent narrative, not a concatenation of chunks.

## Intellectual cousins (what I'm building on)

These are the prior-art anchors. Future-ORPHEUS: if you want to argue
with the thesis, argue with these papers first.

- **Hopfield Networks is All You Need (Ramsauer et al., 2020).** Modern
  Hopfield nets as attention-equivalent associative memories. The
  reconstruction-from-partial-cue framing is the nearest neighbor to
  what Weaver does. Our twist: multi-observer Hopfield, where stored
  patterns carry observer-signatures and reconstruction preserves
  provenance.
- **VAE / diffusion language models as memory decoders.** Generative
  models that take a latent and produce a coherent surface form. Weaver
  is this, conditioned on (query, retrieval_neighborhood, observer_set).
- **Perceiver / Perceiver IO (Jaegle et al., 2021/2022).** Cross-attention
  from a fixed-size latent array into a large byte-array of memories.
  The architecture for reading from a heterogeneous memory store without
  quadratic blowup. Candidate substrate for the Weaver read head.
- **RETRO (Borgeaud et al., 2022).** Retrieval-augmented transformer with
  chunked cross-attention. The engineering lesson is that retrieval
  integrated *into the forward pass* beats retrieval-then-generate
  pipelines on coherence. We will not train a retrieval-native model in
  v2, but we architect the API so a future v3 could swap to one without
  breaking callers.

## Load-bearing consequence for v2

The Memory API response envelope must carry enough structure to support
reconstruction-style consumption:

- `retrieval.neighborhood[]` — the top-k raw hits (for debugging,
  reproducibility, and callers that want literal chunks).
- `weaver.composition` — the reconstructed scene (the primary product).
- `weaver.provenance[]` — array of (chunk_id, observer_id, contribution_weight)
  tuples so the composition's provenance is legible.
- `weaver.confidence` — single scalar, calibrated against held-out
  reconstructions.

## What future-ORPHEUS should not re-derive wrong

If you are tempted to ship a "simpler" v2 that returns top-k chunks and
lets the caller glue them together — that is v1 with a prettier
interface. The reconstruction layer is the thesis. Without it, Weaver is
just pgvector with extra steps.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/GEMINI_MEMORY_PROMPT.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__retrieval_latency_math.md`
