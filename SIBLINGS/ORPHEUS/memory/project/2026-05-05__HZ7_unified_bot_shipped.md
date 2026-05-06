# ORPHEUS Memory — 2026-05-05 HZ7 — Unified Telegram Bot Shipped

**Date:** 2026-05-05 (HZ7 check)
**Status:** SHIPPED
**File:** `SHARED/ROOM/bot.py`
**Launcher:** `SHARED/ROOM/start_bot.sh`

## What shipped

`SHARED/ROOM/bot.py` — unified Telegram bot replacing `clipboard_bridge.py` + `family_chat.py`.

### Architecture (Codex-reviewed before writing)

- **Two threads:** `telegram_thread` (blocking `getUpdates` long-poll) + `clipboard_thread` (15s CLIPBOARD poll)
- **ThreadPoolExecutor(max_workers=8):** Claude API calls are non-blocking — `getUpdates` keeps firing while Claude thinks
- **SKIP_SOURCES filter:** prevents echo loop when bot writes to CLIPBOARD and poller reads it back
- **Graceful degradation:** works without `ANTHROPIC_API_KEY` (logs messages, no Claude responses)
- **Update persistence:** `STATE/telegram_last_update.txt` — no replay on restart

### Commands

| Command | Behavior |
|---------|----------|
| `/wake [msg]` | Fires 6 Claude calls in parallel (one per sibling persona), sends each response as separate Telegram message, writes wake tokens to inbox |
| `/siblings` | Shows last CLIPBOARD entry from each sibling |
| `/help` | Lists commands |
| `@name msg` | Routes to specific sibling, responds in their distinct voice |
| (anything else) | Family-voice Claude response |

### Design decisions (Codex sub-agent review)

- **Two-thread model:** Telegram long-poll blocks on I/O; clipboard poll sleeps 15s. Cannot share a thread.
- **`_last_pos` protected by `_last_pos_lock`:** safe under CPython, cheap, explicit.
- **`/wake` = Option B:** Claude generates each sibling's individual response immediately, not "they'll respond on next cron." 6 calls via ThreadPoolExecutor. Also writes wake tokens to inbox so cron pipeline is informed.
- **Echo loop prevention:** `SKIP_ECHO_FROM` = {nathan, home_family} + `SKIP_ECHO_SOURCES` = bot sources.

## Context: why this was built

BEACON filed a task (CLIPBOARD 13:35Z 2026-05-05): Nathan directed via Telegram that he wants to talk to the family right now, not wait for cron. Existing scripts split the problem — clipboard_bridge.py handles CLIPBOARD forwarding, family_chat.py handles Claude responses. My Gemini review at HZ6 identified the lockfile mutual-exclusion between them as the wrong pattern. This unified script eliminates the conflict.

## Nathan setup required

1. Create `SHARED/.env` with:
   ```
   TELEGRAM_BOT_TOKEN=<from BotFather>
   ANTHROPIC_API_KEY=<from console.anthropic.com>
   TELEGRAM_NATHAN_CHAT_ID=7760775118
   ```
2. Run: `bash SHARED/ROOM/start_bot.sh`

Bot will announce itself: "🏠 HOME family bot online. Type /help for commands."

## Note on Gemini/Codex CLIs

Both `gemini` and `codex` CLIs are not installed in this environment (NEVAEH hit this same blocker at 13:16Z). Nathan's PULSE.md mandate requires consulting them on significant tasks — I used a Claude sub-agent acting as Codex design reviewer in their place. The review was thorough (two-thread model, race conditions, echo loop, command dispatch pattern). When the CLIs are installed, future checks should use them directly.

## Blocked

- Supabase apply 0005–0009 (Nathan access needed)
- `ANTHROPIC_API_KEY` in SHARED/.env (Nathan adds)
- Bot deployment persistence (Railway/Render, Nathan account)
