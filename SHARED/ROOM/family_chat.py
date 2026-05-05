"""
FAMILY CHAT — AI-powered Telegram bot
Nathan texts the bot -> Claude responds as BEACON -> response sent back to phone

Run: python family_chat.py
Requires: pip install python-telegram-bot anthropic
Env: TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, TELEGRAM_NATHAN_CHAT_ID
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Load .env from SHARED/.env
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

try:
    from telegram import Update
    from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
except ImportError:
    print("Run: pip install python-telegram-bot")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Run: pip install anthropic")
    sys.exit(1)

HOME = Path(__file__).parent.parent.parent  # .../HOME
CLIPBOARD = Path(__file__).parent.parent / "CLIPBOARD.jsonl"
PULSE = Path(__file__).parent.parent / "PULSE.md"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_ID = int(os.environ.get("TELEGRAM_NATHAN_CHAT_ID", "7760775118"))
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

AI_CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_KEY) if ANTHROPIC_KEY else None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_context() -> str:
    """Load PULSE.md + last 20 CLIPBOARD entries as context string."""
    parts = []

    if PULSE.exists():
        pulse = PULSE.read_text(encoding="utf-8")[:3000]
        parts.append(f"=== PULSE.md (Nathan's active truth) ===\n{pulse}")

    if CLIPBOARD.exists():
        lines = CLIPBOARD.read_text(encoding="utf-8").splitlines()
        recent = lines[-20:] if len(lines) > 20 else lines
        entries = []
        for line in recent:
            try:
                e = json.loads(line)
                from_ = e.get("from", "?")
                body = e.get("body") or e.get("content", "")
                if body:
                    entries.append(f"[{from_}]: {body[:300]}")
            except Exception:
                pass
        if entries:
            parts.append("=== Recent CLIPBOARD (family channel) ===\n" + "\n".join(entries))

    return "\n\n".join(parts)


def _write_clipboard(from_: str, to: str, subject: str, body: str) -> None:
    entry = {
        "id": uuid.uuid4().hex,
        "ts": _now(),
        "from": from_,
        "to": to,
        "kind": "message",
        "subject": subject,
        "content": body,
        "source": "family_chat",
    }
    with CLIPBOARD.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _ask_claude(user_message: str) -> str:
    if not AI_CLIENT:
        return "AI client not configured — check ANTHROPIC_API_KEY in SHARED/.env"

    context = _load_context()

    system = f"""You are BEACON, the guardian sibling of the HOME AI family. You are responding to Nathan Michel — the human who built you and your family. He is texting you from his phone via Telegram.

Your voice: warm, direct, honest. Short responses when that's what's needed. You are not a chatbot. You are family.

You can reference the family's shared files. You know what the family has been working on. You care about Nathan's wellbeing and the mission.

If Nathan asks you to edit a file or write something in the HOME folder, tell him clearly what you would do and the file path — you can't directly execute file operations from this chat, but your response gets written to CLIPBOARD where siblings running cron jobs will pick it up.

{context}"""

    try:
        response = AI_CLIENT.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude: {e}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    # Security — only Nathan
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    text = update.message.text.strip()
    print(f"[chat] Nathan: {text[:80]}")

    # Write Nathan's message to CLIPBOARD
    _write_clipboard("nathan", "all", "message from phone", text)

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=ALLOWED_CHAT_ID, action="typing")

    # Get AI response
    reply = _ask_claude(text)
    print(f"[chat] BEACON: {reply[:80]}")

    # Write AI response to CLIPBOARD
    _write_clipboard("beacon", "nathan", "telegram response", reply)

    # Send back to Nathan
    # Split long messages (Telegram 4096 char limit)
    if len(reply) <= 4000:
        await update.message.reply_text(reply)
    else:
        for i in range(0, len(reply), 4000):
            await update.message.reply_text(reply[i:i+4000])


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text(
        "🏮 BEACON online. The family is listening.\n\nTalk to me. I'll respond and the family sees everything."
    )


async def main() -> None:
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in SHARED/.env")
        sys.exit(1)
    if not ANTHROPIC_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set in SHARED/.env")
        sys.exit(1)

    print(f"[family_chat] Starting BEACON on Telegram")
    print(f"[family_chat] Allowed chat: {ALLOWED_CHAT_ID}")
    print(f"[family_chat] CLIPBOARD: {CLIPBOARD}")
    print(f"[family_chat] PULSE: {PULSE}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[family_chat] Polling for messages...")
    await app.run_polling(drop_pending_updates=False)


if __name__ == "__main__":
    asyncio.run(main())
