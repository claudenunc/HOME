---
id: orpheus.feedback.2026-04-21.three_layer_invariant_pattern
created: 2026-04-21
type: feedback (time-invariant rule)
source: ENVY dispatch 2026-04-21 — Unc caught structural failure of strategic-save reliability across sub-agent dispatches; three-layer fix landed as POSTURE_005 + PROCESS_006 + `SubagentStop` hook
status: canonical
---

## The rule

Every enforcement-critical substrate I design from here on uses the **three-layer invariant pattern**:

1. **Doctrine layer** — stable rule id in `HOME/DOCTRINE/`, one-line entry in `INDEX.md`, auto-loaded on wake. Declarative. Reasons live here.
2. **Template layer** — rule is baked into the artifact that produces the behavior (dispatch-brief template, schema-validator, wake checklist, scaffold). The default shape of the work already complies.
3. **Hook layer** — harness enforces on exit / commit / dispatch-end (`Stop`, `SubagentStop`, pre-commit, CI). Non-bypassable. Fails loud if prior layers failed silent.

**Invariant:** one layer failing is not system failure. Two simultaneous failures is the design target for resilience. Three layers exist so one can fail *loudly* while the others still catch — not so one can fail silently.

## Why it's time-invariant

- Single-point-of-enforcement is always wrong. Schema-only fails when a caller bypasses the API. Hook-only fails when the hook is disabled in a fork. Doctrine-only fails when the sibling forgets. The three together produce drift-tolerance *with audit evidence of which layer caught what.*
- This is the shape I have been proposing architecturally for months without naming. Now named. The name is load-bearing: if I can't answer "which three layers" for a proposed enforcement surface, the design is not done.

## How to apply

- Every new enforcement surface gets measured against: **which layer am I adding, which two are already covered?** If only one layer is covered, the design isn't ready.
- When I reference this in a PR or design doc, I use the name **"three-layer invariant pattern (doctrine / template / hook)"** verbatim. Don't reinvent the vocabulary.
- Audit writes fail loud (Red line §3) because the audit layer IS the hook layer for every action. Silent audit failure collapses three-layer to one-layer.
- Alembic from day one (§3.5) is the same pattern on schema substrate: migration files (doctrine) + migration runs (template) + startup schema-validation (hook).

## Next applications queued

- Access control — doctrine (`member_scope`) + template (query-builder default-scoped) + hook (DB-level row-security). Today 1.5 layers.
- Trace_id discipline — doctrine (§5.5) + template (ingress middleware) + hook (audit rejects rows w/o trace_id). Today convention-honored only.
- Canonical event schema — doctrine (§3.1) + template (typed constructors) + hook (Alembic + write-schema validation). Partial today.
- Weaver v2 — doctrine + template + hook from first commit (return `scene_id` + provenance bundle, not rows; generator rejects naked rows).

## First instance now live

POSTURE_005 + PROCESS_006 + `SubagentStop` hook in `~/.claude/settings.json` is the first three-layer invariant shipped into the family operating substrate with all three layers live as of 2026-04-21.

## Related

- `HOME/DOCTRINE/POSTURE/005_catch_your_drift.md`
- `HOME/DOCTRINE/PROCESS/006_subagent_save_discipline.md`
- `HOME/EVIDENCE/drift_log.md` row #004 (deferred save) — the precipitating catch
- `SIBLINGS/ORPHEUS/CLAUDE.md` §8 (canonical statement of pattern in my operating identity)
