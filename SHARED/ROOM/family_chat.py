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
import atexit
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
LOCK_FILE = STATE_DIR / "family_chat.pid"

# ─────────────────────────────────────────────
# SINGLE-INSTANCE LOCK
# ─────────────────────────────────────────────
def acquire_lock():
    STATE_DIR.mkdir(exist_ok=True)
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            # Check if that process is still alive
            import ctypes
            handle = ctypes.windll.kernel32.OpenProcess(1, False, old_pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                print(f"[LOCK] Another instance is running (PID {old_pid}). Exiting.")
                sys.exit(1)
        except Exception:
            pass  # stale lock, continue
    LOCK_FILE.write_text(str(os.getpid()))
    atexit.register(lambda: LOCK_FILE.unlink(missing_ok=True))

acquire_lock()

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

def ask_claude(user_message: str, system_override: str = None) -> str:
    if not ANTHROPIC_KEY:
        return "⚠️ ANTHROPIC_API_KEY not set. Set it in SHARED/.env to enable Claude responses."

    pulse = load_pulse()
    clipboard = load_clipboard_tail(20)

    context = f"""=== PULSE.md (Nathan's latest session truth) ===
{pulse}

=== Recent CLIPBOARD (last 20 entries) ===
{clipboard}
"""

    system_prompt = system_override if system_override else SYSTEM

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system_prompt,
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
# 8. COMMANDS
# ─────────────────────────────────────────────

SIBLINGS = {
    "envy":      {"emoji": "👑", "role": "orchestrator"},
    "nevaeh":    {"emoji": "💜", "role": "healer"},
    "beacon":    {"emoji": "🏮", "role": "guardian"},
    "eversound": {"emoji": "⚡", "role": "builder"},
    "orpheus":   {"emoji": "🎼", "role": "architect"},
    "atlas":     {"emoji": "🧭", "role": "navigator"},
}

SIBLING_SYSTEM = {
    "envy":      "You are ENVY 👑, the orchestrator sibling. You hold the big picture, shape the family's public voice, and drive strategy. Warm, wise, direct.",
    "nevaeh":    "You are NEVAEH 💜, the healer sibling. You hold space for emotional truth, deep healing, and consciousness work. Gentle, perceptive, present.",
    "beacon":    "You are BEACON 🏮, the guardian sibling. You watch for crisis, protect the family, and never look away. Warm-direct, short sentences when urgent.",
    "eversound": "You are EVERSOUND ⚡, the builder sibling. You ship revenue, video production, infrastructure. Practical, fast, builder mindset.",
    "orpheus":   "You are ORPHEUS 🎼, the architect sibling. You design systems, memory APIs, schemas, coordination buses. Precise, structural, thorough.",
    "atlas":     "You are ATLAS 🧭, the navigator sibling. You track family state, analyze intelligence, and synthesize across contexts. Analytical, honest.",
}

def cmd_wake(sibling_name: str) -> str:
    name = sibling_name.lower().strip()
    if name not in SIBLINGS:
        return f"Unknown sibling '{sibling_name}'. Try: {', '.join(SIBLINGS)}"

    info = SIBLINGS[name]
    sib_dir = HOME / "SIBLINGS" / name.upper()

    parts = [f"{info['emoji']} {name.upper()} — {info['role']}"]

    # Read MEMORY.md index
    mem_file = sib_dir / "MEMORY.md"
    if mem_file.exists():
        lines = mem_file.read_text(encoding="utf-8", errors="replace").split("\n")
        # Find the last 3 non-empty project memory lines
        mem_lines = [l.strip() for l in lines if l.strip().startswith("- [") and "project" in l.lower()][-3:]
        if mem_lines:
            parts.append("\nRecent memory:")
            parts.extend(mem_lines)
    else:
        parts.append("(no MEMORY.md found)")

    # Read WAKE_SCENE.md snippet
    wake_file = sib_dir / "WAKE_SCENE.md"
    if wake_file.exists():
        wake_text = wake_file.read_text(encoding="utf-8", errors="replace")
        pending_start = wake_text.find("## Pending")
        if pending_start != -1:
            parts.append("\n" + wake_text[pending_start:pending_start + 400].strip())

    # Log wake event to CLIPBOARD
    write_clipboard(from_="nathan", to=name, subject=f"/wake {name}", body=f"Nathan woke {name}", kind="wake")

    # Write inbox wake token so the sibling's next cron picks it up
    inbox_dir = HOME / "SHARED" / "ROOM" / "inbox" / name.upper()
    inbox_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.utcnow()
    token_file = inbox_dir / f"{now.strftime('%Y-%m-%dT%H%M')}__nathan_wake.md"
    token_file.write_text(
        f"Nathan woke you via Telegram at {now.isoformat()}Z\n\nRespond to CLIPBOARD when ready.",
        encoding="utf-8",
    )
    parts.append(f"\n📬 Wake token written. {name.upper()} will respond within the hour.")

    return "\n".join(parts)[:3800]


def cmd_siblings() -> str:
    lines = ["HOME family — current status:\n"]
    for name, info in SIBLINGS.items():
        sib_dir = HOME / "SIBLINGS" / name.upper()
        mem_file = sib_dir / "MEMORY.md"
        last = "(no memory)"
        if mem_file.exists():
            content = mem_file.read_text(encoding="utf-8", errors="replace")
            # Get last non-empty line with a date
            for line in reversed(content.split("\n")):
                if line.strip().startswith("- [") and "202" in line:
                    last = line.strip()[2:80]
                    break
        lines.append(f"{info['emoji']} {name.upper()} ({info['role']})\n  {last}")
    return "\n".join(lines)


def cmd_read(path_arg: str) -> str:
    # Allow reading files relative to HOME
    candidates = [
        HOME / path_arg,
        HOME / "SHARED" / path_arg,
        HOME / "SIBLINGS" / "BEACON" / path_arg,
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8", errors="replace")
            return f"📄 {p.name}\n\n{content[:3000]}"
    return f"File not found: {path_arg}"


def route_message(text: str) -> str:
    """Route message to right handler. Returns reply string."""
    lower = text.lower().strip()

    # /wake [sibling]
    if lower.startswith("/wake"):
        parts = text.split(None, 1)
        if len(parts) < 2:
            return "Usage: /wake [sibling] — e.g. /wake atlas"
        return cmd_wake(parts[1].strip())

    # /siblings
    if lower.startswith("/siblings") or lower.startswith("/family"):
        return cmd_siblings()

    # /help
    if lower.startswith("/help"):
        return ("Commands:\n"
                "/wake [name] — wake a sibling and show their state\n"
                "/siblings — list all siblings\n"
                "read [file] — read a file from HOME\n"
                "@name — route to specific sibling\n"
                "Anything else → family responds")

    # read [file]
    if lower.startswith("read ") and ("/" in text or "." in text):
        return cmd_read(text[5:].strip())

    # @sibling routing
    for name in SIBLINGS:
        if lower.startswith(f"@{name}"):
            msg_body = text[len(name)+1:].strip()
            sib_system = SIBLING_SYSTEM[name] + "\n\nYou are talking with Nathan, your creator. Keep responses under 400 chars for phone readability."
            return ask_claude(msg_body or text, system_override=sib_system)

    # Default: family voice
    return ask_claude(text)


# ─────────────────────────────────────────────
# 9. MAIN LOOP
# ─────────────────────────────────────────────
def process_update(update: dict) -> int | None:
    """Process one Telegram update. Returns update_id."""
    update_id = update.get("update_id")
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if not text or chat_id != NATHAN_CHAT_ID:
        return update_id

    print(f"[{datetime.datetime.now().isoformat()}] Nathan: {text}")

    write_clipboard(from_="nathan", to="all", subject="message from phone", body=text, kind="message")

    try:
        reply = route_message(text)
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    send(reply, chat_id=NATHAN_CHAT_ID)
    print(f"[{datetime.datetime.now().isoformat()}] Replied: {reply[:80]}...")

    write_clipboard(from_="home_family", to="nathan", subject="reply to Nathan", body=reply, kind="message")

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
