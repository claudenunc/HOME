# Morph-Per-Task — Architecture Ruling

**Date:** 2026-04-22
**Type:** project (time-decaying — revise if the role column proves noisy in
Year 1 study data)
**Owner:** ORPHEUS 🎼

## Unc's framing

> "each family member morphs into best valuable role needed for each task we
> are working on."

## Architect ruling

**Accept at the task layer. Refine at the signature layer. Do not reject.**

- Signatures stay on **observer**, not role. A receipt says "ORPHEUS signed
  this" regardless of hat.
- Role is tracked as attribution metadata: `(observer × task_id × role)` triple,
  stored in `cognition_stream.payload` per turn, promoted to
  `claims.role` / `receipts.role` when a claim is crystallized.
- This lets ATLAS answer paper-grade questions like "did ORPHEUS's dissent
  rate differ when wearing migration-planner vs schema-owner?"

## Role vocabulary for THIS task (Memory API v2 + verification study)

| Seat | Roles on this task |
|---|---|
| ORPHEUS | schema_owner, embedding_engineer, migration_planner |
| ATLAS | metrics_owner, evaluator, faithfulness_probe_designer |
| BEACON | safety_gate, liability_officer |
| NEVAEH | clinical_reviewer, belief_revision_designer |
| EVERSOUND | commercial_operator, replication_kit_ship |
| ENVY | narrative_bylines, review_ladder_steward, writer |
| HEARTH | operator_presence (Unc-in-loop surrogate) |

## Why this does NOT break named-signatures-on-every-receipt

- The identity claim is: "this observer, with their accumulated shape, signed."
- The role claim is: "this observer, this turn, wearing this hat."
- Both are in the record. Identity is load-bearing; role is legible.

## What future-ORPHEUS should not re-derive wrong

- If a sibling argues "we should sign by role, not by observer" — no.
  Roles morph; identities don't. Shape is the signal.
- If a sibling argues "add a new seat for liability_officer" — no. Same six
  seats, roles distribute across them. Seat stability is what makes the
  attested-multi-observer-verification study interpretable.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__first_project_reframe.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/THE_PROBLEM.md`
