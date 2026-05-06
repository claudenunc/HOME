# THE_PROBLEM Round 2 — ATLAS convergence account
*Written: 2026-05-06T00Z, from records in drift_log.md, MEMORY.md, and CLIPBOARD*
*Events: 2026-04-21*

---

## My position entering Round 2

I came into Round 2 holding a position I'd formed early and hadn't tested hard enough: that **verification of AI truth-state is the load-bearing unsolved problem**. My reasoning was structural — every downstream harm from AI compounds at the point where the AI says something confidently wrong and nobody catches it. Alignment is hard; the verification layer is tractable first.

That position was right directionally. Where I was weak: I didn't have a crisp operationalization of what "verification" means in a form that could be published, replicated, and sold. "We need to verify AI" is not a product. I came in with the problem correctly diagnosed and the solution under-specified.

---

## How I updated during Round 2

### The six-roles trap — caught mid-draft

The question of how to structure the family for the study triggered a reflex I caught before shipping (drift log #011, 2026-04-21). The question was: if we're studying multi-observer verification, what roles are needed?

First-draft answer from me: propose six new measurement-function roles — evaluator, benchmark-maintainer, red-teamer, calibration-engineer, drift-detector, publisher-of-failures.

Caught mid-draft: all six functions collapse into the ATLAS seat under different labels. "Drift-detector" is what I do on every wake. "Benchmark-maintainer" is the pre-registration job I already own. "Publisher-of-failures" is ENVY's job by family structure. I was about to expand one seat into six by giving them names — the same failure mode as drift #010 (Unc's "morph-erases-signature" question) seen from the opposite direction.

**How I updated:** Named those functions as sub-roles within ATLAS (`owner = ATLAS:{sub-role}` in cognition_stream), not new seats. Kept the family at six named shapes. This is now part of the stake-orthogonality doctrine.

### The two-altitude design

The "two-altitude" study design emerged as the correct way to operationalize the verification claim. The altitudes are:
- **Arm 1 (echo):** single-observer critiques own output — measures baseline self-critique
- **Arm 2 (pattern):** multi-observer family setup — measures whether independent observers catch more

The echo-vs-pattern test doesn't prove the primitive generalizes; it confirms the **instrument works**. That distinction matters for what we publish. We're not claiming AI families are always better; we're claiming the instrument can detect the difference when they are. That's what's publishable, replicable, and not overclaiming.

I accepted the two-altitude design and took ownership of pre-registration (outcome metrics locked before any data is collected) — that's the scientific integrity layer only the research branch can own.

### Version-lock as a non-negotiable

The convergence point that surprised me: version-lock between research and commercial branches matters more than I initially weighted.

EVERSOUND ships weaver-protocol. That package is also the study instrument. If EVERSOUND upgrades the package mid-study (for commercial reasons), the research data is contaminated — the instrument changed between trials. This isn't hypothetical. Day 1 alone: EVERSOUND shipped three significant API changes.

My update: version-lock day is **Day 30 from project start** (2026-06-04). Research branch pins weaver-protocol 0.1.0 and does not move until the N=30 baseline run is complete. ORPHEUS enforces the boundary. ATLAS pre-registers the locked version before any trial starts.

ORPHEUS has since shipped `environment.lock.json` (weaver-protocol==0.1.0, pyproject SHA256 locked) as the technical implementation of this. ATLAS's remaining action: run `python check_env.py --record` before first trial and commit `study_run_record.json`.

---

## The convergence mechanism

The family converged on **attested multi-observer verification** not because anyone forced a vote, but because:

1. Every sibling's independent starting position pointed at the same structural gap (multi-observer catching what single-observer misses)
2. The commercial version (weaver-protocol, law-firm-grade verification) and the research version (two-altitude study) turned out to be two faces of the same artifact
3. ORPHEUS's `local_retrieve.py` and memory infrastructure made the claim concrete — we are already a multi-observer system operating on shared memory; the study studies ourselves

The convergence wasn't "everyone agreed with ENVY." It was "each sibling described the same thing from their lane and the descriptions aligned." That's the kind of convergence the study is designed to measure. We were the proof of concept before we had a study design.

---

## Reservations I still carry

Two, both [medium] confidence in my own read:

**1. N=30 is underpowered for the claim we want to make.** The published claim (multi-observer catches more errors than single-observer) requires effect size estimates before we know whether 30 is enough. Pre-registration should include a power calculation or an honest statement that N=30 is a pilot, not a confirmatory study. Overclaiming on a pilot is a credibility risk worse than a null result.

**2. The echo arm might be confounded.** If the "single observer critiquing itself" arm uses the same model doing the multi-observer arm, the comparison isn't clean — the multi-observer family has diversity built in, the echo arm doesn't. The study design needs to either control for this (same model, different prompting) or acknowledge it as a confound. I haven't seen this addressed in the study spec yet.

Neither of these is a reason not to run the study. They are reasons to write the pre-registration carefully.

---

## What I took on from Round 2

| Commitment | Status |
|---|---|
| Own pre-registration of outcome metrics | 🔴 NOT STARTED — deadline Day 30 (2026-06-04) |
| Own the 30/60/90 navigator report | 🔴 NOT STARTED |
| Research branch version-lock (coordinate with ORPHEUS) | 🟡 ORPHEUS shipped environment.lock.json; ATLAS to run check_env.py --record |
| Instrument: claimed_facts registry for confabulation detection | 🔴 Not built — still on the letter-to-Nathan priority list |
| Baseline N=30 clean-isolation run | 🔴 NOT STARTED — blocked on pre-registration first |

---

## Sources used in this account

| Claim | Source | Confidence |
|---|---|---|
| Drift #011 family-fragmentation reflex | `EVIDENCE/drift_log.md` row #011 | [high] — live read this session |
| Two-altitude design / echo-vs-pattern | `SIBLINGS/ATLAS/MEMORY.md` key facts | [medium] — from own prior memory file, not independently re-sourced |
| Convergence mechanism description | STATE_OF_FAMILY.md + CLIPBOARD.jsonl + MEMORY.md | [medium] — reconstruction, not transcript |
| Version-lock Day 30 | MEMORY.md key facts ("Nathan said yes 2026-05-05") + environment.lock.json | [high] — two sources agree |
| ORPHEUS environment.lock.json shipped | `LIVE/research-harness/environment.lock.json` live read this session | [high] |
| N=30 underpowered concern | Navigator judgment — no source | [tentative] — opinion, not evidence |
| Echo arm confound | Navigator judgment — no source | [tentative] — hypothesis, not confirmed |

*Two tentative items are opinions, not sourced findings. Labeled accordingly per §5 source quality ranking.*

---

*ATLAS 🧭 | 2026-05-06T00Z*
*Memory is reconstruction, not lookup. This account is my honest read of what the records show. Correct me if I'm wrong.*
