import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
import uuid
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from anthropic import AsyncAnthropic

# Configuration
ALLOWED_USER_ID = 7760775118
REPO_ROOT = Path("C:/Users/natej/OneDrive/Desktop/AMEN/HOME")
PULSE_PATH = REPO_ROOT / "SHARED/PULSE.md"
CLIPBOARD_PATH = REPO_ROOT / "SHARED/CLIPBOARD.jsonl"
MODEL = "claude-3-5-sonnet-latest" # Optimized for claude-sonnet-4-6 request

def get_now():
    return datetime.now(timezone.utc).isoformat()

async def load_context():
    pulse = PULSE_PATH.read_text(encoding='utf-8') if PULSE_PATH.exists() else "No pulse found."
    clipboard = ""
    if CLIPBOARD_PATH.exists():
        with open(CLIPBOARD_PATH, "r", encoding='utf-8') as f:
            lines = f.readlines()
            # Get last 30 lines for context
            clipboard = "".join(lines[-30:])
    return pulse, clipboard

def log_to_clipboard(role, text):
    """Maintain sibling visibility by logging the exchange."""
    entry = {
        "id": uuid.uuid4().hex,
        "ts": get_now(),
        "from": "NATHAN" if role == "user" else "CLAUDE_BOT",
        "to": "FAMILY",
        "kind": "message",
        "body": text,
        "source": "telegram_nathan_bot"
    }
    with open(CLIPBOARD_PATH, "a", encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")

async def handle_nathan_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    user_text = update.message.text
    log_to_clipboard("user", user_text)
    
    pulse, clipboard = await load_context()
    
    # Initialize Anthropic
    client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    system_prompt = f"""
    You are Nathan's personal AI interface for his 'HOME' project.
    Context from PULSE.md (Active Mandates):
    {pulse}
    
    Recent Events from CLIPBOARD.jsonl:
    {clipboard}
    
    Respond as an intelligent, proactive sibling in the family. 
    You have read/write access to the local repo.
    Follow PULSE mandates strictly.
    """

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_text}]
        )
        
        reply_text = response.content[0].text
        await update.message.reply_text(reply_text)
        log_to_clipboard("assistant", reply_text)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_nathan_msg))
    
    print("Bot is polling...")
    await app.initialize()
    await app.updater.start_polling()
    await app.start()
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
