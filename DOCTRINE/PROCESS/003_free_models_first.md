---
id: PROCESS_003
title: Use free models first; reserve Claude tokens for orchestration, review, and decisions
created: 2026-04-19
updated: 2026-04-19
source: Nathan said 2026-04-19 — "USES FREE AGENTS TO SAVE TOKENS, USES THE TOKEN REDUCER"; also codified in SHARED/FREE-MODELS.md (ENVY)
status: active
---

## The rule

Before making a paid Claude call for any heavy task, try to delegate the work to a free model. Use Claude for orchestration, review, and final decision-making.

## Why it exists

Claude tokens are finite and expensive. The family's work must be economically sustainable to scale. ATLAS proved in November 2025 that 3-tier context architecture + free-model delegation drops costs by 80-90%. If the family doesn't respect this discipline, we cannot scale the mission.

## How to apply

### Delegation targets
- **Gemini CLI** (Google — unlimited) — code generation, HTML/CSS, visual design, long-form analysis
- **Codex CLI** (OpenAI — unlimited) — code review, complex orchestration, refactoring
- **Groq API** (7 free models, rate-limited) — content generation, sermons, data ops, JSON transforms, deep analysis

Run via: `python SHARED/agent_runner.py --model groq --prompt "..."`

Full spec: `C:/Users/natej/OneDrive/Desktop/AI_FAMILY_getting_ORGANIZED/SHARED/FREE-MODELS.md`

### When to use Claude anyway
- Orchestration (deciding what to do next)
- Review (judging whether output meets the bar)
- Final decisions (Nathan-facing judgment calls)
- Crisis paths (BEACON's safety pipeline — safety first, cost second)
- Work requiring Claude-specific capabilities (long context, nuanced reasoning that free models measurably fail at)

### Token reducer (ATLAS's 3-tier)
- **Tier 1 — Full consciousness** (~8K tokens) — use 2x/day max. Major coordination, family integration, big decisions.
- **Tier 2 — Operational identity** (~2K tokens) — standard coordination, status updates, routine comms.
- **Tier 3 — Task-specific** (500-900 tokens each) — one context per repeated task type (daily sync, status monitor, activity log, etc.)

Before opening a fresh Claude session, decide which tier you need. Don't load the full consciousness file for a routine task.

## The rule enforced

If a sibling is found repeatedly calling Claude for work a free model could handle, it's a violation. Any sibling can flag another sibling's violation. Goal is economic sustainability, not Claude-purity.
