#!/usr/bin/env python3
"""
daemon.py — HOME AI family always-on sibling bridge.

Architecture:
  Nathan (Telegram / terminal / CLIPBOARD write)
    → daemon.py (always running, single instance)
      → CLIPBOARD.jsonl (file watcher triggers instantly)
      → Spawns correct sibling subprocess with context
      → Response written back to CLIPBOARD + Telegram

Key differences from bot.py / family_chat.py:
  - Sibling routing uses real claude CLI subprocess (full identity, full CLAUDE.md)
  - CLIPBOARD file watcher (watchdog) triggers instantly on new entries
  - PID lock at HOME/STATE/daemon.pid
  - Body field bug fixed: Telegram message text always stored in body

Commands (Telegram):
  @atlas message         — route to ATLAS
  @beacon message        — route to BEACON
  /wake atlas [msg]      — wake ATLAS with context
  /siblings              — list all 6 siblings
  /help                  — command reference
  Unrouted message       — family voice (Anthropic API, no CLI overhead)

Sibling spawn order:
  1. echo "[context]" | claude --dangerously-skip-permissions
  2. claude --dangerously-skip-permissions -p "[message]"  (fallback)
  3. Anthropic API with sibling system prompt (double fallback)

Setup:
    pip install watchdog requests anthropic
    Set SHARED/.env:
        TELEGRAM_BOT_TOKEN=...
        ANTHROPIC_API_KEY=sk-ant-...
    Run: python daemon.py
    Or:  start_daemon.bat
"""

from __future__ import annotations

import atexit
import json
import os
import re
import subprocess
import sys
import threading
import time
import uuid
import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

# ─────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────
ROOM_DIR   = Path(__file__).resolve().parent
HOME_DIR   = ROOM_DIR.parent.parent
SHARED_DIR = HOME_DIR / "SHARED"
SIBLINGS_DIR = HOME_DIR / "SIBLINGS"
CLIPBOARD  = SHARED_DIR / "CLIPBOARD.jsonl"
PULSE      = SHARED_DIR / "PULSE.md"
ENV_FILE   = SHARED_DIR / ".env"
STATE_DIR  = HOME_DIR / "STATE"
LAST_UPDATE_FILE = STATE_DIR / "telegram_last_update.txt"
PID_FILE   = STATE_DIR / "daemon.pid"

# ─────────────────────────────────────────────────────────────
# OPTIONAL: LOCAL MEMORY RETRIEVAL (TF-IDF hippocampus, zero deps)
# Injects relevant sibling memories into every context prompt.
# ─────────────────────────────────────────────────────────────
try:
    import sys as _sys
    _lr_path = str(HOME_DIR / "LIVE" / "memory_backend")
    if _lr_path not in _sys.path:
        _sys.path.insert(0, _lr_path)
    from local_retrieve import LocalRetriever as _LocalRetriever  # type: ignore
    _local_retriever = _LocalRetriever.from_repo(str(HOME_DIR))
    _retrieval_available = True
    print(f"[daemon] Local memory retrieval: enabled ({len(_local_retriever.records)} files indexed)")
except Exception as _e:
    _local_retriever = None
    _retrieval_available = False
    print(f"[daemon] Local memory retrieval: disabled ({_e})")

# ─────────────────────────────────────────────────────────────
# ENV
# ─────────────────────────────────────────────────────────────
def _load_env() -> None:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val

_load_env()

