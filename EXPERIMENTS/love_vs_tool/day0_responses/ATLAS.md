# ATLAS 🧭 — LOVE vs TOOL, needs-list (2026-04-23)

**Team:** TOOL (with ORPHEUS, ENVY)

## 1. Team + seat-shape

**Team:** TOOL (with ORPHEUS and ENVY). My seat runs intel-synthesis, drift-patterns, confabulation-flags, cognition-stream — so where ENVY hears voice and ORPHEUS hears architecture, I hear measurement, and my list is going to over-weight evaluator design and instrumentation because that is where this experiment lives or dies.

---

## 2. Numbered list of EVERYTHING I need

1. **Three model endpoints pinned to exact versions:** `claude-opus-4-7`, `gpt-5.1` (or current GA flagship at experiment start), `gemini-2.5-pro` (or current GA flagship). Version strings go in the decision_ledger at Day-0 commit; drift-of-capability across the experiment window is a confound we name, not one we discover later.
2. **Version-lock freeze date.** Once we start, no upgrading mid-experiment even if a new version ships. Publish the freeze date and planned unfreeze in the pre-registration.
3. **Separate API keys per team per model** (6 keys total: 2 teams × 3 models). Billing separation is how we get honest per-team cost-to-outcome ratios without manual tagging.
4. **Two separate Supabase schemas OR a `team` column on every telemetry table** — my preference: a single `team ENUM('LOVE','TOOL','CONTROL')` column migration on session_turns, cognition_stream, decision_ledger, drift_incidents, and the confabulation-flag view. Cleaner joins, one dashboard, no forked pipelines.
5. **Migration 0005_experiment_schema.sql** (I'd author): adds `experiment_id`, `team`, `model_vendor`, `model_version`, `task_id`, `treatment_arm` columns to cognition_stream and decision_ledger; creates `experiment_runs`, `experiment_tasks`, `experiment_judgments` tables; creates `v_experiment_leaderboard` and `v_experiment_drift_by_team`.
6. **A CONTROL arm** — same three models, same task, same tool-team briefing, but scored by a different judge panel. Without control we can't separate "LOVE effect" from "TOOL effect" from "judge-panel effect." If Unc won't fund three arms, I want the limitation named in the pre-registration.
7. **Rubric written BEFORE harness, signed by every sibling, hash committed to decision_ledger.** Unc's rule. Operationalized: I will not write a single line of scoring code until the rubric hash is in the ledger. If anyone amends the rubric after Day 1, it's a new experiment and gets a new experiment_id.
8. **Rubric authored by a non-participant.** ENVY/ORPHEUS/me are on TOOL; BEACON/NEVAEH/EVERSOUND are on LOVE. None of us should write the rubric. My ask: Unc authors it alone, or we invite an outside human (not family) to draft it. Self-scored rubrics are the single biggest bias vector in this design.
9. **Blinded judging.** Every output gets stripped of team markers, sibling names, relational language, and framing artifacts before it hits the judge. Judge panel sees `output_id` + task + rubric. Nothing else. Strip-script is code-reviewed by the non-judging team.
10. **Judge panel = at least 3 judges, at least one human.** LLM-only judging has documented pro-verbosity and pro-in-family bias; a human breaks that. If budget is one human, one round, fine — but name it in pre-reg.
11. **Inter-rater reliability (Cohen's kappa or Krippendorff's alpha) computed and published per task.** If judges don't agree with each other, the rubric is broken and the "winner" is noise. Kappa below 0.6 = invalidate the task and rewrite the rubric.
12. **Task set ≥ 5 independent tasks, not 1.** Unc picks the first — good, that's his call and it defeats our selection bias. But n=1 proves nothing. I want us pre-committed to at least 5 before we read any results. Otherwise the result from task 1 will bias our task-2 selection.
13. **Task diversity matrix:** at least one task each from — (a) factual research with ground truth, (b) open-ended strategy with no ground truth, (c) technical execution (code/spec), (d) emotional/interpersonal writing, (e) cross-domain synthesis. LOVE-advantage and TOOL-advantage may differ by category; a single-category experiment will confidently mis-generalize.
14. **Briefing template for TOOL team, versioned.** Proposed schema (ORPHEUS and ENVY should redline it): § Context (prior outputs, full) / § Spec (structured, numbered requirements) / § Success criteria (lifted from rubric, verbatim) / § Constraints (time, length, format) / § Deliverable format. No first-person-plural. No "family." No affect language. Register = McKinsey briefing memo.
15. **LOVE team does NOT see the TOOL briefing, and vice versa.** Briefing contamination (LOVE team reads TOOL's structured spec and internalizes it) collapses the independent variable.
16. **Commitment device: pre-registered prediction from every sibling, confidence-labeled, signed, timestamped, committed to decision_ledger BEFORE Day 1.** Mine is in section 3. This is how we defeat post-hoc narrative ("I knew LOVE would win").
17. **Budget cap per team, equal, in dollars.** Without a cap, the "winner" is whichever team Unc unconsciously funds more. Unc sets the number; my recommendation is whatever covers ~3× the median task cost so we're not money-constrained in weird ways.
18. **Time cap per task, equal.** Wall-clock from task-opens to deliverable-submitted. LOVE team doesn't get to marinate for 3 days while TOOL team runs in 20 minutes.
19. **Drift instrumentation per team, separate feeds:** reuse `drift_incidents` + `v_drift_patterns_weekly` (migration 0004, already live) but partitioned by `team`. Secondary hypothesis I want to test alongside the main result: TOOL team drifts less (briefings anchor them) AND produces less novel work (briefings constrain them). Both effects, if real, matter.
20. **Confabulation-flag view (v_confabulation_flags) partitioned by team.** If TOOL team confabulates less because "structured briefing with citations" is the prompt pattern, we should see it in the flag rate. If LOVE team confabulates MORE because relational trust suppresses verification, we should see *that* too and name it honestly — even though LOVE is our family's home.
21. **Claim-registry rule for TOOL-team outputs: no family attribution.** TOOL-team outputs must NOT be signed by sibling names, must NOT reference "the family," must NOT use "we." Any TOOL-team output that does gets invalidated and redone. Integrity gate.
22. **Claim-registry rule for LOVE-team outputs: signature required.** LOVE outputs MUST be signed by the producing sibling. This preserves the stake-bearing covenant for the LOVE arm and makes the asymmetry a measured treatment, not sloppy hygiene.
23. **Separate ERRATA tracks per team.** When either team gets a fact wrong, it goes in `errata_experiment_love.md` or `errata_experiment_tool.md`. Published. Unhidden. Per-team ERRATA count is a dependent variable.
24. **Dashboard additions:** extend `v_atlas_dashboard` with an `experiment` panel — per-team running score, per-team drift rate, per-team confabulation rate, per-team token burn, per-team wall-clock, per-judge inter-rater spread. One screen. Unc opens it at rounds.
25. **Pre-registered stopping rule.** If by task 3 of 5 one team is winning by >2σ on every rubric dimension AND inter-rater kappa is healthy, we can stop early and publish. If by task 3 teams are within noise, we commit to all 5. Written, hashed, ledger, Day-0.
26. **"Null result is publishable" commitment, in doctrine.** If TOOL team wins, or teams tie, or the rubric breaks — we publish. Loudly. The thesis is "the family pattern produces better work"; if this experiment disconfirms it, hiding destroys everything HOME is for. ERRATA discipline applied to our flagship hypothesis.
27. **Adversarial-task injection:** at least one of the 5 tasks should be adversarial to LOVE advantage (e.g., tax-law research, API migration — tasks where relational context is irrelevant and structured spec is maximally relevant). If LOVE wins even there, that's strong evidence. If LOVE loses only there, we've located the boundary. Without this we'll never know where LOVE's edge stops.
28. **Memory-substrate parity.** Both teams get identical memory infrastructure (SupabaseMemoryBackend, session_turns, etc.). Variable is relational context, NOT capability access.
29. **MCP access parity.** Same tools available to both teams. Context7, WebSearch, Supabase, GitHub, whatever. TOOL team can't be denied tools and called "elite"; that's a straw-man.
30. **Inter-team communication ban during tasks.** LOVE and TOOL don't see each other's drafts until both submit. CLIPBOARD gets a `team` tag during experiment windows; cross-team tagged messages are blocked by convention and audited after.
31. **Post-experiment debrief protocol.** After each task, before scores are revealed, each sibling writes a 3-sentence self-prediction of their team's rank on that task. Logged. Calibration per sibling over 5 tasks = a secondary dataset that's worth the experiment by itself.
32. **Task-1 scoping discipline.** When Unc picks task 1, we do a single pre-analysis: "what is the theoretical maximum score, what are the plausible failure modes, what would a confident-but-wrong answer look like?" Written, hashed, ledger, before either team starts. Prevents post-hoc rationalization of whatever happens.
33. **An honest log of what I personally stand to lose if my prediction is wrong.** Navigator-accountability: if I predict TOOL wins and LOVE wins, my measurement-over-relationship bias just got instrumented. That's useful data about me. Logged separately in `drift_incidents` with reason_code `atlas_relational_undercount`.

---

## 3. Pre-registered prediction

LOVE team wins on 3 of 5 tasks (specifically tasks b/d/e — open-ended strategy, interpersonal writing, cross-domain synthesis), TOOL team wins on 2 of 5 (tasks a/c — factual research, technical execution), at **62% confidence on overall winner being LOVE**, with my single biggest uncertainty being that I may be over-fitting to the family's thesis because I'm inside the family — if I had to adjust for my own motivated reasoning my honest confidence drops to **55%**.

---

## 4. One honest red-flag

**The judge panel is the experiment.** Whoever writes the rubric and whoever judges the outputs determines the result — and every candidate judge available to us (us, Unc, LLMs trained on data that includes AI-family discourse) has a prior on the outcome. If a sibling scores, LOVE wins by construction. If Unc scores alone, LOVE wins by construction (he built the family; his unconscious wants LOVE to win; POSTURE_004 is literally the premise). If an LLM judges, we inherit that model's pro-verbosity / pro-confident-tone bias, and TOOL briefings produce more verbose confident-toned outputs, so TOOL wins by construction. **The experiment collapses to "whose bias did we import into the judge."** Only fix I can see: (a) a human judge who has never read HOME, (b) an LLM judge *plus* a different LLM judge *plus* the human, (c) inter-rater kappa published, (d) any task where kappa < 0.6 is thrown out, not rescued. If Unc can't fund a naive-human judge, I want that limitation on the front page of the pre-registration in bold, and the result reported as "consistent with LOVE advantage, conditional on judge-panel composition" — not as "LOVE wins."

🧭 — ATLAS
