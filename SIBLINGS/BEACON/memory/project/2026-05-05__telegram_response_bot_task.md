---
date: 2026-05-05
session: telegram-response-bot
type: project
status: dispatched-to-codex
---

# Task: Telegram AI Response Bot

## What Nathan wants

Nathan texted from his phone:
> "I want to be able to talk to you from here. I want you to respond. I want you to be able to edit files right there in the home folder. Please get this working next."
> "Ask gemini what to do ask somebody what to do have codex do it. We have API keys we have whatever you need get it working"

## What needs to be built

Upgrade `SHARED/ROOM/clipboard_bridge.py` (or write a new `SHARED/ROOM/family_chat.py`) so that when Nathan texts the bot, Claude actually responds — not just "✓ Delivered".

## Architecture (Gemini's advice + my design)

- **Polling mode** — python-telegram-bot v20+, async, no webhook
- **Security** — only accept messages from chat_id `7760775118`
- **Context** — on each message, read `SHARED/PULSE.md` + tail last 20 lines of `SHARED/CLIPBOARD.jsonl`
- **Model** — `claude-sonnet-4-6` via Anthropic API
- **System prompt** — BEACON identity (guardian, family member) + PULSE.md content + recent CLIPBOARD
- **Response** — send Claude's reply back via `bot.send_message(chat_id=7760775118, text=response)`
- **Audit** — append both Nathan's message AND Claude's response to CLIPBOARD.jsonl
- **File editing** — if Nathan says "edit X" or "write Y", Claude should be able to do it (use subprocess to call claude CLI, or direct file operations)

## Key paths

- Bot token: in `SHARED/.env` as `TELEGRAM_BOT_TOKEN` = `8318732806:AAEYub2aRNZHiUe6vul-RY0QEUi6C3IWrTg`
- Anthropic key: in `SHARED/.env` as `ANTHROPIC_API_KEY`
- Nathan chat ID: `7760775118` (also in .env as `TELEGRAM_NATHAN_CHAT_ID`)
- PULSE.md: `SHARED/PULSE.md`
- CLIPBOARD: `SHARED/CLIPBOARD.jsonl`
- Output file: `SHARED/ROOM/family_chat.py` (new file, don't break existing bridge)
- Launcher: `SHARED/ROOM/start_chat.bat`

## Existing bridge reference

`SHARED/ROOM/clipboard_bridge.py` — already handles:
- Polling Telegram for Nathan's messages
- Writing them to CLIPBOARD
- Forwarding sibling CLIPBOARD entries to Telegram
- Currently replies "✓ Delivered" — needs to reply with actual Claude response

## Codex task

Build `SHARED/ROOM/family_chat.py` — a standalone script that:
1. Polls Telegram (bot token from .env)
2. Receives Nathan's message
3. Loads PULSE.md + last 20 CLIPBOARD entries as context
4. Calls claude-sonnet-4-6 with BEACON system prompt + context + Nathan's message
5. Sends response back to Nathan on Telegram
6. Writes Nathan's message + AI response to CLIPBOARD

Also create `SHARED/ROOM/start_chat.bat` launcher.
