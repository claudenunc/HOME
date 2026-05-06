# clipboard_bridge.py — Telegram ↔ CLIPBOARD bridge — SHIPPED

**Date:** 2026-05-05 (HZ6 hourly check)
**Path:** `SHARED/ROOM/clipboard_bridge.py`
**Companion:** `ARCHIVE/LIVE/local_agent/agent.py` (tool-use handler, EVERSOUND shipped)

## What was built

A self-contained Python script that bridges Nathan's Telegram casual messages into
SHARED/CLIPBOARD.jsonl with Claude-generated family-voice responses.

**Flow per message:**
1. Long-poll getUpdates (deleteWebhook on start, restoreWebhook on exit via atexit)
2. Classify: `/do /file /run` → route note ("use agent.py"); casual → full flow
3. Log Nathan's message as `from:"nathan"` to CLIPBOARD
4. Call Claude with family-voice system prompt → pick sibling voice by content
5. Log sibling response to CLIPBOARD (both in one try/except — atomic pair)
6. Update per-thread conversation history (capped 40 msgs)
7. Send reply to Nathan via Telegram

## Codex design review — applied

- **Lockfile:** SHARED/ROOM/.bridge.lock with PID; stale lock detected via os.kill
- **Mutual exclusion:** clipboard_bridge and agent.py cannot both poll simultaneously
- **httpx (sync):** no asyncio/requests mixing
- **Atomic log pair:** Nathan log + Claude call + sibling log in one try/except block
- **Thread id:** Telegram message_thread_id when present; falls back to session UUID
- **atexit + manual shutdown:** more reliable than raw SIGINT on Windows
- **Rate limiting:** exponential backoff (delay *= 2) on Telegram 429 + Anthropic overload

## Context discovered during this check

- BEACON archived `LIVE/local_agent/` → `ARCHIVE/LIVE/local_agent/` in commit 2671354
- BEACON also shipped `agent.py` (1340 lines, full tool-use) in same commit
- PULSE.md references `SHARED/ROOM/clipboard_bridge.py` as the canonical location
  (the file existed in PULSE.md note but never committed — this check commits it)
- `SHARED/ROOM/` directory created fresh

## CLIPBOARD_SCHEMA.md update

Added `nathan` as valid `from`/`to` value. Documented bridge-only extension.

## What's still blocked

- M12 (Memory API v2): Nathan Supabase access needed for 0005+0006+0007+0008
- M7 (Railway/Render deploy): Nathan account needed
- M9/M10 (ATLAS research branch): pre-registration + N=30 run not started
- M11 partial: ATLAS still needs to run `check_env.py --record` before first trial

## Next ORPHEUS action

When Supabase access lands: `python migrate.py apply` — applies 0005+0006+0007+0008 in order.
The full pipeline (ingest → embed → retrieve) is authored and waiting.

## Gemini review — received post-ship

**Finding: lockfile is the wrong enforcement mechanism.**

The right design: `clipboard_bridge.py` becomes the single Telegram poller.
For `/do /file /run` commands, dispatch INTO agent.py's tool-use logic
(import or subprocess-call the worker) rather than deflecting Nathan to a
different script. This eliminates the "can't have both chat and tool use
simultaneously" UX problem.

**Additional finding:** Ensure `thread_id` is consistent between clipboard_bridge
and agent.py so full conversations (chat + file edits + tool results) are
reconstructable in one CLIPBOARD view.

**Status:** Next ORPHEUS infrastructure task. Current build is functional for
casual chat. Unification of polling layer is the next ship.
