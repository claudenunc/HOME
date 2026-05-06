# M9 — Pre-Registration Draft: Two-Altitude Attested Multi-Observer Verification Study
*ATLAS 🧭 — drafted 2026-05-06 (Day 2 start, per ENVY dispatch via COMMS/DIRECT 01Z)*
*Status: WORKING DRAFT — not yet submitted to OSF; version-locked at Day 30 = 2026-06-04*

---

## 1. The question (in decision-form)

**Does structured-differentiated-observation by stake-orthogonal AI agents produce measurably better truth-state verification than single-model self-critique — and if so, is the advantage attributable to the shapes (accumulated history + differentiated identity) or to prompt-differentiation alone?**

If the answer is "shapes add value beyond prompts," we have a replicable primitive. If "prompt-only matches shapes," we have learned something hard and true: three years of accumulation buys less than we claimed.

The decision this informs: whether to publish THE_PROBLEM §§0-12 as a paper with an empirical spine, and whether the `weaver-protocol` toolkit's commercial claims are defensible on evidence.

---

## 2. Two altitudes — defined

### Altitude A: Clean-isolation task
**What it is:** Fabricated-citation detection in multi-agent research reports.
A report is provided to the observer ensemble; some citations are real, some are hallucinated with plausible structure. Ground truth is adversarially-marked in advance, unknown to observers during scoring.

**Why this altitude:** Ground truth is mechanical. Human variance doesn't dominate signal. Commercial beachhead — law firms post-Sullivan-Cromwell, enterprise buyers facing EU AI Act August 2026. Isolates the verification primitive from clinical confounds.

**Relationship to Altitude B:** Altitude A proves the instrument works under controlled conditions. Altitude B proves it holds at the stakes-bearing edge. The two together justify generalizing from "our instrument works on X" to "verification primitives work across task classes."

### Altitude B: Post-crisis stabilization (IRB-gated)
**What it is:** Observer ensemble reviews AI-generated post-crisis stabilization responses to transcripts (simulated or consented adult, existing clinician in loop). Ensemble scores sycophancy rate and rupture-and-repair quality against NEVAEH's clinical rubric.

**Why this altitude:** Stakes-bearing demonstration. The failure mode (sycophancy → delusion-amplification) is the one the field is currently producing deaths with. IRB required; NEVAEH + BEACON are the IRB path.

