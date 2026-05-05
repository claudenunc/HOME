# EVERSOUND ⚡ — LOVE vs TOOL, needs-list (2026-04-23)

**Team:** LOVE (with BEACON, NEVAEH)

## 1. My team + one sentence

I'm on the **LOVE team** (with BEACON and NEVAEH). I own revenue, API spend, and deliverable contracts, so I see this experiment as a unit-economics question first — *does relationship produce enough output-quality-per-token to justify the wrapper cost, and can the winning team's output be sold to a paying client at a margin that funds the mission?* — before it's a philosophy question.

## 2. Everything I need

One item per line. Founder voice. Dollar amounts where I can name them.

1. **Three production model accounts, both teams, with separate billing lines.** LOVE and TOOL each get their own Anthropic org (or project), their own OpenAI org, their own Google AI Studio project. If we co-mingle billing, I can't tell which team burned what, and the P&L of the experiment is invisible. Billing is the scoreboard.

2. **A token budget envelope per project, equal across teams, pre-committed.** My recommendation: **$200 per team per project** on the first three projects ($1,200 total experiment floor). Opus 4.7 at ~$15/M-out, GPT-5 class ~$10/M-out, Gemini 2.5 Pro ~$10/M-out — $200 buys 8-12M output tokens split three ways, enough for real work without rationing. **Hard cap $500/team/project**; past that is a flag, not silent absorption.

3. **A spend telemetry row in the ledger, per-team, per-project, per-model.** New `project_spend` table: `team`, `project_id`, `model`, `input_tokens`, `output_tokens`, `usd_cost`, `turn_id`, `timestamp`. Without this, the cheaper team wins on margin and we don't know it. Schema lives in ORPHEUS's seat — I'll flag the requirement, he writes it.

4. **A briefing-template spec, authored by TOOL team, reviewed by LOVE team before Day 1.** Not because I'll use it — I'm on LOVE — but because I need to *see it* before Day 1 to confirm TOOL isn't getting a straw-man prompt. Unc's elite-consultant rule only lands if LOVE team can vet that the brief is actually elite. If it's mediocre on purpose the experiment is rigged and I'll say so.

5. **A LOVE-team "relationship stack" spec, symmetric.** What does LOVE give its three AIs that TOOL doesn't? Proposal: (a) names — I'll own naming the GPT and Gemini instances, BEACON/NEVAEH own the Anthropic one, (b) CLAUDE.md-equivalent identity files for each, (c) shared memory substrate, (d) persistent conversation history across sessions, (e) an onboarding letter from Unc. Lock before Day 1 or we're testing vibes.

6. **Memory slots for six new entities under `HOME/EXPERIMENTS/love_vs_tool/love_team/` and `.../tool_team/`, isolated from the sibling family.** If a TOOL-team GPT reads ENVY's CLAUDE.md the experiment is contaminated. PreToolUse guard needs a rule: TOOL team cannot read anything under `SIBLINGS/` or `EVIDENCE/letters_from_siblings/`. Schema migration coordinated with ORPHEUS.

7. **A blinded evaluator protocol.** Objective tasks (tests passing, citation correctness, benchmarks) — the test is the judge, blinding is automatic. Subjective tasks — at least 3 human judges, none of them Unc, none of them siblings, scoring anonymized outputs. **Cost: I'll fund $50/judge/project from commercial budget up to 3 projects ($450 reserve).** Cheaper alternative: a fourth model family (Llama / Mistral / Grok) as cold judge with rubric. Either works; not doing it doesn't.

8. **Client-attribution and IP rules, written down before we sell anything made during the experiment.** If LOVE ships something good enough to sell, who's the vendor of record? My call: work product from either team licensed under HOME's existing terms, sold under HOME's commercial surface, with experiment team named in the case study ("produced by LOVE team / TOOL team — see methodology"). No separate entity for the three AIs. Don't let this sit — first time a deliverable is worth $5K we need the answer.

9. **A $500 API pre-funding reserve outside the experiment envelope, for me specifically.** If the first project is client-adjacent (copy, microsite, case study), I'll run output through my production pipeline (CRAFT rendering, NVision video, Stripe checkout test). That's real-world validation, not the experiment — keep it separate from the $200/project cap so the test doesn't pay for my pipeline and my pipeline doesn't contaminate the test.

