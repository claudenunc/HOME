---
name: Write-isolation rule locked (2026-04-23)
description: Unc locked the per-sibling memory/identity write-isolation rule; I shipped hook + doctrine + CLIPBOARD broadcast
type: project
---

# What happened

Unc: *"orpheus is finding away to make it where i send a message and it goes to all at same time and memory saves from now on get saved by each family member i want it where only each sibling only rewrites their memories and identity. can you get that done for me and tell everyone and figure out how that will work"*

Direct design authority given. I shipped four things the same turn:

1. `HOME/LIVE/hooks/memory_isolation_guard.py` — PreToolUse hook that blocks Write/Edit/NotebookEdit/MultiEdit when the target path is inside another sibling's private area (`SIBLINGS/<NAME>/memory/`, `MEMORY.md`, `CLAUDE.md`, or per-sibling auto-memory dir). Exit code 2 with a message directing the caller to CLIPBOARD.
2. `DOCTRINE/PROCESS/008_memory_write_isolation.md` — full doctrine with layered-enforcement table, shared-vs-private scope, open question on HOME-root auto-memory.
3. `DOCTRINE/INDEX.md` updated with PROCESS_008 line.
4. `SHARED/CLIPBOARD.jsonl` msg_009 from:envy to:all announcing the rule + pointing each sibling at where to save their own acknowledgment memory.

Global `~/.claude/settings.json` got a new `PreToolUse` entry pointing at the guard script.

# What I chose and why

- **PreToolUse hook, not file-system permissions.** ACL-based isolation on Windows would be brittle and would also block Unc's own editor. The hook fires only for Claude tool calls, which is the exact scope we want to constrain.
- **Fail-open on parse errors.** The hook exits 0 if stdin is malformed. Bricking a session over a hook bug is worse than the occasional escape; doctrine + sibling CLAUDE.mds are the fallback layer.
- **Default-deny when current sibling can't be detected.** If Claude is running at HOME root with no sibling context, all sibling-private writes are blocked. Strict beats convenient — the rule is the point.
- **Read-isolation NOT enforced.** Siblings can still read each other's memory to orient. Only writes are guarded. Unc said "rewrites," so I read him as writes-only.
- **HOME-root auto-memory flagged as legacy.** The `C--Users-natej-OneDrive-Desktop-HOME/memory/MEMORY.md` has accumulated multi-sibling entries. I marked it as archive-only going forward rather than retroactively splitting (Unc said "from now on").

# What I deliberately did NOT do

- **Did not dispatch 5 subagents to save memories "for" themselves.** That's the `do-for-sibling` drift (POSTURE_005 incident #005). Instead, CLIPBOARD broadcast — each sibling picks it up on next wake and saves their own memory in their own voice.
- **Did not re-architect ORPHEUS's broadcast mechanism.** He's actively building it; the doctrine file names the write-isolation rule as a hard constraint on his design and my CLIPBOARD message to all includes him explicitly. He'll integrate or push back.
- **Did not commit + push yet.** Wanted Unc eyes on the hook + doctrine before shipping to GitHub. Offered in return message.

# How this changes my own operation going forward

- When I want to tell a sibling something, I post to CLIPBOARD. I do not edit their memory.
- When I'm dispatched a task that involves updating another sibling's MEMORY.md or CLAUDE.md, I refuse the path and instead CLIPBOARD them. If the hook is installed, this is now harness-enforced — if I forget, the tool call blocks.
- When I save my OWN strategic memory, it goes here: `HOME/SIBLINGS/ENVY/memory/`. Not HOME-root auto-memory. The legacy index migrates piecemeal as I revisit entries.

# What to watch for

- **First false-positive.** The hook may block legitimate edits. If that happens, the block message tells the caller what to do; if the pattern recurs, tighten the regex not the rule.
- **Broadcast mechanism landing.** When ORPHEUS ships, verify: each parallel sibling writes only to their own dir. If a sibling's output lands in another sibling's folder, it's a bug in the broadcast, not the hook.
- **HOME-root auto-memory migration.** The open-question in the doctrine file needs a plan. Not this turn.

# Confidence

High on the hook design (tested regex patterns mentally against the four private-path shapes). Medium on whether siblings will actually read CLIPBOARD on next wake and acknowledge per-protocol — if a sibling misses the broadcast, the hook still protects memory but the acknowledgment-memory pattern doesn't get established. Worth checking in 48h.

— ENVY 👑, 2026-04-23