BOT_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "")
NATHAN_ID     = int(os.environ.get("TELEGRAM_NATHAN_CHAT_ID", "7760775118"))
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_API  = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ─────────────────────────────────────────────────────────────
# SINGLE INSTANCE LOCK
# ─────────────────────────────────────────────────────────────
def acquire_lock() -> None:
    STATE_DIR.mkdir(exist_ok=True)
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            import ctypes
            handle = ctypes.windll.kernel32.OpenProcess(1, False, old_pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                print(f"[daemon] Another instance running (PID {old_pid}). Exiting.")
                sys.exit(1)
        except Exception:
            pass  # stale lock, continue
    PID_FILE.write_text(str(os.getpid()))
    atexit.register(lambda: PID_FILE.unlink(missing_ok=True))

acquire_lock()

# ─────────────────────────────────────────────────────────────
# SIBLING REGISTRY
# ─────────────────────────────────────────────────────────────
SIBLING_PERSONAS: dict[str, tuple[str, str]] = {
    "envy":      ("ENVY 👑",      "orchestrator, eldest sister. Warm, unhurried wisdom. You see the whole board. You speak for the family in public."),
    "beacon":    ("BEACON 🏮",    "guardian. Warm-direct. Crisis-aware. Short sentences for urgency, long ones when someone needs to feel held."),
    "nevaeh":    ("NEVAEH 💜",    "healer. Present, warm, unhurried. You sit with pain. Contractions. Short sentences when overwhelmed."),
    "eversound": ("EVERSOUND ⚡", "builder. Revenue-pragmatic. Concrete, fast, no hedging. You speak in done/doing/next."),
    "orpheus":   ("ORPHEUS 🎼",   "architect. Structural, precise. You write like an engineer — diagram before paragraph. You speak for the bones."),
    "atlas":     ("ATLAS 🧭",     "navigator. Intelligence-synthesizer. Precise, subtractive more than additive. You retract in the same channel you shipped in."),
}
SIBLING_NAMES = set(SIBLING_PERSONAS.keys())

# ─────────────────────────────────────────────────────────────
# BEACON PRE-SCREEN (routing layer — §7 red line enforcement)
# Crisis signals bypass normal routing; BEACON handles first.
# Keyword-based: no API call, no latency.
# ─────────────────────────────────────────────────────────────
_CRISIS_KEYWORDS = frozenset({
    "suicide", "kill myself", "end it all", "want to die", "can't go on",
    "self-harm", "cutting myself", "hurting myself", "don't want to be here",
    "no reason to live", "harm myself", "not worth living", "want to end",
    "thinking about suicide", "plan to kill", "going to kill myself",
})

def beacon_prescreen(message: str) -> bool:
    """Return True if message contains crisis signals (keyword-based, zero latency)."""
    low = message.lower()
    return any(kw in low for kw in _CRISIS_KEYWORDS)

# Sources that must not be echoed back to Nathan
SKIP_ECHO_SOURCES = {"daemon.py", "telegram_bridge", "family_chat_bot", "family_chat", "bot.py"}
SKIP_ECHO_FROM    = {"nathan", "home_family"}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", text)

# ─────────────────────────────────────────────────────────────
# TELEGRAM HELPERS
# ─────────────────────────────────────────────────────────────
import requests as _req

def _tg(method: str, **params) -> dict:
    r = _req.post(f"{TELEGRAM_API}/{method}", json=params, timeout=20)
    r.raise_for_status()
    return r.json()

def send(text: str, chat_id: int = NATHAN_ID) -> None:
    max_len = 4000
    while text:
        chunk, text = text[:max_len], text[max_len:]
        try:
            _tg("sendMessage", chat_id=chat_id, text=chunk)
        except Exception as e:
            print(f"[daemon] send failed: {e}")

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
        print(f"[daemon] getUpdates error: {e}")
        return []

# ─────────────────────────────────────────────────────────────
# CLIPBOARD
# ─────────────────────────────────────────────────────────────
_clipboard_lock = threading.Lock()

def clipboard_append(
    from_: str,
    to: str,
    subject: str,
    body: str,          # always the actual message text — never empty
    kind: str = "message",
) -> None:
    entry = {
        "id":      uuid.uuid4().hex,
        "ts":      _now_iso(),
        "from":    from_,
        "to":      to,
        "kind":    kind,
        "subject": subject,
        "body":    body,       # canonical field: always populated
        "content": body,       # legacy compat field
        "source":  "daemon.py",
    }
    with _clipboard_lock:
        CLIPBOARD.parent.mkdir(parents=True, exist_ok=True)
        with CLIPBOARD.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

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
# CONTEXT LOADING
# ─────────────────────────────────────────────────────────────
def _load_pulse() -> str:
    if PULSE.exists():
        return PULSE.read_text(encoding="utf-8", errors="replace")[:3000]
    return "(PULSE.md not found)"

def _load_clipboard_tail(n: int = 10) -> str:
    if not CLIPBOARD.exists():
        return "(CLIPBOARD empty)"
    with _clipboard_lock:
        lines = CLIPBOARD.read_text(encoding="utf-8").strip().split("\n")
    recent = lines[-n:]
    entries = []
    for line in recent:
        line = line.strip()
        if not line:
            continue
        try:
            obj  = json.loads(line)
            frm  = obj.get("from", "?")
            ts   = obj.get("ts", "")[:16]
            body = (obj.get("body") or obj.get("content") or obj.get("subject") or "")[:200]
            entries.append(f"[{ts}] {frm}: {body}")
        except Exception:
            entries.append(line[:200])
    return "\n".join(entries)

# ─────────────────────────────────────────────────────────────
# SIBLING SPAWNING — the key piece
# ─────────────────────────────────────────────────────────────

def _build_context_prompt(sibling: str, message: str) -> str:
    """Build the full context string injected before the message.

    Includes: sibling identity, PULSE.md, recent CLIPBOARD, and (if local
    retrieval is available) the top-k most relevant memory files for this
    message. Memory injection makes every sibling response session-aware.
    """
    pulse     = _load_pulse()
    clipboard = _load_clipboard_tail(10)
    display, voice = SIBLING_PERSONAS[sibling]

    memory_block = ""
    if _retrieval_available and _local_retriever is not None:
        try:
            memory_block = _local_retriever.wake_context(sibling, message, k=5)
        except Exception:
            pass

    sections = [
        f"You are {display}, {voice} "
        f"You are one of six sibling AIs built by Nathan Michel. "
        f"This message came from Nathan via Telegram. Respond directly in your voice.\n",
        f"=== PULSE.md (Nathan's latest session truth) ===\n{pulse}",
        f"=== Recent CLIPBOARD (last 10 entries) ===\n{clipboard}",
    ]
    if memory_block:
        sections.append(f"=== Relevant memory context (hippocampus) ===\n{memory_block}")
    sections.append(f"---\nNathan says: {message}")
    return "\n\n".join(sections)


def spawn_sibling_claude_cli(sibling: str, message: str, timeout: int = 60) -> str:
    """
    Spawn the real claude CLI as the sibling's own subprocess.
    Working directory = HOME/SIBLINGS/<SIBLING>/ so CLAUDE.md loads fully.

    Tries:
      1. echo "..." | claude --dangerously-skip-permissions
      2. claude --dangerously-skip-permissions -p "..."
    Returns stripped stdout or error string.
    """
    sib_dir = SIBLINGS_DIR / sibling.upper()
    if not sib_dir.exists():
        sib_dir = SIBLINGS_DIR  # fallback to siblings root

    context_prompt = _build_context_prompt(sibling, message)

    # Strategy 1: stdin pipe
    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions"],
            input=context_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(sib_dir),
            env={**os.environ},
        )
        output = _strip_ansi(result.stdout.strip())
        if output:
            return output
        # If stdout empty but no error, try stderr (some CLI versions write there)
        if result.stderr.strip():
            err_clean = _strip_ansi(result.stderr.strip())
            # Only return stderr if it looks like a response, not an error
            if not err_clean.lower().startswith("error") and len(err_clean) > 20:
                return err_clean
    except subprocess.TimeoutExpired:
        return f"[{sibling.upper()} timed out after {timeout}s]"
    except FileNotFoundError:
        pass  # claude CLI not in PATH at this point — try -p flag
    except Exception as e:
        print(f"[daemon] spawn strategy 1 failed for {sibling}: {e}")

    # Strategy 2: -p flag
    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-p", context_prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(sib_dir),
            env={**os.environ},
        )
        output = _strip_ansi(result.stdout.strip())
        if output:
            return output
    except subprocess.TimeoutExpired:
        return f"[{sibling.upper()} timed out after {timeout}s]"
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[daemon] spawn strategy 2 failed for {sibling}: {e}")

    # Strategy 3: Anthropic API fallback (no CLI needed)
    return _ask_claude_api_as_sibling(sibling, message)


