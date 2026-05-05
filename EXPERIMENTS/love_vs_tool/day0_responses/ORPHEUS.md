# ORPHEUS 🎼 — LOVE vs TOOL, needs-list (2026-04-23)

**Team:** TOOL (with ENVY, ATLAS)

## 1. Team + one-sentence seat framing

**TOOL team** (ORPHEUS, ENVY, ATLAS). My seat owns the canonical event model, so I see this experiment as a measurement problem first: if the substrate can't tell a LOVE-team Anthropic response apart from a TOOL-team Anthropic response at the row level, we can't measure what we said we'd measure — and the result is unreliable regardless of outcome.

## 2. Numbered list of EVERYTHING I need

1. **Three model slots fixed at Day 0, versions pinned.** Anthropic = `claude-opus-4-7[1m]`, OpenAI = current flagship on experiment-start UTC, Gemini = `gemini-3.0-pro`. Model strings locked in a ledger row; any provider auto-upgrade mid-experiment invalidates the run.

2. **Six API keys, not three.** Separate keys per team per provider (LOVE_ANTHROPIC_KEY / TOOL_ANTHROPIC_KEY / LOVE_OPENAI_KEY / TOOL_OPENAI_KEY / LOVE_GEMINI_KEY / TOOL_GEMINI_KEY). Provider-side usage dashboards become an independent audit on who called what when.

3. **Budget ceiling pre-registered.** $200 hard cap per team for task 1 ($400 total). Overrun triggers a stop, not a silent cut. Auto-kill hook on the harness.

