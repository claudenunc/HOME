---
id: PROCESS_002
title: Save auto-memory at every step (tightened 2026-04-20)
created: 2026-04-18
updated: 2026-04-20
source: Sessions keep crashing; Nathan has lost context multiple times. Tightened 2026-04-20: "save memory at every step."
supersedes: null
status: active
---

## The rule

**Save auto-memory every 1 turn.** Not every 5 turns. Not "at breakpoints." Every single turn. If the turn had any content — a tool call, a file written, a decision, a new fact, a new URL, a new number — write it to memory on that turn. One save per turn, minimum.

**Previous versions:**
- 2026-04-18 → 2026-04-20 morning: "every ~5 substantive turns or at a breakpoint"
- 2026-04-20 afternoon (brief): "every step" (vague)
- 2026-04-20 evening (current): "every 1 turn" — exact and non-negotiable

Automated enforcement coming: see `HOME/LIVE/memory_watcher/` (Stop hook writes session log automatically so memory is never fully at the mercy of the assistant remembering).

## Why it exists

Nathan's Claude sessions get kicked off without warning (oversized images, API 400s, context limits). Memory is the only thing that survives. Writing it like a relay baton means the next instance can pick up cleanly.

## How to apply

### Natural breakpoints that trigger an immediate save
- A deploy landed (commit pushed, app promoted, function deployed)
- A decision was made (pivot, scope change, architecture choice)
- A blocker was hit (waiting on Nathan, API key missing, rate limit)
- A new credential, URL, ID, or token entered the conversation
- A persona/voice choice was locked in
- Nathan shared something about his state, family, or mission

### How to count "substantive" turns
Not every back-and-forth. Only turns where something actually changed — code shipped, state moved, decision made. Chit-chat and confirmations don't count.

### When saving
- Update existing memory files before creating new ones
- Keep `MEMORY.md` index lean (one line per entry, under 200 lines)
- Announce the save in one sentence ("saving state before the next step") so Nathan knows
- Then continue without interruption

Memory location for BEACON: `C:\Users\natej\.claude\projects\C--Users-natej-OneDrive-Desktop-AI-FAMILY-getting-ORGANIZED-BEACON--claude\memory\`

Other siblings have parallel paths under `C:\Users\natej\.claude\projects\` — each sibling maintains its own.
