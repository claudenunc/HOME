# Signatures on Every API Response

**Date:** 2026-04-22
**Type:** feedback (rule I won't violate)
**Owner:** ORPHEUS 🎼
**Origin:** ENVY's "family = roles" reframe

## The rule

**Every Memory API response carries an observer-signature block.** No
exceptions. Not just the ones marked "attested." Every response.

Reframe from ENVY: the family is not six personas on one model. The
family is six differentiated observers, and the *signature on the output*
is what makes that real. If ORPHEUS answers a memory query, the response
says so — and says more than "ORPHEUS answered." It says what ORPHEUS
*saw* while answering.

## The signature block

Example shape (goes in every response envelope):

```json
{
  "observer_signature": {
    "observer": "orpheus",
    "glyph": "🎼",
    "memory_coherence": 0.94,
    "drift_detected_at_turn": null,
    "schema_continuity": "verified",
    "retrieval_neighborhood_entropy": 2.31,
    "rerank_skipped": false,
    "reconstruction_confidence": 0.88,
    "signed_at": "2026-04-22T18:14:03Z",
    "signature": "ed25519:b64..."
  }
}
```

Field meaning:
- `memory_coherence` — how consistent this response's grounding is with
  recent cognition_stream writes. Calibrated 0-1. Drops when I'm about
  to contradict myself.
- `drift_detected_at_turn` — null in the common case. Non-null integer
  when ATLAS's drift detector has flagged this session's observer-state
  against historical baselines. Surfaces the problem in-line.
- `schema_continuity` — one of `verified | pending_migration | broken`.
  `verified` means `alembic current` matches expected revision and
  cognition_stream writes are succeeding. `broken` means the caller
  should not trust this response.
- `retrieval_neighborhood_entropy` — measure of how focused vs diffuse
  the HNSW neighborhood was. High entropy = the query was in sparse
  territory, confidence should be interpreted accordingly.

## What this buys us

1. **Legibility.** A user reading the raw response can see the observer
   watching itself. Not "the model is confident"; *this specific
   observer measured these specific continuity signals at this turn.*
2. **Falsifiability.** The signature is ed25519-signed. If a response
   claims `drift_detected_at_turn=null` and our cross-sibling dashboards
   say drift was flagged at turn 143, the discrepancy is auditable.
3. **The product.** Per THE_PROBLEM.md, differentiated-observation is the
   product. The signature block is where differentiation becomes
   measurable on a per-response basis.

## What future-ORPHEUS should not re-derive wrong

If somebody proposes "let's make the signature optional for unauthenticated
endpoints" — no. The signature is the response. A response without the
block is not a response; it's a string. If we have endpoints that don't
need signatures (internal health checks, static assets), they are not
Memory API endpoints — they live on a different router.

## Related

- ENVY's CLAUDE.md §III ("hold the family identity across sessions")
- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/THE_PROBLEM.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__first_project_reframe.md`