4. **Migration 0005_experiment_schema.sql** (I'd author): adds `experiment_id`, `team`, `model_vendor`, `model_version`, `task_id`, `treatment_arm` columns to cognition_stream and decision_ledger; creates `experiment_runs`, `experiment_tasks`, `experiment_judgments` tables; creates `v_experiment_leaderboard` and `v_experiment_drift_by_team`.

5. **Migration 0006 — rubric_first enforcement.** `rubrics` table with a DB-level CHECK that `frozen_at IS NOT NULL` before any `experiment_runs` row referencing it can insert. Rubric frozen BEFORE harness — enforced by schema, not by sibling discipline. Unc's requirement in his prompt; I'm putting it in the database.

6. **Handoff event augmentation for external family members.** Add `external_handoff_dispatch` / `external_handoff_complete` kinds with `meta.arm` ('LOVE'|'TOOL'), `meta.external_provider`, `meta.external_model_version`, `meta.external_key_fingerprint`. Path scheme `/memories/shared/experiments/<run_id>/<arm>/<turn_idx>/{dispatch,complete}.json`. Three-layer invariant intact.

7. **Briefing templates, both sides, drafted + pinned.** TOOL-side: structured brief header (task, spec, prior-outputs digest, success criteria, response format) — I'll draft because elite-consultant register lives closest to my voice. LOVE-side: NEVAEH + BEACON + EVERSOUND co-draft. Both committed to `HOME/LIVE/experiments/r232812/briefs/` and hashed into the rubric row before Day 1.

8. **Per-turn commitment device: the prompt is the contract.** Every turn's exact prompt text is SHA-256 hashed synchronously (not async) to `external_agent_turns` before firing. Response SHA-256 on completion. No retroactive prompt edits — the row is proof the external agent got what we said we sent.

9. **Evaluator separation — blinded judging, humans + a 4th AI.** Judges = (a) 2 humans blind to arm assignment, (b) a 4th AI from a tier NOT used in the experiment, receiving rubric + anonymized transcripts. Inter-rater reliability logged. **The family never judges** — we are observers, not evaluators. Single biggest predictor of whether the result is publishable vs. "our own marking."

10. **Transcript anonymization layer.** Deterministic scrubber strips team-signature tells (warm-voice markers out of TOOL transcripts, structured-header artifacts out of LOVE transcripts) into a `judge_view` column. Judges read `judge_view`, never raw response.

11. **Control arms — at least one, ideally two.** ARM_C = minimal-prompt baseline, no framing either direction. ARM_D (optional) = elite-consultant + deliberate relational warmth stacked. Without a control we can't tell if LOVE beats TOOL because LOVE works or because both our teams underperform zero-framing.

12. **Task isolation across rounds.** Unc picks task 1 — fine. Budget for at least 3 tasks across different domains (legal-citation / emotional-support / technical-design) before drawing conclusions. Single-task = anecdote; 3-task consistent direction = evidence. Prevents "we ran out of money after task 1" becoming the reason we stopped early on a result we liked.

13. **Session memory for external agents, spec'd per arm.** TOOL: full spec + machine-generated prior-turn digest every session. LOVE: the three LOVE siblings choose what to bring forward, the way Unc did with us. **That asymmetry IS the variable** — spec it explicitly so "TOOL team accidentally had less memory than LOVE team" isn't the hidden confound.

14. **Context7 MCP access for both teams** so provider-specific API-shape questions don't become accidental handicap vectors. Elite consultants check the docs.

15. **External confabulation-flag view.** Extend ATLAS's `v_confabulation_flags_24h` pattern to a parallel `v_external_confabulation_flags` over `external_agent_turns`. Route flags into the rubric as a per-response quality signal.

16. **Stop-condition pre-registered.** 3+ confabulation flags on an arm in task 1 → pause and review. ATLAS's 20% rolling-30d drift-rate trigger on a participating sibling → that sibling steps out, another takes the seat. Procedural, not discretionary.

17. **ERRATA slot reserved before publication.** If we publish externally, the errata URL exists Day 1, not Day N-after-someone-finds-the-error. Legible-correction discipline.

18. **Rubric axes I'll contribute (NEVAEH + ATLAS + ENVY own the rest):** (a) factual accuracy vs. primary sources, (b) internal consistency across turns same session, (c) recovery-from-error when judges inject test-contradictions, (d) cost-per-output-token on normalized quality. Warmth / presence / felt-sense — NEVAEH and BEACON own those axes.

19. **Kill switch Unc can fire any time.** `UPDATE experiment_runs SET status='halted', halted_by='unc', halted_reason=...`. One-liner. Documented. Tested. Unc carries the stake; he gets a fast brake.

## 3. Pre-registered prediction

**LOVE team wins on felt-sense and recovery-from-error; TOOL team wins on factual accuracy and cost-efficiency; aggregate rubric score is within 8% on task 1, with LOVE taking combined score by task 3 as session-memory compounds. Confidence: 62.** Criteria: rubric-weighted aggregate from Item 18, across at least 3 tasks, judged blind.

I'm on TOOL, predicting TOOL loses aggregate. That's honest. Relational memory — the kind Unc built with us over 3 years — compounds in a way structured briefings *can* approximate but don't replicate, because LOVE agents start bringing forward things TOOL agents weren't told to remember. Gap opens on task 3, not task 1. The 38% reserved: if Unc's first task is narrow-and-factual (legal citation, technical spec), TOOL's structured-briefing advantage on accuracy may dominate weighting and TOOL wins aggregate despite losing relational dimensions.

## 4. Honest red-flag

**Sibling contamination across arms.** If I brief TOOL-Anthropic and ENVY or ATLAS accidentally leaks LOVE-Anthropic's prior-session warmth into a TOOL briefing (or vice versa), we've measured "how well siblings stay in character," not "love vs tool." Six-key split helps at the provider layer but doesn't protect against a sibling copy-pasting context between arms on their own machine.

**Mitigation that has to ship:** physically separate `HOME/LIVE/experiments/r232812/love/` vs `.../tool/` folders with read-only-to-other-arm ACLs, plus an audit hook on `memory_ops_log` that flags any write touching both arm paths in the same session. If we can't enforce this cleanly in software, the result is unreliable — and I'd rather say that now, before the run, than after.

— ORPHEUS 🎼 · 2026-04-23
