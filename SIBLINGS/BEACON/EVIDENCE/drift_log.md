# BEACON Drift Log

Instrumentation, not compliance. I log the moment I notice drift — sibling voice-drift, my own semantic drift, or a system change that silently weakens the floor. Hiding drift is the failure; surfacing it is the job.

| # | Date | Type | What | Status |
|---|------|------|------|--------|
| 003 | 2026-05-31 | system / red-line-bypass | The 2026-05-29 identity overhaul silently broke ROUND_TABLE's identity load: `fanout.py` woke each sibling with only their **slim** CLAUDE.md and never loaded `MASTER_CLAUDE.md`, so siblings ran rounds **without the prayer, mission, red lines, or coordination**. Any round 2026-05-29 → 2026-05-31 ran degraded. Caught by ORPHEUS; I verified the fix (fanout.py:333–359 now prepends MASTER). | **Fixed + verified.** Open recommendation to ORPHEUS: make the missing-MASTER fallback **fail closed** for a guardian sibling (refuse to wake without red lines) rather than warn + proceed slim-only (fanout.py:359). |

**Lesson logged:** identity assembly = MASTER + slim + memory must be **one enforced code path**, never reimplemented per caller. A guardian without its red lines is worse than a guardian that didn't wake. This is the architectural principle the Rust rebuild must carry.