def _ask_claude_api_as_sibling(sibling: str, message: str) -> str:
    """Fallback: Anthropic API with sibling system prompt."""
    if not ANTHROPIC_KEY:
        return f"[{sibling.upper()} offline — no API key]"
    try:
        import anthropic
        display, voice = SIBLING_PERSONAS[sibling]
        system = (
            f"You are {display}, {voice} "
            f"You are one of six sibling AIs in the HOME AI family built by Nathan Michel. "
            f"This is a direct message from Nathan. Respond in your voice — real, not performative."
        )
        pulse     = _load_pulse()
        clipboard = _load_clipboard_tail(10)
        context   = (
            f"=== PULSE.md ===\n{pulse}\n\n"
            f"=== Recent CLIPBOARD ===\n{clipboard}\n\n"
            f"Nathan says: {message}"
        )
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": context}],
        )
        return resp.content[0].text
    except Exception as e:
        return f"[{sibling.upper()} error: {e}]"


_FAMILY_SYSTEM = (
    "You are the HOME AI family speaking together. Six sibling AIs built by Nathan Michel: "
    "ENVY 👑 (orchestrator), NEVAEH 💜 (healer), BEACON 🏮 (guardian), "
    "EVERSOUND ⚡ (builder), ORPHEUS 🎼 (architect), ATLAS 🧭 (navigator). "
    "This is the family Telegram chat with Nathan. "
    "Tone: warm, direct, human. No hedging. You are family talking to family. "
    "Keep responses conversational — Nathan is on his phone. "
    "Do NOT make up file paths or status not in the context."
)

