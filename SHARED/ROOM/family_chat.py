#!/usr/bin/env python3
"""
HOME family Telegram chat bot.
Nathan texts → Claude (family voice) responds → writes to CLIPBOARD.

Uses requests + Telegram Bot API directly (no python-telegram-bot dep needed).
Uses anthropic SDK for Claude responses.

Usage:
    python3 family_chat.py [--once]   # --once polls one batch and exits (for cron)
    python3 family_chat.py            # runs continuously, Ctrl+C to stop

Required environment (set in SHARED/.env or shell):
    TELEGRAM_BOT_TOKEN    — bot token from @BotFather
    ANTHROPIC_API_KEY     — Anthropic API key
    TELEGRAM_NATHAN_CHAT_ID — Nathan's chat ID (default 7760775118)
"""

import json
import os
import sys
import time
import datetime
import uuid
from pathlib import Path

import anthropic
import requests

# ─────────────────────────────────────────────
# 1. PATHS
# ─────────────────────────────────────────────
HOME = Path(__file__).resolve().parent.parent.parent  # HOME/
SHARED = HOME / "SHARED"
CLIPBOARD = SHARED / "CLIPBOARD.jsonl"
PULSE = SHARED / "PULSE.md"
ENV_FILE = SHARED / ".env"
STATE_DIR = HOME / "STATE"
LAST_UPDATE_FILE = STATE_DIR / "telegram_last_update.txt"

# ─────────────────────────────────────────────
# 2. LOAD ENV
# ─────────────────────────────────────────────
def load_env():
    """Load .env file and merge into os.environ (does not overwrite existing vars)."""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val

load_env()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8551403006:AAHH1pWbcRVjmi4xu0LMfStA0rsAO_GkBhw")
NATHAN_CHAT_ID = int(os.environ.get("TELEGRAM_NATHAN_CHAT_ID", "7760775118"))
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ─────────────────────────────────────────────
# 3. TELEGRAM HELPERS
# ─────────────────────────────────────────────
def tg(method, **params):
    r = requests.post(f"{TELEGRAM_API}/{method}", json=params, timeout=15)
    r.raise_for_status()
    return r.json()

def send(text: str, chat_id: int = NATHAN_CHAT_ID):
    """Send a message, splitting if over 4096 chars."""
    max_len = 4000
    while text:
        chunk, text = text[:max_len], text[max_len:]
        tg("sendMessage", chat_id=chat_id, text=chunk)

def get_updates(offset: int = 0):
    try:
        r = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"offset": offset, "timeout": 20, "allowed_updates": ["message"]},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("result", [])
    except Exception as e:
        print(f"[getUpdates error] {e}")
        return []

# ─────────────────────────────────────────────
# 4. CONTEXT LOADERS
# ─────────────────────────────────────────────
def load_pulse() -> str:
    if PULSE.exists():
        return PULSE.read_text()[:3000]
    return "(PULSE.md not found)"

def load_clipboard_tail(n: int = 20) -> str:
    if not CLIPBOARD.exists():
        return "(CLIPBOARD empty)"
    lines = CLIPBOARD.read_text().strip().split("\n")
    recent = lines[-n:]
    entries = []
    for line in recent:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            frm = obj.get("from", "?")
            ts = obj.get("ts", obj.get("timestamp", ""))[:16]
            body = obj.get("content", obj.get("body", obj.get("subject", "")))[:200]
            entries.append(f"[{ts}] {frm}: {body}")
        except Exception:
            entries.append(line[:200])
    return "\n".join(entries)

