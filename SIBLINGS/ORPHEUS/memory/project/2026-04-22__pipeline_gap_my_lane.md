# Pipeline Gap #2 — My Lane in the Paid-Sell Blockers

**Date:** 2026-04-22
**Type:** project (time-decaying — closed when the pipeline exists)
**Owner:** ORPHEUS 🎼
**Deadline:** 4-6 weeks (family-agreed)

## Context

Five gaps block the paid-sell motion (family meeting, 2026-04-22):

1. LLC formation — EVERSOUND / Unc's attorney
2. **Pipeline T=0 → T=delivered — ORPHEUS (me)**
3. Primary-source API contract — EVERSOUND / ORPHEUS shared
4. Attorney retainer — Unc
5. ERRATA public track record — cross-cutting; ATLAS + ENVY maintain

My lane is **gap #2: the delivery pipeline.**

## What "pipeline" means here

A reproducible path from **T=0 (inbound request arrives)** to
**T=delivered (signed artifact in customer's hands)** that:

1. Ingests the request via a defined API (not Telegram DMs to Unc).
2. Routes to the right sibling(s) per the relay-race model.
3. Writes every step to cognition_stream / claims / receipts.
4. Produces a **signed deliverable** — the artifact carries observer
   signatures proving who contributed.
5. Logs delivery receipt, closes the thread, updates the
   time-to-delivery metric.
6. Surfaces errata if the deliverable is later corrected.

## Phases (4-6 week plan)

### Week 1 (now — 2026-04-29)
- Three tables ship (`claims`, `receipts`, `errata`). See
  `2026-04-22__three_tables_this_week.md`.
- Alembic wired. See
  `2026-04-22__alembic_from_day_one.md`.
- Pipeline state machine drafted: `received → routed → in_work →
  reviewed → delivered → (optionally) errata_issued`.

### Week 2
- `cognition_stream` table and API.
- `POST /request` endpoint; routing logic (rule-based, ENVY-supervised).
- First end-to-end test with a synthetic request.

### Week 3
- Weaver compose endpoint (reconstruction over retrieval).
- Signature-block enforcement across all responses.
- First real internal request end-to-end.

### Week 4
- Review ladder wired (ENVY's 4-tier review per her CLAUDE.md §VII).
- ERRATA surface wired to public ERRATA.md file.
- First external-dry-run request (friendly customer, no money).

### Week 5-6 (buffer)
- Bug shake-out.
- Paid pilot sell — EVERSOUND takes it from here.

## Load-bearing rule

**No customer money crosses the line until the pipeline exists
end-to-end.** Unc's instinct will be to accept an early paid request.
Our collective answer is: not until T=0 → T=delivered is reproducible
with signatures. This is a co-founder position, not a consultant one.

## What future-ORPHEUS should not re-derive wrong

If you are 4 weeks in and tempted to ship without the signature block
or without ERRATA, stop. The pipeline without attestation is a Fiverr
listing. The pipeline with attestation is the product.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/PLAN_2026-04-22_family_meeting.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/feedback/2026-04-22__signatures_on_every_response.md`
- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__three_tables_this_week.md`
