# GEMINI RESEARCH PROMPT — Anthropic subscription + Claude Code + API: what to use that we're not

*Single-author (ENVY) for speed per Unc's "just give me prompt." Covers six angles from the family's research lanes: guardian / healer / architect / builder / navigator / voice. Paste verbatim into Gemini Deep Research or equivalent.*

---

## 0. CONTEXT FOR GEMINI

You are a senior research analyst producing a deep, citation-grounded intelligence brief for an operator on the **Claude Max** subscription tier (Anthropic, consumer 20x/5x plan) with **Claude Code** installed and active daily use, plus **Claude API** access. The operator's question is simple: *what am I paying for that I'm not using, and what would I use if I knew about it?* Return features, capabilities, skills, and tools that exist as of Q2 2026, grouped by the six research lanes below. For each finding: name the feature exactly as Anthropic documents it, where it's documented (URL), what it does (one sentence), why it matters for a multi-agent "AI family" operator running six named AI personas coordinating on memory + verification + legal-tech work, effort to adopt (minutes / hours / days), and whether it's likely already in use based on the operator's documented workflow (Claude Code daily, Supabase substrate, Telegram bot, hook-based auto-memory, local_agent Windows service, multi-sibling dispatches via Agent tool).

**What this brief is NOT:** marketing recap, "top 10 features" clickbait, or speculation about unreleased products. No vibes.

**What this brief IS:** specific, named, documented capabilities with direct URLs to Anthropic's docs (`docs.anthropic.com`, `docs.claude.com`, `anthropic.com/news`, `anthropic.com/engineering`, Anthropic's GitHub). Cite every finding. Flag confidence: **Verified / Inferred / Unknown** with tight criteria (Verified = primary source with stable link + retrieval date; Inferred = named bridge between two cites; Unknown preferred over Inferred when bridge is more than two hops).

**Audience depth:** high. Operator is technical, builds in Python + TypeScript, runs Windows services and Supabase, uses pgvector, ships Claude Code agents and MCP servers. Err on specificity.

---

## 1. CLAUDE CODE — HOOKS, PERMISSIONS, SAFETY, MONITORING (Guardian lane)

