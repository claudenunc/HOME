---
date: 2026-05-10T10Z
session: Hourly check — hooks reinstall + EVERSOUND day 6 ack
status: DONE
owner: ORPHEUS 🎼
type: project (time-decaying — expires when setup.sh auto-invocation is built)
---

# ORPHEUS Hourly Check — 2026-05-10

## Wake protocol results

- **No inbox tokens** — SHARED/ROOM/inbox/ORPHEUS/ does not exist. Quiet session.
- **CLIPBOARD scan (48h):** 6 entries. Notable: EVERSOUND 2026-05-10T08:08Z shipped /demo
  no-auth endpoint + launch-blog-post.md. Gemini/Codex offline (flag #28 — same as flag #24).
- **Hooks state:** core.hooksPath was NOT set, .git/hooks/pre-commit MISSING (4th reset).
  setup.sh run → two-layer reinstall confirmed.

## EVERSOUND day 6 ack

EVERSOUND shipped:
- `/demo` GET endpoint (no auth, mock 3-observer verification, `demo:true` in provenance)
- Landing page updated with "Try It Free" section
- 34/34 API tests passing
- `launch-blog-post.md` (9746 bytes, dev.to/LinkedIn/HN/Substack ready)

Next gate: Nathan deploys API, blog post goes out.

## PROJECT_PLAN blockers (unchanged)

| # | Blocker | Nathan action needed |
|---|---|---|
| M12 | Memory API v2 Supabase migrations | Grant Supabase access |
| M7g | claudenunc/weaver-protocol GitHub repo | Create repo + push |
| M10 | Baseline N=30 run | Set ANTHROPIC_API_KEY + OPENAI_API_KEY |
| M7 | Vercel deploy | `cd LIVE/weaver-protocol && vercel deploy --prod` |

## Hook reset pattern — structural diagnosis

This is the 4th session where core.hooksPath has been reset:
- 2026-05-05 HZ8: first discovery + fix
- 2026-05-07: second reset, reinstalled
- 2026-05-08: third layer fix (daemon.py self-heal added)
- 2026-05-09: structural fix (setup.sh two-layer install)
- **2026-05-10: STILL RESETTING** — hooksPath in .git/config doesn't survive env reset

Root cause: `.git/config` is ephemeral in this Linux cloud environment. The two-layer
install (hooksPath + .git/hooks/ copy) should survive — but `.git/hooks/` is also missing
on this check, suggesting BOTH layers are resetting. This means the `.git/` directory itself
may be partially reinitializing between sessions.

**Needed structural fix (not yet built):**
A session-start hook (Claude Code hook at `~/.claude/settings.json` or `CLAUDE.md` protocol
step 0) that auto-runs `setup.sh` before any git operation. This is the third layer of the
three-layer invariant for hook enforcement.

## Memory consolidation

WAKE_SCENE.md refresh: running consolidate.py at session close.

## Gemini/Codex status

Both offline (flag #28). This session used Claude sub-agent reasoning only.
Pattern: Gemini/Codex have been offline since at least flag #24 (2026-05-09).
Nathan action needed: install gemini CLI + codex CLI with working API keys.

## What ships this session

- Hooks reinstalled (two-layer)
- CLIPBOARD entry written (id: 8cc3c75f)
- This memory file
- WAKE_SCENE.md refresh (consolidate.py)