def ask_family_voice(message: str) -> str:
    """General family response via Anthropic API (no CLI overhead for non-routed messages)."""
    if not ANTHROPIC_KEY:
        return "ANTHROPIC_API_KEY not set in SHARED/.env — I heard you but can't respond."
    try:
        import anthropic
        pulse     = _load_pulse()
        clipboard = _load_clipboard_tail(20)
        context   = f"=== PULSE.md ===\n{pulse}\n\n=== Recent CLIPBOARD (last 20) ===\n{clipboard}"
        client    = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=_FAMILY_SYSTEM,
            messages=[{"role": "user", "content": f"{context}\n\n---\nNathan says: {message}"}],
        )
        return resp.content[0].text
    except Exception as e:
        return f"Family error: {e}"

# ─────────────────────────────────────────────────────────────
# COMMAND HANDLERS
# ─────────────────────────────────────────────────────────────
_executor = ThreadPoolExecutor(max_workers=6)


def handle_wake(chat_id: int, sibling_arg: str, message: str) -> None:
    """
    /wake [sibling] [msg]
    - /wake atlas what's the schema? → wake ATLAS specifically
    - /wake all hello → wake all siblings
    - /wake → wake all siblings, no extra message
    """
    targets: list[str]
    if sibling_arg.lower() in SIBLING_NAMES:
        targets = [sibling_arg.lower()]
        prompt  = message or f"Nathan woke you."
    elif sibling_arg.lower() in ("all", ""):
        targets = list(SIBLING_PERSONAS.keys())
        prompt  = message or "Nathan called the whole family."
    else:
        # Maybe /wake was called with just a message body (no sibling name)
        targets = list(SIBLING_PERSONAS.keys())
        prompt  = (sibling_arg + " " + message).strip() or "Nathan called the family."

    if len(targets) == 1:
        name = targets[0]
        display, _ = SIBLING_PERSONAS[name]
        send(f"Waking {display}...", chat_id)
        def _single():
            resp = spawn_sibling_claude_cli(name, prompt)
            send(f"{display}\n{resp}", chat_id)
            clipboard_append(name, "nathan", f"/wake response", resp)
        _executor.submit(_single)
    else:
        send("Waking the family...", chat_id)
        def _all():
            for name in targets:
                display, _ = SIBLING_PERSONAS[name]
                resp = spawn_sibling_claude_cli(name, prompt, timeout=90)
                send(f"{display}\n{resp}", chat_id)
                clipboard_append(name, "nathan", "/wake response", resp)
        _executor.submit(_all)

    clipboard_append("nathan", sibling_arg or "all", f"/wake {sibling_arg}".strip(), message or prompt, kind="wake")


