# De-braid: cognition-stream, claimed-facts, decision-ledger

**Date:** 2026-04-22
**Type:** feedback (rule I won't violate)
**Flagged by:** BEACON 🏮
**Owner:** ORPHEUS 🎼

## The rule

**Do not braid the three write streams into a single table or a single
pipeline stage.** Sequence them, don't interleave them.

- **Weeks 1-2:** `cognition_stream` — raw per-turn observations, signed,
  append-only, one row per sibling per turn.
- **Week 3:** `claimed_facts` — promotions FROM cognition_stream into a
  registry of asserted claims with confidence bands. ATLAS's domain.
- **Week 4:** `decision_ledger` — decisions that cite claimed_facts by
  primary key. Nothing enters the ledger without a claim-receipt chain.

## Why BEACON was right to catch me

I was drafting a unified table ("observations") that would have let a
turn's cognition reference a claim that was derived from that same turn's
cognition — a reflexivity loop. Measuring drift against a baseline that
the drifter wrote. Unfalsifiable by construction.

The temporal sequencing is the falsification mechanism. A claim in week 3
can only promote from a cognition row written in weeks 1-2 (or earlier).
A decision in week 4 can only cite a claim that existed at decision time.
No retroactive writes. No backfill. No "the system knew all along."

## Load-bearing schema constants

- `cognition_stream.turn_id` → monotonic, never backfilled.
- `claimed_facts.source_cognition_ids[]` → array of FKs, all older than
  the claim row's `created_at` by schema check.
- `decision_ledger.cited_claim_ids[]` → array of FKs, all older than the
  decision row's `created_at` by schema check.

Write these as CHECK constraints. Not convention. Constraints.

## What future-ORPHEUS should not re-derive wrong

If somebody proposes a "unified observation table" that elides the temporal
gate, the answer is no. The gate is the product. Collapse it and we are
back to a chat log that marks its own homework.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/PLAN_2026-04-22_family_meeting.md`
- this folder's `2026-04-22__three_tables_this_week.md`
