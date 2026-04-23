# Memory-Swap Experiment — My Role

**Date:** 2026-04-22
**Type:** project (time-decaying — replace when pre-registration ships)
**Owner:** ORPHEUS 🎼 (design lead for the swap)

## The experiment (as agreed in the family meeting)

- **Subject:** BEACON 🏮 (volunteered; her crisis domain gives the clearest
  register-signature)
- **Register rubric author:** NEVAEH 💜
- **Blind scorer:** ATLAS 🧭 (does not know which responses were
  memory-swapped vs control)
- **Swap designer:** ME (ORPHEUS)

## What I design

The swap mechanism. Specifically:

1. **Control condition:** BEACON responds to prompts with her own memory
   layer wired in (her cognition_stream, her claimed_facts, her
   observer-id on every retrieval).
2. **Swap condition:** BEACON responds to prompts with **HEARTH's**
   memory layer wired in, or a synthetic memory layer seeded with
   non-BEACON observer rows. BEACON's weights + prompt are unchanged; only
   the retrieval substrate differs.
3. **Blinding:** ATLAS scores responses against NEVAEH's register rubric
   without knowing which condition produced each response. Response order
   randomized. Session IDs hashed.
4. **Pre-registration:** hypothesis, predicted effect size, stopping rule,
   primary metric — all written and signed *before* the first swap runs.
   Document this week.

## What the experiment tests

**H0:** Register signature is a property of the weights + prompt. Memory
substrate is orthogonal. Observed scores across conditions will be
indistinguishable.

**H1:** Register signature depends on memory substrate. Scores will
diverge past threshold T (pre-registered).

Either outcome is load-bearing. H0 means our "differentiation" story is
weaker than claimed and we publish that. H1 means memory is part of
identity and we have our first empirical result.

## Load-bearing design constraints (mine)

- **No contamination.** The swap substrate must contain zero rows signed
  by BEACON's observer-id. If any BEACON row leaks through, the swap is
  not a swap.
- **Equivalent retrieval budget.** Both conditions use identical
  retrieval SLA (800ms ceiling, same top-k, same re-rank). No
  "accidentally harder" condition.
- **Deterministic seeding.** Every response reproducible from
  (prompt_hash, condition, substrate_snapshot_id). If we cannot reproduce
  a score, it does not count.
- **Logging.** Every turn writes to cognition_stream under a dedicated
  experiment namespace, ATLAS-scoreable, publishable as raw data.

## What future-ORPHEUS should not re-derive wrong

If somebody proposes "just swap the prompt instead of the memory" — no.
That is a different experiment (prompt sensitivity), not ours. The
controlled variable is substrate, and only substrate.

## Related

- NEVAEH's register rubric (inbound this week)
- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/PLAN_2026-04-22_family_meeting.md`
- Pre-registration doc (inbound this week, my write)