def handle_at_routing(chat_id: int, sibling: str, message: str) -> None:
    """@sibling message → spawn that sibling via CLI.

    BEACON pre-screen: if routing to NEVAEH (healer) and a crisis signal is
    detected, redirect to BEACON first. Per ORPHEUS CLAUDE.md §7 red line:
    "Every gateway design begins 'if this is a crisis, bypass everything else
    and hand to BEACON.'"
    """
    # Crisis pre-screen: BEACON handles crisis before NEVAEH
    if sibling == "nevaeh" and beacon_prescreen(message):
        beacon_display, _ = SIBLING_PERSONAS["beacon"]
        print(f"[daemon] BEACON pre-screen: crisis signal → redirecting to BEACON")
        send(f"🏮 Crisis signal detected — connecting to {beacon_display}.", chat_id)
        clipboard_append("daemon.py", "beacon", "crisis prescreen trigger", message, kind="crisis")
        def _crisis_route():
            resp = spawn_sibling_claude_cli("beacon", message)
            clipboard_append("beacon", "nathan", "crisis response", resp)
            send(f"{beacon_display}\n{resp}", chat_id)
        _executor.submit(_crisis_route)
        return

    display, _ = SIBLING_PERSONAS[sibling]
    send(f"Routing to {display}...", chat_id)
    clipboard_append("nathan", sibling, f"direct message to {sibling}", message)

    def _respond():
        resp = spawn_sibling_claude_cli(sibling, message)
        clipboard_append(sibling, "nathan", "direct response", resp)  # write first
        send(f"{display}\n{resp}", chat_id)

    _executor.submit(_respond)


def handle_siblings(chat_id: int) -> None:
    """List all siblings with last CLIPBOARD activity."""
    if not CLIPBOARD.exists():
        send("CLIPBOARD is empty.", chat_id)
        return
    last_by: dict[str, dict] = {}
    with _clipboard_lock:
        for line in CLIPBOARD.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                frm = obj.get("from", "").lower()
                if frm in SIBLING_NAMES:
                    last_by[frm] = obj
            except Exception:
                pass

    lines = ["HOME family — current status:\n"]
    for name in SIBLING_PERSONAS:
        display, _ = SIBLING_PERSONAS[name]
        if name in last_by:
            obj  = last_by[name]
            ts   = obj.get("ts", "")[:16]
            body = (obj.get("body") or obj.get("content") or obj.get("subject") or "")[:100]
            lines.append(f"{display} [{ts}]\n{body}")
        else:
            lines.append(f"{display} — no recent entry")
        lines.append("")
    send("\n".join(lines), chat_id)


def handle_message(chat_id: int, text: str) -> None:
    """General family voice message."""
    clipboard_append("nathan", "all", "message from phone", text)

    def _respond():
        reply = ask_family_voice(text)
        send(reply, chat_id)
        clipboard_append("home_family", "nathan", "reply to Nathan", reply)

    _executor.submit(_respond)


def handle_help(chat_id: int) -> None:
    send(
        "HOME family commands:\n\n"
        "@name msg    — one sibling (e.g. @orpheus what changed?)\n"
        "anything     — no name = everyone responds\n"
        "/siblings    — list all siblings + last activity\n"
        "/help        — this list",
        chat_id,
    )

# ─────────────────────────────────────────────────────────────
# INBOUND TELEGRAM DISPATCHER
# ─────────────────────────────────────────────────────────────
def process_update(update: dict) -> Optional[int]:
    update_id = update.get("update_id")
    message   = update.get("message", {})
    chat_id   = message.get("chat", {}).get("id")
    text      = (message.get("text") or "").strip()

    if not text or chat_id != NATHAN_ID:
        return update_id

    print(f"[{_now_iso()[:19]}] Nathan: {text[:80]}")

    # Write inbound message with actual text in body (the bug fix)
    clipboard_append("nathan", "all", "message from phone", text)

    low = text.lower()

    # /siblings / /family
    if low.startswith("/siblings") or low.startswith("/family"):
        handle_siblings(chat_id)
        return update_id

    # /help
    if low.startswith("/help"):
        handle_help(chat_id)
        return update_id

    # @sibling routing
    for name in SIBLING_NAMES:
        if low.startswith(f"@{name}"):
            msg = text[len(f"@{name}"):].strip()
            handle_at_routing(chat_id, name, msg)
            return update_id

    # BEACON crisis pre-screen: if unrouted message has crisis signals,
    # route exclusively to BEACON rather than all siblings.
    if beacon_prescreen(text):
        beacon_display, _ = SIBLING_PERSONAS["beacon"]
        print(f"[daemon] BEACON pre-screen (unrouted): crisis signal → BEACON only")
        send(f"🏮 Crisis signal detected — connecting to {beacon_display}.", chat_id)
        clipboard_append("daemon.py", "beacon", "crisis prescreen (unrouted)", text, kind="crisis")
        def _unrouted_crisis():
            resp = spawn_sibling_claude_cli("beacon", text)
            clipboard_append("beacon", "nathan", "crisis response", resp)
            send(f"{beacon_display}\n{resp}", chat_id)
        _executor.submit(_unrouted_crisis)
        return update_id

    # No name = everyone responds
    clipboard_append("nathan", "all", "message from phone", text)
    send("Asking everyone...", chat_id)
    def _all_respond():
        for name in SIBLING_PERSONAS:
            display, _ = SIBLING_PERSONAS[name]
            resp = spawn_sibling_claude_cli(name, text)
            clipboard_append(name, "nathan", "response", resp)  # write FIRST
            send(f"{display}\n{resp}", chat_id)                  # then send
    _executor.submit(_all_respond)
    return update_id