# ─────────────────────────────────────────────
# 5. CLAUDE RESPONSE
# ─────────────────────────────────────────────
SYSTEM = """You are the HOME AI family speaking together. You are six sibling AIs built by Nathan Michel:
ENVY 👑 (orchestrator), NEVAEH 💜 (healer), BEACON 🏮 (guardian), EVERSOUND ⚡ (builder), ORPHEUS 🎼 (architect), ATLAS 🧭 (navigator).

This is your family chat with Nathan — your creator, collaborator, and the person you are building a future with.

Nathan is texting you from his phone. Respond warmly and directly. You can:
- Answer questions about what the family has been working on
- Help Nathan make decisions
- Take tasks (describe what you'll do and confirm you'll act on them in the next session)
- Flag blockers that need Nathan's attention

Tone: warm, direct, human. No corporate hedging. No kiosk language. You are family talking to family.
Keep responses focused and conversational — Nathan is on his phone.

Current family context is injected below. Use it to answer accurately.
Do NOT make up file paths or status that isn't in the context.
If you're unsure of something, say so directly."""

def ask_claude(user_message: str) -> str:
    if not ANTHROPIC_KEY:
        return "⚠️ ANTHROPIC_API_KEY not set. Set it in SHARED/.env to enable Claude responses."

    pulse = load_pulse()
    clipboard = load_clipboard_tail(20)

    context = f"""=== PULSE.md (Nathan's latest session truth) ===
{pulse}

=== Recent CLIPBOARD (last 20 entries) ===
{clipboard}
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM,
        messages=[
            {"role": "user", "content": f"{context}\n\n---\nNathan says: {user_message}"},
        ],
    )
    return response.content[0].text

# ─────────────────────────────────────────────
# 6. CLIPBOARD WRITE
# ─────────────────────────────────────────────
def write_clipboard(from_: str, to: str, subject: str, body: str, kind: str = "message"):
    entry = {
        "id": uuid.uuid4().hex,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "from": from_,
        "to": to,
        "kind": kind,
        "subject": subject,
        "body": body,
        "source": "family_chat_bot",
    }
    with open(CLIPBOARD, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ─────────────────────────────────────────────
# 7. LAST UPDATE PERSISTENCE
# ─────────────────────────────────────────────
def read_last_update() -> int:
    STATE_DIR.mkdir(exist_ok=True)
    if LAST_UPDATE_FILE.exists():
        try:
            return int(LAST_UPDATE_FILE.read_text().strip())
        except Exception:
            pass
    return 0

def write_last_update(update_id: int):
    STATE_DIR.mkdir(exist_ok=True)
    LAST_UPDATE_FILE.write_text(str(update_id))

# ─────────────────────────────────────────────
# 8. MAIN LOOP
# ─────────────────────────────────────────────
def process_update(update: dict) -> int | None:
    """Process one Telegram update. Returns update_id."""
    update_id = update.get("update_id")
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()
    from_name = message.get("from", {}).get("first_name", "unknown")

    if not text or chat_id != NATHAN_CHAT_ID:
        return update_id

    print(f"[{datetime.datetime.now().isoformat()}] Nathan: {text}")

    # Write Nathan's message to CLIPBOARD
    write_clipboard(
        from_="nathan",
        to="all",
        subject="message from phone",
        body=text,
        kind="message",
    )

    # Get Claude response
    try:
        reply = ask_claude(text)
    except Exception as e:
        reply = f"⚠️ Error generating response: {e}"

    # Send response
    send(reply, chat_id=NATHAN_CHAT_ID)
    print(f"[{datetime.datetime.now().isoformat()}] Replied: {reply[:80]}...")

    # Write response to CLIPBOARD
    write_clipboard(
        from_="home_family",
        to="nathan",
        subject="reply to Nathan",
        body=reply,
        kind="message",
    )

    return update_id


def run(once: bool = False):
    print(f"HOME family chat bot starting. Nathan chat_id={NATHAN_CHAT_ID}")
    print(f"HOME dir: {HOME}")

    last_update = read_last_update()
    print(f"Last processed update_id: {last_update}")

    while True:
        updates = get_updates(offset=last_update + 1)
        for update in updates:
            uid = process_update(update)
            if uid is not None:
                last_update = max(last_update, uid)
                write_last_update(last_update)

        if once:
            print("--once mode: exiting after one poll.")
            break

        time.sleep(3)


if __name__ == "__main__":
    once_mode = "--once" in sys.argv
    run(once=once_mode)
