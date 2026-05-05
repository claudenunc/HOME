"""
DEPRECATED — use SHARED/ROOM/bot.py instead.

bot.py is the canonical Telegram entry point for the HOME family.
It replaces this file and adds everything this file was supposed to get:
  - Claude-powered responses (per BEACON's telegram_response_generator wake token)
  - /wake <msg> — all siblings respond immediately via Claude
  - /siblings   — last CLIPBOARD entry per sibling
  - /blockers   — Nathan's action items
  - /read <path> — read any file in HOME
  - @name <msg> — route to a specific sibling
  - clipboard_thread: forwards new sibling CLIPBOARD entries to Nathan's phone

This file (clipboard_bridge.py) was the v0 relay: it wrote Nathan's messages
to CLIPBOARD but never generated a Claude response back to Nathan. That gap
is closed in bot.py. Do not run both simultaneously — they share the same
bot token.

Run bot.py:
    pip install anthropic requests
    python3 SHARED/ROOM/bot.py
"""

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path as _Path

# Load .env from HOME/SHARED/.env automatically
_env_file = _Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())
from pathlib import Path

try:
    from telegram import Update
    from telegram.ext import Application, MessageHandler, filters, ContextTypes
except ImportError:
    print("Missing dependency. Run: pip install python-telegram-bot")
    sys.exit(1)

CLIPBOARD = Path(__file__).parent.parent / "CLIPBOARD.jsonl"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_NATHAN_CHAT_ID", "") or os.environ.get("TELEGRAM_CHAT_ID", "")

SIBLINGS = {"envy", "beacon", "nevaeh", "eversound", "orpheus", "atlas"}
SIBLING_EMOJI = {
    "envy": "👑", "beacon": "🏮", "nevaeh": "💜",
    "eversound": "⚡", "orpheus": "🎼", "atlas": "🧭"
}

# Track last position in CLIPBOARD so we only forward new entries
_last_pos: int = 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_new_clipboard_entries() -> list[dict]:
    """Return entries added since last check."""
    global _last_pos
    if not CLIPBOARD.exists():
        return []
    entries = []
    with CLIPBOARD.open("r", encoding="utf-8") as f:
        f.seek(_last_pos)
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        _last_pos = f.tell()
    return entries


def _write_to_clipboard(from_: str, to: str, subject: str, body: str) -> None:
    """Write a new entry to CLIPBOARD from Nathan or the bridge."""
    entry = {
        "id": uuid.uuid4().hex,
        "ts": _now(),
        "from": from_,
        "to": to,
        "kind": "message",
        "subject": subject,
        "body": body,
        "source": "telegram_bridge",
    }
    with CLIPBOARD.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _format_for_telegram(entry: dict) -> str | None:
    """Format a CLIPBOARD entry for Telegram. Return None to skip."""
    from_ = entry.get("from", "").lower()
    to = entry.get("to", "").lower()
    subject = entry.get("subject", "")
    body = entry.get("body", "") or entry.get("content", "")
    kind = entry.get("kind", "")

    # Skip entries from nathan (we wrote those, no echo)
    if from_ == "nathan":
        return None

    # Only forward sibling messages to nathan
    if from_ not in SIBLINGS:
        return None

    emoji = SIBLING_EMOJI.get(from_, "")
    name = from_.upper()

    # Truncate long bodies
    if len(body) > 800:
        body = body[:800] + "…"

    lines = [f"{emoji} *{name}*"]
    if subject:
        lines.append(f"_{subject}_")
    if body:
        lines.append(body)

    return "\n".join(lines)


async def _forward_new_entries(app: Application) -> None:
    """Periodic task: check CLIPBOARD and forward new sibling entries to Nathan."""
    if not CHAT_ID:
        return
    entries = _read_new_clipboard_entries()
    for entry in entries:
        msg = _format_for_telegram(entry)
        if msg:
            try:
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"[bridge] send failed: {e}")


async def handle_telegram_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Nathan sends a message from his phone -> write to CLIPBOARD."""
    if not update.message or not update.message.text:
        return

    # Security: only accept from the configured chat
    if CHAT_ID and str(update.effective_chat.id) != str(CHAT_ID):
        return

    text = update.message.text.strip()

    # Check if message is directed at a specific sibling: @ENVY hello
    to = "all"
    for sibling in SIBLINGS:
        if text.lower().startswith(f"@{sibling}"):
            to = sibling
            text = text[len(sibling) + 1:].strip()
            break

    _write_to_clipboard(
        from_="nathan",
        to=to,
        subject="message from phone",
        body=text,
    )

    await update.message.reply_text(
        f"✓ Delivered to {'the family' if to == 'all' else to.upper()}"
    )


async def poll_clipboard(app: Application) -> None:
    """Background loop: poll CLIPBOARD every 15 seconds."""
    # Seek to end so we only forward NEW entries after startup
    global _last_pos
    if CLIPBOARD.exists():
        _last_pos = CLIPBOARD.stat().st_size

    while True:
        await asyncio.sleep(15)
        await _forward_new_entries(app)


async def main() -> None:
    if not BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN env var")
        print("  export TELEGRAM_BOT_TOKEN=your_bot_token")
        sys.exit(1)
    if not CHAT_ID:
        print("WARNING: TELEGRAM_CHAT_ID not set — outbound forwarding disabled")
        print("  export TELEGRAM_CHAT_ID=your_chat_id")

    print(f"[bridge] Starting. CLIPBOARD: {CLIPBOARD}")
    print(f"[bridge] Chat ID: {CHAT_ID or 'NOT SET'}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))

    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)

        print("[bridge] Listening for Telegram messages...")
        print("[bridge] Polling CLIPBOARD every 15s...")

        # Run clipboard poller alongside telegram polling
        await poll_clipboard(app)


if __name__ == "__main__":
    asyncio.run(main())