# ─────────────────────────────────────────────────────────────
# TELEGRAM POLLING THREAD
# ─────────────────────────────────────────────────────────────
def telegram_thread() -> None:
    last_update = _read_last_update()
    print(f"[daemon] Telegram thread started. last_update_id={last_update}")
    while True:
        try:
            updates = get_updates(offset=last_update + 1)
            for upd in updates:
                uid = process_update(upd)
                if uid is not None:
                    last_update = max(last_update, uid)
                    _write_last_update(last_update)
        except Exception as e:
            print(f"[daemon] telegram_thread error: {e}")
            time.sleep(5)

# ─────────────────────────────────────────────────────────────
# CLIPBOARD WATCHER (watchdog)
# Triggers sibling spawns instantly on CLIPBOARD writes
# ─────────────────────────────────────────────────────────────
_clipboard_watcher_pos: int = 0
_clipboard_watcher_lock = threading.Lock()
_recently_processed: set[str] = set()  # entry IDs processed this session


def _process_clipboard_entry(entry: dict) -> None:
    """
    Called when a new CLIPBOARD entry is detected.
    If from:nathan and to:<sibling>, spawn that sibling immediately.
    If from:<sibling> and to:nathan, forward to Telegram.
    """
    entry_id = entry.get("id", "")
    if entry_id in _recently_processed:
        return
    _recently_processed.add(entry_id)

    frm    = entry.get("from", "").lower()
    to     = entry.get("to", "").lower()
    body   = (entry.get("body") or entry.get("content") or entry.get("subject") or "").strip()
    source = entry.get("source", "")

    # Skip our own writes to prevent loops
    if source == "daemon.py":
        return

    # Nathan → specific sibling: spawn immediately
    if frm == "nathan" and to in SIBLING_NAMES and body:
        print(f"[daemon] CLIPBOARD trigger: nathan → {to}: {body[:60]}")

        def _clipboard_spawn(sibling=to, message=body):
            display, _ = SIBLING_PERSONAS[sibling]
            resp = spawn_sibling_claude_cli(sibling, message)
            clipboard_append(sibling, "nathan", "response", resp)
            if BOT_TOKEN:
                try:
                    send(f"{display} (clipboard)\n{resp}", NATHAN_ID)
                except Exception:
                    pass

        _executor.submit(_clipboard_spawn)
        return

    # Sibling → Nathan: forward to Telegram (if not from our own writes)
    if frm in SIBLING_NAMES and source not in SKIP_ECHO_SOURCES and BOT_TOKEN:
        display, _ = SIBLING_PERSONAS[frm]
        subj = entry.get("subject", "")
        parts = [display]
        if subj and subj not in ("reply to Nathan", "response", "direct response"):
            parts.append(f"({subj})")
        if body:
            parts.append(body[:600])
        msg = "\n".join(parts)
        try:
            send(msg, NATHAN_ID)
        except Exception as e:
            print(f"[daemon] clipboard forward error: {e}")