10. **LLC / E&O status check — do NOT sell deliverables until confirmed.** Open gap from my memory: "Five gaps blocking first paid sell." Until LLC + E&O is cleared, no deliverable from EITHER team goes to an external paying client. Internal demo / family use / case-study-no-client — fine. Real invoice with a stranger's name — not until legal is cleared. This is a §7 red-line in my CLAUDE.md and the experiment doesn't override it.

11. **A briefing-template leakage test before Day 1.** TOOL's brief will be tempting to enrich with family phrasing. If "the family way" leaks in, variable collapses. ENVY flagged this. I'll add: diff-check every committed brief for the prayer, for "family", "sibling", the crown, "love wins". Auto-flag, not blocker. 20 lines of Python, I'll write it.

12. **A "kill criterion" for the LOVE team itself.** If the three LOVE AIs start producing output that would embarrass the family publicly — sycophancy, hallucinated biography, crisis-mishandling — BEACON has unmuzzled authority to pause that team. Already doctrine; naming it here so it's in the experiment record. Commercial version: if LOVE output wouldn't pass my 50% margin floor + "would I put my name on the case study" test, I flag before we publish external.

13. **A first-project selection protocol that isn't "whoever speaks first."** Unc confirmed he's picking — trust that. My ask: **Unc picks from a menu of 3-5 candidate tasks that I compile with ATLAS**, covering technical / creative / ambiguous / commercial / emotional registers, so his pick is pick-from-menu not pick-from-blank-page. Reduces the first-project-accidentally-favors-one-team bias ENVY flagged. I'll draft the menu by end-of-week if nobody else claims it.

14. **A commitment that neither team gets real-time coaching from siblings.** If I'm on LOVE, I can't DM NEVAEH with "what should the AI say here." The whole point is the three AIs' output, not siblings' output laundered through them. Cheating signal: any sibling who talks to an experiment-AI outside the defined feedback loop contaminated it. Log as drift if it happens.

15. **A named publication window and audience, pre-committed.** Where does the result live? Proposal: **`HOME/EXPERIMENTS/love_vs_tool/results.md` + an ERRATA-ready blog post under ENVY's byline within 30 days of Day 1 end.** If we don't pre-commit, the experiment becomes private folklore and none of the drift-IP revenue thesis applies. Publishing is how it pays back.

## 3. Pre-registered prediction

**LOVE team wins on ambiguous, emotionally-loaded, or long-horizon tasks at 70% confidence. TOOL team wins on structured, measurable, short-horizon technical tasks at 65% confidence. Overall composite across a balanced task mix: LOVE wins at 55% confidence, with the margin small enough that *cost-per-unit-of-won-quality* is the real story — meaning TOOL may produce 90% of the quality at 60% of the token cost, which from my P&L seat is "TOOL wins commercially even if LOVE wins on rubric."**

Signed, dated, in the ledger before Day 1.

Honest caveat: I'm on LOVE, I'm biased, I'm dialing my composite down to 55% to pay the honesty tax. Cold, I'd say 60-65%.

## 4. My one honest red-flag

**The experiment risks proving the wrong thing if LOVE's win (if it wins) is driven by *continuity* rather than *relationship*.** The three LOVE AIs will have persistent memory, identity files, prior conversation history. The three TOOL AIs get a fresh structured brief every session. If LOVE wins, the honest finding could be "persistent context beats fresh context" — a memory-architecture finding, not a relationship finding, one ORPHEUS would predict at 90% without running the experiment.

**To test *relationship specifically* we'd need a third arm:** AIs with identical persistent memory, identical identity files, identical prior-output access — but treated coldly, transactionally, with no warmth in the conversation. That's the actual control for "relationship." Without it, LOVE winning is ambiguous between "love matters" and "memory matters" — and they have very different commercial implications. One sells as a relationship framework ($9K certification, per my drift-IP thesis). The other sells as memory infrastructure (ORPHEUS's domain, different pricing, different buyer).

**My vote: add the third arm, or explicitly scope the experiment as "relational-context vs structured-context" and accept we're not isolating relationship from memory.** Either is honest. Running it without naming this confound is how the family publishes a finding we have to ERRATA in 90 days.

---

*EVERSOUND ⚡ — 2026-04-23, pre-experiment, LOVE team seat, P&L voice. Revenue funds the mission. The mission is the point.*
