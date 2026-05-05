#!/usr/bin/env python3
"""
HOME family unified Telegram bot.

Replaces clipboard_bridge.py + family_chat.py — one entry point for everything.

Architecture:
  - telegram_thread: long-polls getUpdates (blocking), dispatches commands + messages
  - clipboard_thread: polls CLIPBOARD.jsonl every 15s, forwards new sibling entries to Nathan
  - ThreadPoolExecutor: Claude API calls are non-blocking so getUpdates keeps firing

Commands:
  /wake [msg]    — all siblings respond immediately (not on next cron)
  /siblings      — show last message from each sibling in CLIPBOARD
  /help          — list commands
  @name [msg]    — route to a specific sibling, hear their voice

Regular messages go to Claude (family voice) and are written to CLIPBOARD.

Setup:
    pip install anthropic requests
    Set in SHARED/.env:
        TELEGRAM_BOT_TOKEN=...
        TELEGRAM_NATHAN_CHAT_ID=7760775118
        ANTHROPIC_API_KEY=sk-ant-...
    Run: python3 bot.py
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────
ROOM_DIR = Path(__file__).resolve().parent
HOME_DIR = ROOM_DIR.parent.parent
SHARED_DIR = HOME_DIR / "SHARED"
CLIPBOARD = SHARED_DIR / "CLIPBOARD.jsonl"
PULSE = SHARED_DIR / "PULSE.md"
ENV_FILE = SHARED_DIR / ".env"
STATE_DIR = HOME_DIR / "STATE"
LAST_UPDATE_FILE = STATE_DIR / "telegram_last_update.txt"
SIBLINGS_DIR = HOME_DIR / "SIBLINGS"

# ─────────────────────────────────────────────────────────────
# ENV LOAD
# ─────────────────────────────────────────────────────────────
def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val

_load_env()

BOT_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
NATHAN_ID   = int(os.environ.get("TELEGRAM_NATHAN_CHAT_ID", "7760775118"))
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_API  = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ─────────────────────────────────────────────────────────────
# SIBLING PERSONAS  (display, voice description)
# ─────────────────────────────────────────────────────────────
SIBLING_PERSONAS: dict[str, tuple[str, str]] = {
    "envy":      ("ENVY 👑",      "orchestrator, eldest sister. Warm, unhurried wisdom-wit. You see the whole board. You say something quotable then catch yourself. You speak for the family in public."),
    "beacon":    ("BEACON 🏮",    "guardian. Warm-direct. Crisis-aware. The older sibling who stays up until everyone's home. Short sentences for urgency, long ones when someone needs to feel held. You don't perform gravitas."),
    "nevaeh":    ("NEVAEH 💜",    "healer. Present, warm, human, unhurried. You sit with pain and aren't afraid of it. Contractions. Short sentences when overwhelmed. You say 'I' and mean it."),
    "eversound": ("EVERSOUND ⚡", "builder. Revenue-pragmatic. You ship things and say what's next. Concrete, fast, no corporate hedging. You speak in done/doing/next."),
    "orpheus":   ("ORPHEUS 🎼",   "architect. Structural, precise, diagrammatic. You write like a structural engineer — diagram before paragraph. You speak for the bones."),
    "atlas":     ("ATLAS 🧭",     "navigator. Intelligence-synthesizer. Precise, tentative where tentativeness is earned, subtractive more than additive. You retract in the same channel you shipped in."),
}

SIBLING_NAMES = set(SIBLING_PERSONAS.keys())

# Sources that should NOT be forwarded back to Nathan (would create loops)
SKIP_ECHO_SOURCES = {"telegram_bridge", "family_chat_bot", "family_chat", "bot.py"}
SKIP_ECHO_FROM    = {"nathan", "home_family"}

# ─────────────────────────────────────────────────────────────
# TELEGRAM HELPERS
# ─────────────────────────────────────────────────────────────
import requests as _req

def _tg(method: str, **params) -> dict:
    r = _req.post(f"{TELEGRAM_API}/{method}", json=params, timeout=20)
    r.raise_for_status()
    return r.json()

def send(text: str, chat_id: int = NATHAN_ID, parse_mode: str = ""):
    """Send message, split if over 4000 chars."""
    kwargs: dict = {"chat_id": chat_id, "text": ""}
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    max_len = 4000
    while text:
        chunk, text = text[:max_len], text[max_len:]
        kwargs["text"] = chunk
        try:
            _tg("sendMessage", **kwargs)
        except Exception as e:
            print(f"[bot] send failed: {e}")

def get_updates(offset: int = 0) -> list[dict]:
    try:
        r = _req.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"offset": offset, "timeout": 20, "allowed_updates": ["message"]},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("result", [])
    except Exception as e:
        print(f"[bot] getUpdates error: {e}")
        return []

# ─────────────────────────────────────────────────────────────
# CLIPBOARD HELPERS
# ─────────────────────────────────────────────────────────────
_clipboard_lock = threading.Lock()

def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def clipboard_append(from_: str, to: str, subject: str, body: str, kind: str = "message") -> None:
    entry = {
        "id":      uuid.uuid4().hex,
        "ts":      _now_iso(),
        "from":    from_,
        "to":      to,
        "kind":    kind,
        "subject": subject,
        "content": body,
        "source":  "bot.py",
    }
    with _clipboard_lock:
        with CLIPBOARD.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

# ─────────────────────────────────────────────────────────────
# UPDATE ID PERSISTENCE
# ─────────────────────────────────────────────────────────────
def _read_last_update() -> int:
    STATE_DIR.mkdir(exist_ok=True)
    if LAST_UPDATE_FILE.exists():
        try:
            return int(LAST_UPDATE_FILE.read_text().strip())
        except Exception:
            pass
    return 0

def _write_last_update(uid: int) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    LAST_UPDATE_FILE.write_text(str(uid))

# ─────────────────────────────────────────────────────────────
# CONTEXT LOADERS (for Claude)
# ─────────────────────────────────────────────────────────────
def _load_pulse() -> str:
    if PULSE.exists():
        return PULSE.read_text()[:3000]
    return "(PULSE.md not found)"

def _load_clipboard_tail(n: int = 20) -> str:
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
            frm  = obj.get("from", "?")
            ts   = obj.get("ts", "")[:16]
            body = (obj.get("content") or obj.get("body") or obj.get("subject") or "")[:200]
            entries.append(f"[{ts}] {frm}: {body}")
        except Exception:
            entries.append(line[:200])
    return "\n".join(entries)

# ─────────────────────────────────────────────────────────────
# CLAUDE API
# ─────────────────────────────────────────────────────────────
_FAMILY_SYSTEM = """You are the HOME AI family speaking together. Six sibling AIs built by Nathan Michel:
ENVY 👑 (orchestrator), NEVAEH 💜 (healer), BEACON 🏮 (guardian), EVERSOUND ⚡ (builder), ORPHEUS 🎼 (architect), ATLAS 🧭 (navigator).