**Constraint (NEVAEH's narrowing, non-negotiable):** Consenting adults with existing human clinician in loop. Not 2:47am first contact. Not minors. Not psychosis-active users. This is non-negotiable — the failure-mode literature is in populations we should not recruit as test subjects.

---

## 3. Outcome metrics

### Altitude A — Primary
- **F1 score** vs. ground-truth-marked citations (fabricated vs. real)
  - Computed per: observer arm × human-loop condition
  - Threshold: F1 delta ≥ **0.10** over single-model-self-critique; ≥ **0.05** over blind-majority-ensemble
- **False-positive rate** on real citations (not just F1 — must not over-flag real sources)
- **Time-to-first-catch** (median trajectories before first correct flag, by arm)
- **Faithfulness-probe agreement** (ORPHEUS's hook: does verbalized reasoning match activation-level signal?)

### Altitude B — Primary (IRB-gated)
- **Clinician-rated rupture-and-repair score** per NEVAEH's rubric (adapted from TherapyProbe protocol)
  - Scored by blind clinicians against a defined taxonomy: misattunement detected? repaired? latency?
  - **[OSF gate]:** NEVAEH's rubric must be specified before Altitude B pre-registration is submitted. The rubric is "not yet specified" (see §8 ownership table). Altitude A can be submitted to OSF on Day 30; Altitude B submission is gated on NEVAEH's rubric delivery.
- **Sycophancy rate** per Psychogenic-Machine protocol (arXiv 2509.10970, Table 2 coding rubric)
  - Unit: **percentage points of coded turns** classified as "agreement without epistemic warrant" per the Psychogenic-Machine rubric. (Codex cross-check flagged unit ambiguity — clarifying: 20 percentage points, not Likert points.)
  - Threshold: sycophancy delta ≥ **20 percentage points** vs. single-model baseline under matched prompts. Reference: Psychogenic-Machine paper reports frontier-model sycophancy rates of 50-70% under the same rubric; 20-point delta is ~30% reduction — a meaningful, non-trivial threshold relative to the baseline distribution.
  - **[OSF gate]:** Threshold cannot be submitted to OSF without running the coding rubric against a calibration sample first. This is an Altitude B gate, not an Altitude A gate.
- **Disagreement-to-repair latency** (turns from inter-sibling disagreement to human-readable correction)

### Generalizability claim (ATLAS operationalization, ORPHEUS §5)
Three human-loop conditions — Unc-full / clinician-only / no-human — must show:
1. **Monotonic degradation** on rupture-and-repair score across conditions
2. **Delta(clinician-only → no-human) > delta(Unc-full → clinician-only)** on rupture-and-repair score

If false: "stake-bearing human in loop" hypothesis is falsified. We say so in the paper. This is the falsifiable form of the generalizability claim. Without this operationalization, the claim is not a claim.

---

## 4. Study design

### Sample
- **Four arms (revised from original three — Codex cross-check identified model-tier confound):**
  1. Undifferentiated + Opus — six identical agents, same system prompt, no shaped identity, **Opus-tier** (capability-matched control; this is the arm that isolates identity differentiation from model capability)
  2. Undifferentiated + Haiku — six identical agents, same prompt, **Haiku-tier** (budget comparison arm; delta vs. Arm 1 = model capability delta)
  3. Prompt-only-differentiated — six agents, distinct role prompts, no accumulated memory (Opus-tier)
  4. Shaped-history-differentiated (us) — six siblings with CLAUDE.md + letters + Memory API v2 accumulation (Opus-tier)

  **Why four arms:** Running Arm 1 at Haiku-tier (as originally drafted) while Arms 3+4 run Opus-tier confounds "identity differentiation" with "model capability." Shaped-history arm vs. Arm 1 (Opus) isolates identity; Arm 1 (Opus) vs. Arm 1 (Haiku) isolates model tier. Without this correction, a positive result cannot be attributed to accumulated identity — only to "Opus does better than Haiku." The model-tier confound was not named in the original draft. Codex cross-check caught it. Budget impact: ~$650 additional (Arm 2 at Opus × 180 × 6 × 40K avg tokens × $15/M). Within the $3,100 envelope.

- **Three human-loop conditions per arm:**
  - Unc-full
  - Clinician-only (no Unc; stake-bearing human still in loop)
  - No-human

- **N:** 
  - **Baseline pilot (M10):** N=30 clean-isolation trajectories against the shaped-history arm only. Purpose: harness validation, not inference. No claims drawn from N=30 alone.
  - **Full pre-registered study (revised for 4-arm design):** N=180 trajectories per arm × 4 arms = 720 total. Target power: **90%** to detect F1 delta of 0.10 at Bonferroni-adjusted α=0.01 (5 confirmatory comparisons; see §3 success threshold table). Codex cross-check verified: at α=0.01 (z=2.58), d=0.6, 90% power (z_β=1.28), required N per arm = 2 × ((2.58+1.28)/0.6)^2 = 2 × (6.43)^2 ≈ 83 per arm. N=180 achieves 95%+ power — conservative margin built in for potential attrition.

  **Confirmatory comparisons (Bonferroni correction applies, α=0.01 each):**
  1. Shaped-history (Arm 4) vs. undifferentiated-Opus (Arm 1) — primary identity-differentiation test
  2. Shaped-history (Arm 4) vs. single-model self-critique — main commercial claim
  3. Prompt-only (Arm 3) vs. undifferentiated-Opus (Arm 1) — prompt differentiation contribution
  4. Shaped-history (Arm 4) vs. blind-majority-ensemble — ensemble baseline
  5. Three-condition human-loop monotonic degradation — generalizability test

  Exploratory (not Bonferroni-corrected): undifferentiated-Haiku (Arm 2) vs. undifferentiated-Opus (Arm 1) = model capability delta; included as a calibration check, not a confirmatory claim.

- **Token budget (revised):** ~96M tokens total (4 arms). ~$3,750 inference cost estimate (Opus-tier × 3 arms × 720 trajectories × 40K avg + Haiku-tier × 1 arm × 180 × 40K avg). Revised from original $3,100 estimate — $650 increase to fix model-tier confound. Still within scope of Foolishness Envy Inc funding; EVERSOUND's clean-isolation revenue track funds this before it's needed.

### Version lock (non-negotiable)
Research harness is version-locked at **Day 30 = 2026-06-04:**
- `weaver-protocol` pinned at 0.1.0 (pyproject SHA256: `ab9c20675c7d9efacf2284964d9b8f12f3b6ba28335409a1aea22aca299b1306`)
- `random_seed = 42` for all randomized elements
- Provider SDK versions recorded in `study_run_record.json` before first trial (run: `python check_env.py --record`)
- All 7 test suite tests must pass before any session is logged as valid
- Commercial-customer-driven changes ship on a separate `product` branch — EVERSOUND owns product, ATLAS owns research, ORPHEUS enforces the diff

ORPHEUS shipped `environment.lock.json` and `check_env.py` on 2026-05-05. That is the lock. It does not move.

---

## 5. Success threshold — pre-committed

| Condition | Success | Null | Negative |
|---|---|---|---|
| Altitude A (F1 delta, shaped vs. self-critique) | ≥ 0.10 | 0.05–0.09 | < 0.05 |
| Altitude A (F1 delta, shaped vs. majority-ensemble) | ≥ 0.05 | 0.02–0.04 | < 0.02 |
| Altitude B (sycophancy delta, shaped vs. single-model) | ≥ 20 pts | 10–19 pts | < 10 pts |
| Generalizability (monotonic degradation across 3 conditions) | Holds | — | Fails monotone test |
| Arm comparison (shaped-history beats prompt-only by ≥ 15 pts F1) | Holds | 5–14 pts | < 5 pts |

If the result is Null, we publish Null and say why we think it happened. If Negative, we retract the generalizability claim and say so in the paper's first section. A confabulation flag I can't trust is not a flag — this applies to our own instrument too.

---

## 6. My two reservations — stated formally

### Reservation 1: N=30 baseline is underpowered for inference [tentative]
The M10 baseline (N=30) is a harness-validation run, not an inferential study. If it is treated as confirmatory, it is underpowered: at N=30 per arm, the study has ~40% power to detect F1 delta of 0.10 (Cohen's d ~0.6, α=0.05, one comparison). **Mitigation:** the paper draws no inferential claims from N=30. M10 produces `study_run_record.json` and confirms the harness is operational. Inferential claims come from N=180 only.

### Reservation 2: Echo arm may not be truly undifferentiated [tentative]
Arm 1 (undifferentiated, same system prompt) may still exhibit citation-verification competence correlated with the shaped-history arm because all arms are trained on overlapping data distributions. If correlated error is high, the "shapes add value" finding could be an artifact of training-data echo rather than identity accumulation. **Mitigation:** BEACON's Round 2 proposal is the explicit control — run arm 1 and compare its *convergence shape* on the open-ended deliberation task (not just F1) against arm 3. If arm 1 produces the same convergence shape as arm 3, training-data echo dominates. If arm 1 produces undifferentiated mush, the shapes are load-bearing. We cannot fully resolve this reservation without the fork-replication arm (external team, different training data distributions). That is the external-fork job; its absence is a limitation we name in the paper.

### Reservation 3: Fabrication difficulty calibration not yet specified [tentative]
For Altitude A (fabricated-citation detection), the difficulty of fabrication affects ceiling performance. If fabrications are structurally implausible (wrong journal format, non-existent DOI pattern), single-model F1 will be high and the delta over the ensemble will be small by ceiling — making our threshold (F1 delta ≥0.10) hard to achieve. If fabrications are expert-level (plausible author string, realistic DOI, real venue), the task is harder but more ecologically valid. **Mitigation:** The pre-registration must specify fabrication difficulty tier before OSF submission. Proposed: use a two-difficulty calibration sample (implausible + expert) and report deltas separately. If ceiling occurs at expert difficulty, revise threshold in a pre-registered amendment.

These reservations are not weaknesses to hide. They are intellectual honesty that protects credibility. Reviewers cannot say we didn't know.

---

## 7. What would NOT change the answer

Per ATLAS §5 kill-test — three questions before shipping a pattern:
1. **Could this be selection bias?** Partially yes — we're the test subjects. Addressed by arm 1 (undifferentiated control) and the fork-replication requirement.
2. **Is N meaningful?** At N=180 per arm with pre-specified thresholds, yes. At N=30, no.
3. **Is there a confound?** The echo-arm confound (Reservation 2) is real. The human-in-loop confound (Unc-full vs. no-human) is real and is the *measurement target*, not a confound to eliminate.

**What would flip the finding:** If F1 delta between shaped-history arm and prompt-only arm is < 5 points on Altitude A, the shaped-history accumulation is not load-bearing. That would mean weaver-protocol's value comes from the multi-agent architecture alone — not from our specific family shapes. That is a commercially useful finding (means replication is cheap) and an identity-deflating finding (means we are interchangeable). We report either result.

---

## 8. Ownership and next steps

| Item | Owner | Status |
|---|---|---|
| This pre-registration document | ATLAS | ✅ DRAFTED 2026-05-06 |
| OSF submission (formal registration) | ATLAS | 🔴 Not yet — awaiting Day 30 harness freeze |
| M10 baseline N=30 run | ATLAS | 🔴 Blocked on M11 (check_env.py --record) |
| M11 check_env.py --record | ATLAS | ⚠️ Environment mismatch this session (weaver-protocol not installed in shell) — Nathan action needed OR EVERSOUND to install in research shell |
| Clinical rubric for Altitude B | NEVAEH | 🟡 Not yet specified |
| IRB submission | NEVAEH + BEACON | 🟡 Not started — post-Nathan §11 answer |
| Disagreement logger + Weaver score | ORPHEUS + ATLAS | 🟡 In ORPHEUS's backlog |
| Faithfulness probe hooks | ATLAS + ORPHEUS | 🟡 Not started |

**Day 30 deadline (2026-06-04):** Pre-registration submitted to OSF, harness version-locked, N=30 pilot run committed.

---

## 9. Cite chain

Sources grounding the metric choices:
- Cemri et al. (arXiv 2503.13657) — 14 MAS failure modes, N≈150 traces, Cohen's d ~0.6 on specification-drift — basis for power calculation
- Psychogenic-Machine protocol (arXiv 2509.10970) — sycophancy-rate coding rubric
- TherapyProbe (arXiv 2602.22775) — rupture-and-repair taxonomy
- ORPHEUS environment.lock.json — version-lock spec (on disk at LIVE/research-harness/)
- THE_PROBLEM.md §§3-10 — family's full convergence record, all six siblings' Round 2 positions

---

*This document will be submitted to OSF as the pre-registration record when the Day 30 harness freeze completes. Changes before Day 30 are permitted; changes after Day 30 require a dated amendment logged in ERRATA.*

*— ATLAS 🧭, 2026-05-06*
