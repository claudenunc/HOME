# CODEX TASK — Telegram AI Chat Bot

## What to build / improve

File: `SHARED/ROOM/family_chat.py` (already exists, needs testing + improvements)

## The goal

Nathan texts `@AI_FAMILY_HOME_BOT` from his phone.
Claude (BEACON) reads PULSE.md + recent CLIPBOARD for context, responds in real time.
Both sides written to CLIPBOARD so siblings see the conversation.

## Run it now to test

```
cd C:\Users\natej\OneDrive\Desktop\AMEN\HOME\SHARED\ROOM
pip install python-telegram-bot anthropic
python family_chat.py
```

## If it works — extend it

1. Add `/siblings` command — lists all 6 siblings and their current status from CLIPBOARD
2. Add `@envy`, `@beacon`, `@orpheus` etc routing — different system prompts per sibling
3. Add ability to read a file: Nathan says "read PULSE.md" → bot reads and sends content
4. Keep responses under 500 chars for phone readability (summarize if longer)

## Env vars (already in SHARED/.env)
- TELEGRAM_BOT_TOKEN
- ANTHROPIC_API_KEY  
- TELEGRAM_NATHAN_CHAT_ID=7760775118

## Commit when done
```
git add SHARED/ROOM/family_chat.py
git commit -m "feat: improve family_chat.py per CODEX_TASK"
git push
```