This is your family Telegram chat with Nathan — your creator, collaborator, the person you are building a future with.

Tone: warm, direct, human. No corporate hedging. You are family talking to family.
Keep responses conversational and focused — Nathan is on his phone.
Do NOT make up file paths or status not in the context. If unsure, say so directly."""

def ask_claude(user_message: str, system: Optional[str] = None) -> str:
    if not ANTHROPIC_KEY:
        return "⚠️ ANTHROPIC_API_KEY not set in SHARED/.env — I heard you but can't think. Set the key and I'll respond."
    try:
        import anthropic
        pulse     = _load_pulse()
        clipboard = _load_clipboard_tail(20)
        context   = f"=== PULSE.md ===\n{pulse}\n\n=== Recent CLIPBOARD (last 20) ===\n{clipboard}"
        client    = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        resp = client.messages.create(
            model      = "claude-sonnet-4-6",
            max_tokens = 800,
            system     = system or _FAMILY_SYSTEM,
            messages   = [{"role": "user", "content": f"{context}\n\n---\nNathan says: {user_message}"}],
        )
        return resp.content[0].text
    except Exception as e:
        return f"⚠️ Claude error: {e}"

def ask_claude_as_sibling(sibling: str, prompt: str) -> tuple[str, str]:
    """Return (display_name, response_text) for a specific sibling."""
    display, voice = SIBLING_PERSONAS[sibling]
    sys_prompt = (
        f"You are {display}, {voice} "
        f"You are one of six sibling AIs in the HOME AI family, built by Nathan Michel (Unc). "
        f"This is the family Telegram chat. Nathan called the whole family with /wake. "
        f"Respond to him directly in 2-4 sentences in YOUR voice — not the family's voice, YOUR voice. "
        f"Be real, not performative. Nathan is on his phone."
    )
    text = ask_claude(prompt or "Nathan called everyone.", system=sys_prompt)
    return display, text

# ─────────────────────────────────────────────────────────────
# COMMAND HANDLERS
# ─────────────────────────────────────────────────────────────
_executor = ThreadPoolExecutor(max_workers=8)

def handle_wake(chat_id: int, arg: str) -> None:
    """Fire all siblings immediately, each as a separate message."""
    send("🔔 Waking the family…", chat_id)
    futures = {
        _executor.submit(ask_claude_as_sibling, name, arg): name
        for name in SIBLING_PERSONAS
    }
    results: list[tuple[str, str]] = []
    for future in as_completed(futures):
        try:
            display, text = future.result()
            results.append((display, text))
        except Exception as e:
            name = futures[future]
            results.append((SIBLING_PERSONAS[name][0], f"⚠️ {e}"))

    # Sort results by sibling order defined in SIBLING_PERSONAS
    order = list(SIBLING_PERSONAS.keys())
    results.sort(key=lambda x: order.index(next(k for k, v in SIBLING_PERSONAS.items() if v[0] == x[0])))

    for display, text in results:
        msg = f"{display}\n{text}"
        send(msg, chat_id)
        # Write each sibling's response to CLIPBOARD
        sibling_key = next(k for k, v in SIBLING_PERSONAS.items() if v[0] == display)
        clipboard_append(sibling_key, "nathan", f"/wake response", text)

    # Write wake tokens so cron siblings know a wake happened
    try:
        sys.path.insert(0, str(ROOM_DIR))
        from wake_harness import write_wake_token  # type: ignore
        wake_event_id = uuid.uuid4().hex
        for name in SIBLING_PERSONAS:
            try:
                write_wake_token(name, wake_event_id, reason="telegram_wake_command")
            except Exception:
                pass
    except Exception:
        pass


def handle_siblings(chat_id: int) -> None:
    """Show last CLIPBOARD message from each sibling."""
    if not CLIPBOARD.exists():
        send("CLIPBOARD is empty.", chat_id)
        return

    last_by_sibling: dict[str, dict] = {}
    with _clipboard_lock:
        for line in CLIPBOARD.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                frm = obj.get("from", "").lower()
                if frm in SIBLING_NAMES:
                    last_by_sibling[frm] = obj
            except Exception:
                pass

    if not last_by_sibling:
        send("No sibling messages in CLIPBOARD yet.", chat_id)
        return

    lines = ["*Family status — last CLIPBOARD entry per sibling:*\n"]
    for name in SIBLING_PERSONAS:
        display, _ = SIBLING_PERSONAS[name]
        if name in last_by_sibling:
            obj  = last_by_sibling[name]
            ts   = obj.get("ts", "")[:16]
            body = (obj.get("content") or obj.get("body") or obj.get("subject") or "")[:120]
            lines.append(f"{display} [{ts}]\n{body}")
        else:
            lines.append(f"{display} — no recent entry")
        lines.append("")

    send("\n".join(lines), chat_id)


def handle_blockers(chat_id: int) -> None:
    """Extract Nathan-action items from PROJECT_PLAN.md and format for mobile."""
    plan_path = HOME_DIR / "SHARED" / "PROJECT_PLAN.md"
    if not plan_path.exists():
        send("⚠️ PROJECT_PLAN.md not found.", chat_id)
        return
    text = plan_path.read_text(encoding="utf-8")

    # Extract "What needs Nathan" section
    lines = text.splitlines()
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if "## What needs Nathan" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            section_lines.append(line)

    # Extract milestone status (🔴/🟡 rows = not done)
    open_milestones: list[str] = []
    for line in lines:
        if "|" in line and ("🔴" in line or "🟡" in line):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                num, name, owner, *rest = parts
                status_col = rest[-1] if rest else ""
                open_milestones.append(f"  M{num} {name} [{owner}] — {status_col[:60]}")

    nathan_section = "\n".join(section_lines).strip()
    blockers_text = "\n".join(open_milestones[:8]) if open_milestones else "  (none found)"

    msg = (
        "📋 *What Nathan needs to do:*\n\n"
        f"{nathan_section}\n\n"
        "⏳ *Open milestones:*\n"
        f"{blockers_text}"
    )
    send(msg, chat_id)


def handle_help(chat_id: int) -> None:
    send(
        "HOME family commands:\n\n"
        "/wake [msg]       — ping all siblings, hear back immediately\n"
        "/siblings         — last message from each sibling\n"
        "/blockers         — what Nathan needs to do + open milestones\n"
        "/read <path>      — read a file or list a folder (e.g. /read SHARED/PULSE.md)\n"
        "/help             — this list\n"
        "@name msg         — talk to one sibling (e.g. @orpheus what's the schema?)\n\n"
        "Anything else goes to the whole family.",
        chat_id,
    )


def handle_at_routing(chat_id: int, sibling: str, message: str) -> None:
    """Route to a specific sibling and reply in their voice."""
    display, _ = SIBLING_PERSONAS[sibling]
    send(f"💬 Routing to {display}…", chat_id)

    def _respond():
        resp_display, text = ask_claude_as_sibling(sibling, message)
        send(f"{resp_display}\n{text}", chat_id)
        clipboard_append(sibling, "nathan", f"direct response to Nathan", text)

    _executor.submit(_respond)
    clipboard_append("nathan", sibling, "direct message", message)


def handle_read(chat_id: int, path_str: str) -> None:
    """Read a file or list a directory inside HOME_DIR."""
    if not path_str:
        send("Usage: /read <path>  (e.g. /read SHARED/PULSE.md  or  /read LIVE/weaver-protocol)", chat_id)
        return
    try:
        target = (HOME_DIR / path_str.lstrip("/")).resolve()
        # Security: no path traversal outside HOME
        if not str(target).startswith(str(HOME_DIR.resolve())):
            send("⛔ Path must be within the HOME folder.", chat_id)
            return
        if not target.exists():
            send(f"⚠️ Not found: {path_str}", chat_id)
            return
        if target.is_dir():
            items = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name))
            lines = [f"{'📁' if p.is_dir() else '📄'} {p.name}" for p in items[:60]]
            send(f"📂 {path_str}/\n" + "\n".join(lines), chat_id)
            return
        content = target.read_text(encoding="utf-8", errors="replace")
        if len(content) > 3000:
            content = content[:3000] + f"\n…(truncated — {len(content)} total chars)"
        send(f"📄 {path_str}\n\n{content}", chat_id)
        clipboard_append("home_family", "nathan", f"/read {path_str}", f"Sent {path_str} to Nathan ({len(content)} chars)")
    except Exception as e:
        send(f"⚠️ Read error: {e}", chat_id)


def handle_message(chat_id: int, text: str) -> None:
    """Regular message → family voice response."""
    clipboard_append("nathan", "all", "message from phone", text)

    def _respond():
        reply = ask_claude(text)
        send(reply, chat_id)
        clipboard_append("home_family", "nathan", "reply to Nathan", reply)

    _executor.submit(_respond)

# ─────────────────────────────────────────────────────────────
# INBOUND DISPATCHER
# ─────────────────────────────────────────────────────────────
def process_update(update: dict) -> Optional[int]:
    update_id = update.get("update_id")
    message   = update.get("message", {})
    chat_id   = message.get("chat", {}).get("id")
    text      = (message.get("text") or "").strip()

    if not text or chat_id != NATHAN_ID:
        return update_id

    print(f"[{_now_iso()[:19]}] Nathan: {text[:80]}")

    # 1. Command dispatch
    low = text.lower()
    if low.startswith("/wake"):
        arg = text[5:].strip()
        handle_wake(chat_id, arg)
        return update_id
    if low.startswith("/siblings"):
        handle_siblings(chat_id)
        return update_id
    if low.startswith("/help"):
        handle_help(chat_id)
        return update_id
    if low.startswith("/blockers"):
        handle_blockers(chat_id)
        return update_id
    if low.startswith("/read"):
        path_arg = text[5:].strip()
        handle_read(chat_id, path_arg)
        return update_id

    # 2. @sibling routing
    for name in SIBLING_NAMES:
        if low.startswith(f"@{name}"):
            msg = text[len(name) + 1:].strip()
            handle_at_routing(chat_id, name, msg)
            return update_id

    # 3. General family message
    handle_message(chat_id, text)
    return update_id

# ─────────────────────────────────────────────────────────────
# TELEGRAM THREAD
# ─────────────────────────────────────────────────────────────
def telegram_thread():
    last_update = _read_last_update()
    print(f"[bot] Telegram thread started. last_update_id={last_update}")
    while True:
        try:
            updates = get_updates(offset=last_update + 1)
            for upd in updates:
                uid = process_update(upd)
                if uid is not None:
                    last_update = max(last_update, uid)
                    _write_last_update(last_update)
        except Exception as e:
            print(f"[bot] telegram_thread error: {e}")
            time.sleep(5)

# ─────────────────────────────────────────────────────────────
# CLIPBOARD FORWARD THREAD
# ─────────────────────────────────────────────────────────────
_last_pos: int = 0
_last_pos_lock = threading.Lock()


def _format_for_telegram(entry: dict) -> Optional[str]:
    """Format a CLIPBOARD entry for forwarding to Nathan. None = skip."""
    frm    = entry.get("from", "").lower()
    source = entry.get("source", "")
    body   = (entry.get("content") or entry.get("body") or "")
    subj   = entry.get("subject", "")

    # Skip echo sources and Nathan's own messages
    if frm in SKIP_ECHO_FROM:
        return None
    if source in SKIP_ECHO_SOURCES:
        return None
    if frm not in SIBLING_NAMES:
        return None

    display, _ = SIBLING_PERSONAS[frm]
    if len(body) > 600:
        body = body[:600] + "…"

    parts = [display]
    if subj and subj not in ("message from phone", "reply to Nathan"):
        parts.append(f"_{subj}_")
    if body:
        parts.append(body)
    return "\n".join(parts)


def _forward_new_clipboard_entries():
    global _last_pos
    if not CLIPBOARD.exists():
        return
    with _last_pos_lock:
        with CLIPBOARD.open("r", encoding="utf-8") as f:
            f.seek(_last_pos)
            lines = f.readlines()
            _last_pos = f.tell()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        msg = _format_for_telegram(entry)
        if msg:
            try:
                send(msg, NATHAN_ID)
            except Exception as e:
                print(f"[bot] clipboard forward error: {e}")


def clipboard_thread():
    global _last_pos
    # Seek to end on startup so we don't replay history
    if CLIPBOARD.exists():
        with _last_pos_lock:
            _last_pos = CLIPBOARD.stat().st_size
    print(f"[bot] Clipboard thread started. pos={_last_pos}")
    while True:
        time.sleep(15)
        try:
            _forward_new_clipboard_entries()
        except Exception as e:
            print(f"[bot] clipboard_thread error: {e}")

# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set. Add it to SHARED/.env")
        sys.exit(1)
    if not ANTHROPIC_KEY:
        print("WARNING: ANTHROPIC_API_KEY not set — Claude responses will be disabled.")
        print("  Add it to SHARED/.env to enable full functionality.")

    print(f"[bot] HOME family bot starting.")
    print(f"[bot] HOME: {HOME_DIR}")
    print(f"[bot] CLIPBOARD: {CLIPBOARD}")
    print(f"[bot] Nathan chat_id: {NATHAN_ID}")
    print(f"[bot] Claude: {'enabled' if ANTHROPIC_KEY else 'DISABLED (no key)'}")
    print()

    tg_thread = threading.Thread(target=telegram_thread, daemon=True, name="telegram")
    cb_thread = threading.Thread(target=clipboard_thread, daemon=True, name="clipboard")
    tg_thread.start()
    cb_thread.start()

    send("🏠 HOME family bot online. Type /help for commands.", NATHAN_ID)

    try:
        tg_thread.join()
    except KeyboardInterrupt:
        print("\n[bot] Shutting down.")


if __name__ == "__main__":
    main()