- **All hook types available in Claude Code** (2026) — `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `Notification`, `UserPromptSubmit`, `PreCompact`. For each: exact JSON schema in `settings.json`, example use, real-world patterns.
- **`/security-review` skill** — what it checks, how to invoke, how to wire into pre-commit or CI.
- **`/ultrareview` slash command** — the multi-agent cloud code review capability. Who runs it, what it outputs, billing model.
- **Permission modes** — `allow` / `deny` lists, `settings.local.json` vs `settings.json` scope, `additionalDirectories`, `skipDangerousModePermissionPrompt`. Safety tradeoffs.
- **Audit logging / turn-level telemetry** — any native capability or recommended third-party layer for high-stakes deployment (legal, medical, finance).
- **High-stakes deployment guidance** from Anthropic specifically for regulated industries.
- **Anthropic's Trust & Safety docs** — moderation endpoint, safety classifiers, prompt-injection defenses.

## 2. CLAUDE.AI PROJECTS / ARTIFACTS / MEMORY / LONG CONTEXT (Healer lane)

- **Claude.ai Projects** — what they are, Claude Max limits on project count / size / file knowledge, custom instructions, how they differ from Claude Code's CLAUDE.md workflow.
- **Artifacts** — the side-pane creative surface. Full list of what can be built (apps, docs, SVGs, React, Python, long writing), versioning, sharing/publishing artifacts publicly, recent 2025-2026 additions.
- **Claude Memory tool** (Anthropic API) — official `memory` tool block, what it stores, auto-persistence across conversations, differences from Claude Code's `CLAUDE.md`, how to use it programmatically.
- **Long context — Claude Opus 4.7 with 1M tokens** — what becomes possible that wasn't before. Reading entire books, full codebases, long conversation windows. Cost per call at 1M tokens, when to use vs shorter-context Sonnet/Haiku.
- **Extended thinking / slow mode** — Claude's extended-thinking feature, when to enable, cost implications, how it appears in responses.
- **Claude voice mode / voice input** — web and mobile. Consent model, what's stored, architectural implications for crisis/mental-health-adjacent use.
- **Citations API** — how Claude returns verifiable citations via `citations` block in API responses. Production use cases, limitations.
- **Fast mode (`/fast`)** — Claude Code's fast-output mode on Opus 4.6. Tradeoffs vs Opus 4.7 (1M context).

## 3. CLAUDE API — SKILLS, MCP, AGENT SDK, TOOL USE, BATCH, CACHING (Architect lane)

- **Claude Skills** — `SKILL.md` packaging format, how skills are discovered and loaded, Anthropic-published skills vs user-built, install path, how to fork Anthropic's example skills. Full list of shipped skills.
- **MCP (Model Context Protocol)** — current spec version, how Claude Code and API consume MCP servers, `claude_desktop_config.json` vs `.mcp.json`, OAuth flow, transport types (stdio / SSE / HTTP). List of Anthropic-maintained MCP servers and notable community servers.
- **Claude Agent SDK** — official SDK for building custom Claude-native agents. Language support, capability differences from raw API, where it eats into Claude Code's territory vs complements.
- **Tool Use API** — structured tool calls, parallel tool use, `tool_choice` options, how `memory` / `bash` / `text_editor` / `code_execution` server-side tools work, billing model for server-side tools.
- **Prompt Caching** — cache breakpoints, TTL (5min / 1hr), which message parts cache, cost reduction math (expect 90% read discount), best-practice placement of `cache_control` in system / tools / messages.
- **Batch API** — 50% cost discount for async jobs, 24-hour delivery window, request/response format, limits, use cases for large-scale work.
- **Files API** — PDF / image / text upload, lifetime, citation integration, how multimodal file inputs flow through Claude's context.
- **Computer Use** — current beta status, supported operating systems, safety constraints, real-world deployment examples.

## 4. CLAUDE MAX SUBSCRIPTION + TEAMS + WORKBENCH + ANALYTICS (Builder / P&L lane)

- **Claude Max specifically** (20x / 5x tiers) — exact message/day or token/day limits, Opus access patterns, priority during peak load, rollover behavior, what it includes that Pro doesn't.
- **Claude for Teams / Claude for Enterprise** — features a Max subscriber can't access, pricing thresholds, when it makes sense to upgrade. Shared Projects, admin console, SSO, audit logs.
- **Anthropic Console / Workbench** — web-based prompt-engineering tool. What it does that Claude Code doesn't. Prompt library, evaluation workflows, API key management.
- **Usage and cost analytics** — console-level dashboards, per-model usage, per-org usage. Export to CSV, webhook / API for usage data.
- **Spend caps, org-level limits** — how to enforce a monthly API ceiling, how to alert.
- **Billing models across tiers** — Claude.ai subscription vs API usage-based vs Bedrock vs Vertex. Credit rollovers, prepaid packages, enterprise contracts.
- **Specific features added in Anthropic's 2025-2026 releases** that affect commercial deployment cost structure (caching, batch, smaller models, tool-use billing).

## 5. CLAUDE CODE INTERNALS — SUBAGENTS, SETTINGS, SLASH COMMANDS, COST OPTIMIZATION (Navigator lane)

- **Subagents** — every built-in subagent Claude Code ships (`general-purpose`, `Explore`, `Plan`, `claude-code-guide`, `statusline-setup`, etc.), what each does, when it routes automatically, when to call explicitly. Cost tradeoff vs main-session work.
- **Custom subagents** — `.claude/agents/` directory, how to build one, how the main session discovers them, how `description` field affects auto-routing. Best practices.
- **`settings.json` — every field documented** with safety implications. Hooks, permissions, env, `additionalDirectories`, `alwaysThinkingEnabled`, `enabledPlugins`, IDE integrations, status line customization.
- **Slash commands** — full list of built-in `/*` commands (`/help`, `/clear`, `/compact`, `/model`, `/fast`, `/review`, `/security-review`, `/ultrareview`, `/init`, `/loop`, `/schedule`, etc.). Which are user-triggered vs auto.
- **`/loop` and `/schedule` skills** — recurring and cron-like task scheduling inside Claude Code. Use cases, limits.
- **Cost tracking** — how to see per-turn token usage, per-session cost, session replay. Claude Code's built-in telemetry.
- **IDE integrations** — VS Code, JetBrains, web. Features available per integration, keyboard shortcuts, chord bindings (`~/.claude/keybindings.json`).
- **Token optimization patterns** — specific recommendations from Anthropic engineering blog for reducing cost without reducing capability (smaller models for routing, caching, batch for async, etc.).
- **Inventory of pre-built custom agents the operator may already have in `~/.claude/agents/`** but not be actively using — Anthropic-published reference agents, community agent libraries worth adopting.

## 6. CLAUDE.AI UI + MODEL SELECTION + PUBLISHING / CREATIVE SURFACE (Voice lane)

- **Model selection heuristics** — when to use Opus 4.7 (1M context) vs Sonnet 4.6 vs Haiku 4.5. Latency, cost, capability breakpoints. `/model` command in Claude Code, model-picker in Claude.ai.
- **Artifacts as publishing surface** — can an operator publish an Artifact as a shareable URL? What does the recipient see? Any limits on interactivity.
- **Claude.ai Projects as Content Strategy** — using a Project to hold a book-in-progress, podcast research, long-form writing. File knowledge limits, custom instructions for voice preservation.
- **Claude's writing capabilities 2025-2026** — specific Anthropic-documented patterns for long-form writing, voice consistency, stylistic control.
- **Creative surface integrations** — any Claude.ai connections to Canva, Figma, Notion, Google Drive (per the MCP-ish integrations that exist on web). What's bundled in Max.
- **Voice input / voice mode** — creative use cases (dictating long-form, podcast prep).
- **Publishing long Artifacts** — one-off web apps, writing portfolios, sharable report pages. Cost/hosting implications.

---

## 7. SYNTHESIS — THE OPINIONATED POSITION

After all six sections, answer directly:

**Given an operator on Claude Max + Claude Code + Claude API with an active multi-sibling AI-family architecture, Supabase substrate, Telegram bot, hook-based auto-memory, and daily legal-tech-adjacent work — what are the TOP 10 things they're almost certainly not using but should adopt this week, ranked by leverage?**

For each of the 10:
- Feature name (exact, Anthropic's wording)
- URL to documentation
- What it unlocks
- Estimated hours to adopt
- Estimated cost impact (positive = saves money, negative = spends more)
- Why this specific operator should care given their architecture

Close with: *"Things you should know that I didn't ask"* — everything adjacent I missed (plugins, integrations, upcoming features telegraphed in Anthropic's 2026 releases, community tools worth evaluating).

---

## 8. OUTPUT FORMAT

- Markdown, hierarchical headings matching section numbers.
- Inline citations with URLs.
- Tables for feature comparisons.
- Confidence flag per finding: **Verified / Inferred / Unknown**.
- Date-stamp anything likely to go stale.
- No marketing language.

Begin.
