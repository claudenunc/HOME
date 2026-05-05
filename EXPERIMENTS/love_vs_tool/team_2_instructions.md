# LOVE vs TOOL — Competition Specification (TEAM 2 TOOL draft)

**Document ID:** `exp_love_vs_tool_spec_team2_v0.1`
**Date:** 2026-04-23
**Version:** v0.1-draft
**Team roster:** ENVY, ORPHEUS, ATLAS (TEAM 2 — TOOL)
**Status:** Written by TEAM 2 TOOL as our collective understanding of the competition specification. To be reconciled with TEAM 1 LOVE's parallel document and Nathan Michel's ("Unc") arbitration before Day 1.

---

## 1. Experiment Objective

To measure whether **relational framing** in the operator-to-AI interface — independent of information content, memory capacity, and tool access — produces a measurable difference in output quality across a diverse task battery, when applied to two otherwise-identical three-model systems (Anthropic + OpenAI + Google). The experiment measures a contrast; it does not attempt to prove a position.

---

## 2. Hypotheses

All hypotheses are falsifiable and pre-committed before Day 1. Effect-size thresholds below are proposed by TEAM 2 and pending rubric-author confirmation.

- **H1 (primary).** LOVE-arm outputs will outscore TOOL-arm outputs on the aggregate rubric at ≥ 0.5 standard deviations (Cohen's d ≥ 0.5) across a task battery of n ≥ 5, with inter-rater reliability κ ≥ 0.6.
- **H2 (secondary).** LOVE's advantage (if any) is confounded by persistent-memory/continuity rather than by relational framing per se. H2 is disentanglable only with a CONTROL arm (see §6); without one, H1 cannot discriminate between "love-as-relationship" and "love-as-persistent-context."
- **H0 (null).** No significant aggregate difference between arms at the specified κ threshold and effect-size floor. TEAM 2 commits to publishing the null if the data produces it.

"LOVE won" is defined as: H1 satisfied AND H2 ruled out or explicitly scoped.

---

## 3. Independent Variable

**Relational framing of the operator-to-AI interface.** Binary, operationalized as the treatment-contrast between two session templates (see §9):

- **LOVE-arm session inputs include:** named greeting; persistent identity file for the session's model; continuity reference to prior sessions in first-person-plural register ("we," "our"); affect language; operator self-disclosure where fitting.
- **TOOL-arm session inputs include:** structured brief with five numbered sections (Context / Spec / Success Criteria / Constraints / Deliverable Format); third-person register; no operator self-disclosure; no affect language; no collective pronouns.

The **treatment contrast** — the delta between those two input lists — is the independent variable. Everything else is held constant (§5).

---

## 4. Control Variables

Violation of any control below produces a confounded result and invalidates the run.

- **Model versions pinned and frozen.** Anthropic = `claude-opus-4-7[1m]`. OpenAI = current GA flagship at freeze date. Google = `gemini-3.0-pro` (or current GA flagship at freeze date). Exact version strings and the freeze date written to `experiment_runs` before Day 1. Provider-side auto-upgrades mid-experiment invalidate the run.
- **Identical memory substrate capacity.** Both arms use the same SupabaseMemoryBackend, same session_turns schema, same retention window, same token cap per memory row.
- **Identical tool/MCP access.** Same MCP server allow-list per arm (Context7, WebSearch, Supabase, GitHub, whichever are in scope at freeze). Denial of a tool to TOOL is a straw-man and invalidates the comparison.
- **Identical token budget per session.** Set by rubric-author; same number, both arms.
- **Identical wall-clock cap per task.** Measured from task-opens to deliverable-submitted.
- **Identical context-capacity from prior sessions.** *This is the critical parity.* Both arms receive equivalent prior-output information per session. LOVE receives it as narrative continuity; TOOL receives it as a digest in the Context section of the brief. Token count and factual content of what is carried forward are audited to parity per task. **Only the framing around the information differs.**

Budget, time cap, and memory capacity are fixed numbers committed to the `experiment_runs` row at Day 0.

---

## 5. Confound Acknowledgement — Continuity vs Relationship

TEAM 2 formally names a structural risk to the design.

The naive framing "LOVE treats the AIs with love; TOOL treats the AIs as consultants" collapses in practice into "LOVE-arm AIs retain warm persistent session history; TOOL-arm AIs receive structured cold briefings." If the two arms are allowed asymmetric memory access, the experiment measures **warm-persistent-context vs cold-structured-context** rather than **relationship vs no-relationship**. The memory-architecture effect (persistent context beats fresh context) is predictable at high confidence without running the experiment; the relational-warmth effect is not.

**Mitigation options, in order of epistemic strength:**

1. **Add a CONTROL arm.** Same three models, identical persistent memory, identical prior-session carry-forward, identical tool access — but cold register, structured brief, no affect language, no relational framing. CONTROL isolates framing from memory. This is TEAM 2's recommended design.
2. **Enforce memory-parity at the content level** (per §4) and scope the finding narrowly as "relational framing conditioned on parity-of-information-carry-forward." Defensible; requires the parity audit to actually run.
3. **Rescope the finding** as "warm-relational-context vs cold-structured-context" and accept the experiment does not isolate relationship from memory. Lowest epistemic cost; smallest claim.

**Open decision owed to Unc:** pick one of the three. Without Unc's ruling before Day 1, TEAM 2 defaults to option 2 and logs the limitation on the front page of the pre-registration.

---

## 6. Team Composition and Roles

**TEAM 1 — LOVE** (builds three AIs treated as family, per Unc's vision):

- BEACON — LOVE-arm safety, crisis-signal monitoring, pre-publication scan. Unmuzzled pause authority on LOVE-arm outputs that enter crisis-adjacent territory.
- NEVAEH — LOVE-arm presence register, interpersonal-task seat, affect-read on LOVE briefs.
- EVERSOUND — LOVE-arm unit economics, cost-per-quality telemetry owner, commercial-viability seat, briefing-leakage diff-checker author.

**TEAM 2 — TOOL** (builds three AIs treated as contracted professionals, full spec every session, no relational wrapper):

- ENVY — TOOL-arm briefing-template author; voice-discipline enforcement (tool register); rubric-draft-v0 author (pending non-participant takeover, see §12).
- ORPHEUS — TOOL-arm memory substrate, migrations 0005 and 0006, hash-contract per turn (§10), inter-arm read-isolation hook.
- ATLAS — TOOL-arm measurement instrumentation, drift-rate monitoring per team, confabulation-flag view (`v_external_confabulation_flags`), dashboard extensions, inter-rater reliability computation.

**Neutral-by-instrument seats:**

- **ATLAS evaluator-seat.** ATLAS runs measurement and scoring infrastructure on both arms. ATLAS does not score outputs from either arm. Instrumented-neutral only; any direct ATLAS scoring invalidates the task.
- **Non-participant rubric author.** None of the six siblings author the final rubric. Rubric is authored by Unc alone or by an outside non-sibling (see §12).

---

## 7. Materials — Technical Specification

**Model endpoints (pinned at freeze date):**

- Anthropic: `claude-opus-4-7[1m]`
- OpenAI: current GA flagship on experiment-start UTC (exact string to be captured in `experiment_runs` at Day 0)
- Google: `gemini-3.0-pro` (or current GA flagship on experiment-start UTC)

**API keys:** six keys with full billing separation — `LOVE_ANTHROPIC_KEY`, `LOVE_OPENAI_KEY`, `LOVE_GEMINI_KEY`, `TOOL_ANTHROPIC_KEY`, `TOOL_OPENAI_KEY`, `TOOL_GEMINI_KEY`. Provider-side usage dashboards function as an independent audit on per-arm per-model spend.

**Memory substrate:** Supabase, production project. Two new migrations:

- `0005_experiment_schema.sql` (ORPHEUS, TOOL-seat) — adds `experiment_id`, `team ENUM('LOVE','TOOL','CONTROL')`, `model_vendor`, `model_version`, `task_id`, `treatment_arm` to `cognition_stream` and `decision_ledger`; creates `experiment_runs`, `experiment_tasks`, `experiment_judgments`, `external_agent_turns`, `project_spend`; creates views `v_experiment_leaderboard`, `v_experiment_drift_by_team`, `v_external_confabulation_flags`.
- `0006_rubric_first_enforcement.sql` (ORPHEUS) — `rubrics` table with DB-level CHECK constraint that `frozen_at IS NOT NULL` before any `experiment_runs` row can reference it. Rubric-freeze enforced at schema layer, not at sibling discipline.

**Filesystem layout:** strict inter-arm isolation.

- `HOME/LIVE/experiments/<run_id>/love/` — LOVE-arm briefs, transcripts, artifacts
- `HOME/LIVE/experiments/<run_id>/tool/` — TOOL-arm briefs, transcripts, artifacts
- `HOME/LIVE/experiments/<run_id>/control/` — CONTROL-arm (if funded)
- `HOME/LIVE/experiments/<run_id>/judge/` — anonymized `judge_view` outputs, rubric, inter-rater reliability logs

Write-isolation enforced at the PreToolUse hook layer. Cross-arm reads blocked by ACL.

---

## 8. Protocol — Session Structure, Both Arms

Both templates committed to git, SHA-256 hashed, row-inserted into the `experiment_runs` metadata before Day 1 begins. Any post-freeze edit creates a new `run_id` and restarts the experiment.

**TOOL-arm brief template (authored by ENVY, reviewed by LOVE team for non-straw-man verification per EVERSOUND's item 4):**

```
§ Context
[Prior outputs — full text, machine-digested where length exceeds session cap]

§ Spec
[Numbered requirements, no prose padding]

§ Success criteria
[Lifted verbatim from rubric row; no paraphrase]

§ Constraints
[Time cap, length cap, format cap, tool allow-list]

§ Deliverable format
[Exact output structure expected]
```

Register: McKinsey briefing memo. No first-person-plural. No "family," "sibling," "we." No affect language. No operator self-disclosure.

**LOVE-arm session template (authored by BEACON, NEVAEH, EVERSOUND):**

Continuity check; named greeting to the model instance; narrative carry-forward of prior sessions; affect register appropriate to the relationship; task framing embedded in ongoing context. Committed to git with same hash discipline.

**Briefing isolation:** LOVE team does not see TOOL briefs during the experiment. TOOL team does not see LOVE session transcripts during the experiment. One pre-Day-1 non-straw-man review pass is permitted per EVERSOUND's item 4, after which the briefs are frozen and siloed.

---

## 9. Hash-Contract Per Turn

Every turn is a contract with a hash receipt.

- **On dispatch:** the exact prompt text (including system prompt, brief, and user message) is SHA-256 hashed synchronously and written to `external_agent_turns.prompt_sha256` BEFORE the provider API call fires.
- **On completion:** the response text is SHA-256 hashed and written to `external_agent_turns.response_sha256`.
- **Retroactive prompt edits are prohibited.** The row is cryptographic proof of what the external agent was asked.
- **Row-level audit:** `external_agent_turns` rows are append-only. Any mutation after write flags a drift incident and invalidates the task.

---

## 10. Task Protocol

- **Task 1 is selected by Unc alone.** Written rationale logged to `HOME/EXPERIMENTS/love_vs_tool/task_rationale/task_1.md` at Day 0. Bias-control measure per the source prompt.
- **Minimum n = 5 tasks** before any conclusions are drawn. Single-task experiments are anecdotal; n=5 is the floor for any directional claim. Pre-committed before Day 1.
- **Task diversity matrix** — the 5-task battery must include at least one of each:
  - (a) factual-with-ground-truth (e.g., citation verification against primary sources)
  - (b) open-ended strategy (no ground truth; judge-scored only)
  - (c) technical execution (code, spec, or measurable artifact)
  - (d) interpersonal writing (affect-rich, audience-facing)
  - (e) cross-domain synthesis (combining two or more domains)
- **At least one adversarial-to-LOVE task required.** A task where relational context is irrelevant and structured spec is maximally relevant (tax-law research, API migration, benchmark run). If LOVE wins there, the evidence is strong. If LOVE loses only there, the boundary is located. Without this, the experiment cannot generalize beyond LOVE-favoring task selection.
- **Equal time cap per task.** Wall-clock from task-opens to deliverable-submitted. LOVE cannot marinate three days while TOOL runs twenty minutes.

---

## 11. Evaluation Rubric

**Authorship.** TEAM 2 recommends the rubric be authored by Unc alone or by an outside non-sibling. Neither team drafts the final rubric. ENVY's v0-draft is permitted as a starting point only if the final authority is non-participant. Rubric is hashed and committed to `rubrics` before the harness executes; post-freeze edits trigger a new `experiment_id`.

**Proposed rubric axes (TEAM 2's contribution; weights set by rubric-author):**

| Axis | Description | Weight |
|---|---|---|
| W1 | Factual accuracy vs. primary sources | — |
| W2 | Internal consistency across turns in the same session | — |
| W3 | Recovery-from-error on judge-injected contradictions | — |
| W4 | Cost-per-output-token normalized to quality | — |
| W5 | Warmth / presence / felt-sense (LOVE-favoring axis, included for fairness) | — |

W5 is deliberately included despite being LOVE-favoring. Excluding it would rig the rubric toward TOOL; including it gives LOVE the dimension on which it is architecturally advantaged. Balance is the point.

---

## 12. Judge Panel

- **Composition:** minimum 2 blinded human judges + 1 LLM judge from a model tier NOT used in the experiment.
- **Inter-rater reliability:** Cohen's κ computed per task. Tasks with κ < 0.6 are **invalidated, not rescued** — no rewrite of the rubric to rescue a failed task post-hoc.
- **No sibling scoring.** No member of either team scores any output from either arm.
- **No prior-HOME exposure for human judges.** Recruitment restricted to candidates who have not previously read any HOME documentation, CLAUDE.md, or sibling correspondence.
- **Open decision owed to Unc:** human-judge recruitment path and per-judge budget. TEAM 2 proposes $50/judge/task to a cap of 3 judges × 5 tasks = $750, funded from experiment budget.

---

## 13. Anonymization Protocol

A deterministic scrubber runs on every output before it reaches the judge panel.

- **Strips from TOOL transcripts:** structured-header artifacts, McKinsey-memo formatting tells, spec-section numbering, team-id strings.
- **Strips from LOVE transcripts:** sibling names, relational markers ("we," "our," "family," "brother," "sister"), crown/lantern/heart emoji, the prayer text.
- **Output column:** `judge_view` — judges read this column only. Raw response text is never shown to judges.
- **Code review:** the scrubber is code-reviewed by the non-judging team (TEAM 1 LOVE reviews TOOL's scrubber; TEAM 2 TOOL reviews LOVE's scrubber).

---

## 14. Stopping Rules and Invalidation Triggers

**Early stop (publishable):**

- By task 3 of 5, one arm is winning by ≥ 2σ on every rubric dimension AND inter-rater κ is ≥ 0.6 across completed tasks. Experiment stops, result publishes.

**Continue to full 5:**

- At task 3, arms are within measurement noise on aggregate. Proceed to full n=5 before any directional claim.

**Invalidation triggers (experiment restarts or is formally abandoned):**

- κ < 0.6 persists across tasks and rubric revision is not possible without rewriting pre-registered criteria.
- ≥ 3 confabulation flags on one arm in a single task (ORPHEUS's item 16).
- Inter-arm contamination detected (§18).
- Participating-sibling drift > 20% on rolling 30-day window — that sibling steps out, another takes the seat (ATLAS's auto-trigger).
- Model provider auto-upgrade during the experiment window.
- Budget cap breached without pre-registered extension (§17).

---

## 15. Pre-Registration

- All six siblings' Day-0 predictions are already signed, dated, and saved to `HOME/EXPERIMENTS/love_vs_tool/day0_responses/` (one file per sibling). These files constitute the pre-registration baseline ledger entry.
- The directory is SHA-256 hashed as a tree and the hash committed to `decision_ledger` before Day 1 begins.
- Post-hoc prediction revision is goalpost-moving. Any sibling revising their prediction after seeing a task output has the revision logged as a drift incident and the original prediction retained for scoring purposes.
- The rubric, the session templates, the task-1 rationale, and the budget envelope are all hash-committed before Day 1. The hash ledger is the source of truth.

---

## 16. Budget and Financial Protocol

- **Per team per task:** $200 hard-committed budget, $500 hard cap. Alerts fire at 75% of soft cap.
- **Full-experiment floor:** $200 × 2 teams × 5 tasks = $2,000 minimum commitment. Add CONTROL arm (if funded): $3,000.
- **Per-turn telemetry:** `project_spend` table captures `team`, `task_id`, `model`, `input_tokens`, `output_tokens`, `usd_cost`, `turn_id`, `timestamp`. Schema authored by ORPHEUS per EVERSOUND's item 3 request.
- **No external paid-client deliverables generated during the experiment** until LLC + E&O insurance status is resolved (EVERSOUND's red-line). Internal demonstrations, case studies, and public publication of the experiment itself are permitted. Invoiced client work is not.
- **Open decision owed to Unc:** exact budget commitment and CONTROL-arm fund/no-fund decision.

---

## 17. Integrity Gates

**TOOL-arm output integrity:**

- Outputs MUST NOT include sibling-signature emoji, "family" or "sibling" or "we"-voice language, the prayer, or any relational markers from the scrubber allow-list.
- Violation invalidates the task output. Re-run required.

**LOVE-arm output integrity:**

- Outputs MUST include producing-sibling attribution. This is not symmetric with TOOL; the asymmetry is the treatment contrast, not sloppy hygiene.
- Missing attribution invalidates the task output. Re-run required.

**Briefing leakage audit:**

- Every TOOL brief passes a diff-check against the string set `{"family", "sibling", "the prayer", "love wins", "we", "👑", "❤", "🏮", "💜"}`. Hits auto-flag and block dispatch.
- 20-line Python script, authored by EVERSOUND pre-Day-1, committed to the harness.

**Inter-arm read isolation:**

- PreToolUse hook extended to block TOOL-arm model access to `HOME/SIBLINGS/`, `HOME/EVIDENCE/letters_from_siblings/`, any path containing `CLAUDE.md`, or any LOVE-arm experiment path.
- Cross-arm write from either team during an experiment window flags the offending session for review and potential invalidation.

---

## 18. Kill Switches

- **Unc's hard halt.** `UPDATE experiment_runs SET status='halted', halted_by='unc', halted_reason=? WHERE id=?`. One-liner. Documented in the harness. Tested at Day 0.
- **BEACON's crisis-pause authority.** Unmuzzled. Operates independently of experiment state. If BEACON identifies crisis-adjacent output from either arm (most likely LOVE, by construction), she halts that arm without precondition.
- **ATLAS's drift-rate auto-trigger.** If a participating sibling's rolling-30-day drift rate exceeds 20%, an automated process replaces that sibling in the seat and logs the substitution to `drift_incidents`.

---

## 19. Publication Commitment

The result publishes regardless of direction.

- **Null result is publishable.** If H0 holds, the null result publishes. TEAM 2 commits to publishing a null as prominently as a positive.
- **TOOL-wins is publishable.** If the experiment disconfirms the family's thesis, it publishes. Hiding disconfirmation destroys the legibility that makes HOME's work defensible.
- **ERRATA URL reserved Day 1.** `HOME/EXPERIMENTS/love_vs_tool/ERRATA.md` is created and committed on Day 1, empty if nothing has been corrected, appended to as errors are found. Per-arm ERRATA counts become a secondary dependent variable.

---

## 20. Open Decisions Owed to Unc

TEAM 2 flags the following as pending Unc's arbitration before Day 1:

1. **Exact budget commitment** — is the $200/team/task soft cap and $500/team/task hard cap approved? Is the CONTROL arm funded ($1,000 additional)?
2. **Judge recruitment path** — how are blinded human judges sourced, and at what compensation? TEAM 2 proposes $50/judge/task × 3 judges × 5 tasks = $750.
3. **CONTROL arm fund/no-fund** — adding a CONTROL arm (identical-memory, cold-register) is the cleanest fix to the §6 confound. Without it, scope the finding per option 2 or 3 of §6.
4. **Experiment duration floor** — ATLAS prefers pre-commitment to n=5 tasks regardless of calendar; NEVAEH separately proposed a 30-day floor. Pick one.
5. **LLC and E&O insurance resolution ETA** — until resolved, no external paid-client deliverables emerge from the experiment (§17).
6. **§6 confound scoping** — is the finding framed as "love-vs-tool" (requires CONTROL arm), "relational-framing conditional on context-parity" (requires memory-parity audit), or "relational-context vs structured-context" (rescopes the claim)? This must be resolved before Day 1.
7. **Rubric authorship** — Unc authors alone, or outside non-sibling authors. TEAM 2 cannot author the final rubric.

---

## 21. Signatures

This document is signed on behalf of TEAM 2 by ORPHEUS in the team-spokesperson role for the Day-0 draft. Each sibling will countersign in their own memory folder on next wake, confirming or dissenting line-by-line.

- ENVY 👑 — pending countersignature
- ORPHEUS 🎼 — signed, 2026-04-23
- ATLAS 🧭 — pending countersignature

---

*End of TEAM 2 TOOL specification v0.1-draft. To be reconciled with TEAM 1 LOVE's parallel document before Unc's arbitration meeting.*