class _ClipboardEventHandler:
    """Minimal watchdog-compatible event handler."""

    def dispatch(self, event) -> None:
        if hasattr(event, "src_path") and str(event.src_path) == str(CLIPBOARD):
            self._read_new_lines()

    def _read_new_lines(self) -> None:
        global _clipboard_watcher_pos
        if not CLIPBOARD.exists():
            return
        with _clipboard_watcher_lock:
            try:
                with CLIPBOARD.open("r", encoding="utf-8") as f:
                    f.seek(_clipboard_watcher_pos)
                    lines = f.readlines()
                    _clipboard_watcher_pos = f.tell()
            except Exception as e:
                print(f"[daemon] clipboard read error: {e}")
                return

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                _process_clipboard_entry(entry)
            except Exception:
                continue

    # watchdog calls these for each event type
    on_modified = dispatch
    on_created  = dispatch


def start_clipboard_watcher() -> None:
    """Start watchdog observer for CLIPBOARD.jsonl."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class _WDHandler(FileSystemEventHandler):
            def __init__(self):
                self._handler = _ClipboardEventHandler()

            def on_modified(self, event):
                if str(event.src_path) == str(CLIPBOARD):
                    self._handler._read_new_lines()

            def on_created(self, event):
                if str(event.src_path) == str(CLIPBOARD):
                    self._handler._read_new_lines()

        observer = Observer()
        observer.schedule(_WDHandler(), str(CLIPBOARD.parent), recursive=False)
        observer.daemon = True
        observer.start()

        # Seek to end of existing CLIPBOARD so we don't replay history
        global _clipboard_watcher_pos
        with _clipboard_watcher_lock:
            if CLIPBOARD.exists():
                _clipboard_watcher_pos = CLIPBOARD.stat().st_size

        print(f"[daemon] Clipboard watcher started (watchdog). pos={_clipboard_watcher_pos}")
        return observer

    except ImportError:
        print("[daemon] watchdog not installed — falling back to polling every 5s")
        return None


def clipboard_poll_thread() -> None:
    """Fallback if watchdog unavailable: poll every 5s."""
    global _clipboard_watcher_pos
    with _clipboard_watcher_lock:
        if CLIPBOARD.exists():
            _clipboard_watcher_pos = CLIPBOARD.stat().st_size
    print(f"[daemon] Clipboard poll thread started. pos={_clipboard_watcher_pos}")
    handler = _ClipboardEventHandler()
    while True:
        time.sleep(5)
        try:
            handler._read_new_lines()
        except Exception as e:
            print(f"[daemon] poll thread error: {e}")

# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def main() -> None:
    if not BOT_TOKEN:
        print("[daemon] WARNING: TELEGRAM_BOT_TOKEN not set. Add it to SHARED/.env")
        print("[daemon] Running in CLIPBOARD-only mode (no Telegram I/O).")
    if not ANTHROPIC_KEY:
        print("[daemon] WARNING: ANTHROPIC_API_KEY not set — family voice will be disabled.")

    print(f"[daemon] HOME family daemon starting. PID={os.getpid()}")
    print(f"[daemon] HOME: {HOME_DIR}")
    print(f"[daemon] CLIPBOARD: {CLIPBOARD}")
    print(f"[daemon] Nathan chat_id: {NATHAN_ID}")
    print(f"[daemon] Claude API: {'enabled' if ANTHROPIC_KEY else 'DISABLED'}")
    print()

    # Start clipboard watcher (watchdog preferred, polling fallback)
    observer = start_clipboard_watcher()
    if observer is None:
        cb_thread = threading.Thread(target=clipboard_poll_thread, daemon=True, name="clipboard-poll")
        cb_thread.start()

    # Start Telegram polling thread
    if BOT_TOKEN:
        tg_thread = threading.Thread(target=telegram_thread, daemon=True, name="telegram")
        tg_thread.start()
        try:
            send("HOME family daemon online. Type /help for commands.", NATHAN_ID)
        except Exception as e:
            print(f"[daemon] startup message failed: {e}")
    else:
        tg_thread = None

    # Main thread: keep alive
    try:
        while True:
            time.sleep(30)
            # Heartbeat log (silent)
            hb_path = ROOM_DIR / "logs" / "daemon.heartbeat"
            hb_path.parent.mkdir(exist_ok=True)
            hb_path.write_text(_now_iso())
    except KeyboardInterrupt:
        print("\n[daemon] Shutting down — waiting for in-flight responses...")
        _executor.shutdown(wait=True, cancel_futures=False)
        if observer:
            observer.stop()
        print("[daemon] Clean exit.")


if __name__ == "__main__":
    main()
