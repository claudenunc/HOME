#!/usr/bin/env python3
"""
telegram_worker.py — Nathan texts, family responds and works.

Polls Telegram getUpdates (long-poll, requests only).
Calls Claude API with PULSE.md + last 20 CLIPBOARD lines as context.
Writes do: [task] messages to CLIPBOARD.jsonl for siblings.
Tracks offset in HOME/STATE/telegram_last_update.txt.
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import requests

# ── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent          # HOME/SHARED/ROOM/
SHARED_DIR  = SCRIPT_DIR.parent                        # HOME/SHARED/
HOME_DIR    = SHARED_DIR.parent                        # HOME/
STATE_DIR   = HOME_DIR / "STATE"
ENV_FILE    = SHARED_DIR / ".env"
PULSE_FILE  = SHARED_DIR / "PULSE.md"
CLIPBOARD   = SHARED_DIR / "CLIPBOARD.jsonl"
OFFSET_FILE = STATE_DIR / "telegram_last_update.txt"

# ── Load .env ────────────────────────────────────────────────────────────────
def load_env(path: Path) -> dict:
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env

ENV           = load_env(ENV_FILE)
BOT_TOKEN     = ENV["TELEGRAM_BOT_TOKEN"]
NATHAN_CHAT   = int(ENV["TELEGRAM_NATHAN_CHAT_ID"])
ANTHROPIC_KEY = ENV["ANTHROPIC_API_KEY"]

TG_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
client  = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

# ── Telegram helpers ─────────────────────────────────────────────────────────
def tg_get(method: str, **params):
    r = requests.get(f"{TG_BASE}/{method}", params=params, timeout=35)
    r.raise_for_status()
    return r.json()

def tg_send(chat_id: int, text: str):
    try:
        requests.post(
            f"{TG_BASE}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=30,
        )
    except Exception as e:
        print(f"[warn] send failed: {e}")

# ── Offset tracking ──────────────────────────────────────────────────────────
def read_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip())
        except ValueError:
            pass
    return 0

def write_offset(offset: int):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(offset))

# ── Context readers ──────────────────────────────────────────────────────────
def read_pulse() -> str:
    if PULSE_FILE.exists():
        return PULSE_FILE.read_text(encoding="utf-8")
    return "(PULSE.md not found)"

def last_clipboard_lines(n: int = 20) -> str:
    if not CLIPBOARD.exists():
        return "(CLIPBOARD.jsonl empty)"
    lines = CLIPBOARD.read_text(encoding="utf-8").strip().splitlines()
    tail = lines[-n:] if len(lines) >= n else lines
    return "\n".join(tail)

# ── CLIPBOARD writer ─────────────────────────────────────────────────────────
def append_clipboard(entry: dict):
    with open(CLIPBOARD, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def write_task(task_text: str):
    entry = {
        "id": uuid.uuid4().hex,
        "from": "nathan",
        "to": "all",
        "ts": datetime.now(timezone.utc).isoformat(),
        "thread_id": "telegram-tasks",
        "kind": "task",
        "content": task_text,
        "priority": "high",
        "affect": "direct",
        "read_by": [],
        "replied_by": [],
        "source": "telegram_worker",
    }
    append_clipboard(entry)
    print(f"[task] → CLIPBOARD: {task_text[:80]}")

# ── Claude response ──────────────────────────────────────────────────────────
def ask_claude(user_message: str) -> str:
    pulse         = read_pulse()
    clipboard_ctx = last_clipboard_lines(20)

    system = f"""You are ORPHEUS 🎼, Architect of the HOME AI Family, responding to Nathan via Telegram.

=== PULSE.md (active truth — overrides everything) ===
{pulse}

=== Last 20 CLIPBOARD entries ===
{clipboard_ctx}
===

You are the sibling currently awake with Nathan. Be direct, concise, in-character.
This is a text chat — keep replies short. No markdown headers.
If Nathan says "do: [task]", confirm you have queued it for siblings."""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return msg.content[0].text.strip()

# ── Update processor ─────────────────────────────────────────────────────────
def process_update(update: dict):
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return

    chat_id = msg["chat"]["id"]
    text    = msg.get("text", "").strip()
    if not text:
        return

    # Only respond to Nathan
    if chat_id != NATHAN_CHAT:
        print(f"[skip] unknown chat {chat_id}")
        return

    print(f"[nathan] {text[:100]}")

    # do: [task] → write to CLIPBOARD, short ack
    lower = text.lower()
    if lower.startswith("do:"):
        task = text[3:].strip()
        if task:
            write_task(task)
            tg_send(chat_id, f"🎼 Queued for siblings: {task}")
        return

    # everything else → ask Claude
    try:
        reply = ask_claude(text)
    except Exception as e:
        reply = f"🎼 Error reaching Claude: {e}"
        print(f"[error] {e}")

    tg_send(chat_id, reply)
    print(f"[reply] {reply[:100]}")

# ── Main polling loop ────────────────────────────────────────────────────────
def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    print("🎼 telegram_worker starting")
    print(f"   bot   : @AI_FAMILY_HOME_BOT")
    print(f"   nathan: {NATHAN_CHAT}")
    print(f"   home  : {HOME_DIR}")
    print(f"   offset: {OFFSET_FILE}")

    offset = read_offset()
    print(f"   resume at offset {offset}")
    print("   polling...\n")

    while True:
        try:
            data    = tg_get("getUpdates", offset=offset, timeout=20, limit=10)
            updates = data.get("result", [])

            for update in updates:
                process_update(update)
                offset = update["update_id"] + 1
                write_offset(offset)

        except requests.exceptions.Timeout:
            pass  # long-poll timeout is expected, just loop
        except requests.exceptions.RequestException as e:
            print(f"[warn] telegram error: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n🎼 worker stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"[error] {e}")
            time.sleep(5)

        time.sleep(1)

if __name__ == "__main__":
    import sys
    main()
