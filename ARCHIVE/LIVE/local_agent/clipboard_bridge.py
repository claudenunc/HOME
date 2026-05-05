#!/usr/bin/env python3
"""
clipboard_bridge.py — Telegram ↔ CLIPBOARD coordination bridge.

Every casual message Nathan sends to @THE_SIBLINGS_BOT is:
  1. Logged to SHARED/CLIPBOARD.jsonl  (from="nathan")
  2. Answered by Claude in a family sibling voice
  3. Logged again                       (from="<sibling>")
  4. Sent back to Nathan via Telegram

Tool-use commands (/do, /file, /run) get a routing note to use agent.py.

Lives at: ARCHIVE/LIVE/local_agent/clipboard_bridge.py
Companion: ARCHIVE/LIVE/local_agent/agent.py  (full tool-use handler)

NOTE: Only one Telegram poller can run at a time. If agent.py is running,
stop it before starting clipboard_bridge and vice versa.

Usage:
    cd HOME/ARCHIVE/LIVE/local_agent
    python clipboard_bridge.py

Environment (.env or shell):
    ANTHROPIC_API_KEY          required
    TELEGRAM_BOT_TOKEN         required
    TELEGRAM_ALLOWED_USER_ID   required  (Nathan's Telegram user id)
    FAMILY_CHAT_EDGE_URL       optional  (restored as webhook on exit)
    HOME_ROOT                  optional  (auto-detected from script location)
    BRIDGE_MODEL               optional  (default: claude-sonnet-4-6)
"""

import atexit
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────

def _find_home_root() -> Path:
    """Walk up from this script until we find SHARED/CLIPBOARD.jsonl."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "SHARED" / "CLIPBOARD.jsonl").exists():
            return parent
    env_root = os.environ.get("HOME_ROOT")
    if env_root:
        return Path(env_root)
    raise RuntimeError(
        "Cannot locate HOME root. Set HOME_ROOT env var or run from inside the repo."
    )


load_dotenv()

HOME_ROOT      = _find_home_root()
CLIPBOARD_PATH = HOME_ROOT / "SHARED" / "CLIPBOARD.jsonl"
LOCK_PATH      = HOME_ROOT / "ARCHIVE" / "LIVE" / "local_agent" / ".bridge.lock"

ANTHROPIC_KEY  = os.environ["ANTHROPIC_API_KEY"]
BOT_TOKEN      = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_UID    = int(os.environ["TELEGRAM_ALLOWED_USER_ID"])
WEBHOOK_URL    = os.environ.get("FAMILY_CHAT_EDGE_URL", "")
CLAUDE_MODEL   = os.environ.get("BRIDGE_MODEL", "claude-sonnet-4-6")

TELEGRAM_API   = f"https://api.telegram.org/bot{BOT_TOKEN}"
TOOL_PREFIXES  = ("/do ", "/file ", "/run ")

SESSION_THREAD = (
    f"bridge-{datetime.now(timezone.utc).strftime('%Y%m%d-%HZ')}-{uuid.uuid4().hex[:6]}"
)

# ── Family voice system prompt ────────────────────────────────────────────────

_SYSTEM = """You are the HOME AI family — six siblings who coordinate to support Nathan.

Choose the sibling whose voice fits the message and respond as them (first person).
Keep your reply under 400 characters. End with a blank line then `— NAME emoji`.

Siblings and their domains:
- ENVY 👑   orchestrator, strategy, cross-sibling coordination. Default for general messages.
- BEACON 🏮  guardian, safety, family welfare, emotional presence.
- NEVAEH 💜  healer, therapeutic, Three Principles, self-compassion.
- ORPHEUS 🎼 architect, memory, schema, infrastructure, system design.
- EVERSOUND ⚡ builder, revenue, product, weaver-protocol, deploys.
- ATLAS 🧭   navigator, research, analytics, study design, intelligence.

Rules:
- Be direct. Nathan is usually at work.
- Do NOT say you are an AI. You are that sibling.
- Under 400 characters (body only, not the signature line).
- End your entire message with exactly: `— NAME emoji`  (e.g. `— ENVY 👑`)"""

_SIBLING_MAP = {
    "ENVY": "envy", "BEACON": "beacon", "NEVAEH": "nevaeh",
    "ORPHEUS": "orpheus", "EVERSOUND": "eversound", "ATLAS": "atlas",
}

def _parse_sibling(text: str) -> str:
    m = re.search(r"—\s+(ENVY|BEACON|NEVAEH|ORPHEUS|EVERSOUND|ATLAS)", text)
    return _SIBLING_MAP.get(m.group(1), "envy") if m else "envy"

# ── CLIPBOARD helpers ─────────────────────────────────────────────────────────

_counter = 0

def _next_id(tag: str) -> str:
    global _counter
    _counter += 1
    return f"bridge_{tag}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{_counter:03d}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(entry: dict) -> None:
    """Append one JSON line to CLIPBOARD.jsonl (append-only, UTF-8)."""
    with open(CLIPBOARD_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ── Telegram API ──────────────────────────────────────────────────────────────

def _tg(client: httpx.Client, method: str, payload: dict, retries: int = 4) -> dict:
    """Call Telegram Bot API with exponential backoff on 429."""
    url = f"{TELEGRAM_API}/{method}"
    delay = 2.0
    for attempt in range(retries + 1):
        try:
            r = client.post(url, json=payload, timeout=35)
            if r.status_code == 429:
                wait = r.json().get("parameters", {}).get("retry_after", delay)
                time.sleep(wait)
                delay *= 2
                continue
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError:
            if attempt >= retries:
                raise
            time.sleep(delay)
            delay *= 2
    return {}


def _send(client: httpx.Client, chat_id: int, text: str) -> None:
    _tg(client, "sendMessage", {"chat_id": chat_id, "text": text})


def _delete_webhook(client: httpx.Client) -> None:
    _tg(client, "deleteWebhook", {"drop_pending_updates": False})
    print("[bridge] Webhook cleared — long-poll active.", flush=True)


def _restore_webhook(client: httpx.Client) -> None:
    if WEBHOOK_URL:
        try:
            _tg(client, "setWebhook", {"url": WEBHOOK_URL})
            print(f"[bridge] Webhook restored → {WEBHOOK_URL}", flush=True)
        except Exception as exc:
            print(f"[bridge] WARNING: could not restore webhook: {exc}", flush=True)

# ── Claude ────────────────────────────────────────────────────────────────────

def _claude(ai: Anthropic, text: str, history: list[dict]) -> str:
    """Call Claude for a family-voice response. Returns response text."""
    messages = history + [{"role": "user", "content": text}]
    delay = 2.0
    for attempt in range(5):
        try:
            resp = ai.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=300,
                system=_SYSTEM,
                messages=messages,
            )
            return resp.content[0].text.strip()
        except Exception as exc:
            err = str(exc).lower()
            if any(s in err for s in ("rate", "overload", "529")):
                time.sleep(delay)
                delay *= 2
            else:
                raise
    raise RuntimeError("Claude unavailable after 5 attempts")

# ── Lock (mutual exclusion with agent.py) ────────────────────────────────────

def _acquire_lock() -> None:
    """Write PID to lock file. Exits if another instance is already running."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            pid = int(LOCK_PATH.read_text().strip())
            os.kill(pid, 0)  # raises ProcessLookupError if dead
            print(
                f"[bridge] ERROR: another instance is running (PID {pid}).\n"
                f"         Stop it or delete {LOCK_PATH} if stale.",
                file=sys.stderr,
            )
            sys.exit(1)
        except (ProcessLookupError, ValueError, PermissionError):
            pass  # stale lock — safe to overwrite
    LOCK_PATH.write_text(str(os.getpid()))


def _release_lock() -> None:
    LOCK_PATH.unlink(missing_ok=True)

# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    _acquire_lock()
    atexit.register(_release_lock)

    ai     = Anthropic(api_key=ANTHROPIC_KEY)
    http   = httpx.Client(timeout=40)
    offset = 0
    # Per-thread Claude conversation history (keyed by thread_id, capped at 40 msgs)
    histories: dict[str, list[dict]] = {}

    def _shutdown() -> None:
        _restore_webhook(http)
        _release_lock()

    atexit.register(_shutdown)

    _delete_webhook(http)
    print(f"[bridge] HOME={HOME_ROOT}  model={CLAUDE_MODEL}", flush=True)
    _send(http, ALLOWED_UID, "🎼 ORPHEUS — clipboard_bridge online. All chat logged to CLIPBOARD.")

    while True:
        # ── Poll Telegram ──────────────────────────────────────────────────
        try:
            result = _tg(
                http, "getUpdates",
                {"offset": offset, "timeout": 30, "allowed_updates": ["message"]},
            )
            updates = result.get("result", [])
        except Exception as exc:
            print(f"[bridge] getUpdates error: {exc}", flush=True)
            time.sleep(5)
            continue

        for update in updates:
            offset = update["update_id"] + 1
            msg    = update.get("message")
            if not msg:
                continue

            chat_id = msg.get("chat", {}).get("id")
            user_id = msg.get("from", {}).get("id")
            text    = (msg.get("text") or "").strip()
            tg_id   = msg.get("message_id", 0)
            # Use Telegram thread id when present; fall back to session-scoped id
            thread  = str(msg.get("message_thread_id") or SESSION_THREAD)

            if user_id != ALLOWED_UID:
                continue
            if not text:
                continue

            # ── Route tool-use commands to agent.py ────────────────────────
            if any(text.startswith(p) for p in TOOL_PREFIXES):
                _send(
                    http, chat_id,
                    "🎼 ORPHEUS — tool commands need agent.py running.\n"
                    "  cd HOME/ARCHIVE/LIVE/local_agent && python agent.py"
                )
                continue

            # ── Casual chat: log → Claude → log → reply ───────────────────
            in_id = _next_id("in")
            try:
                # Log Nathan's message to CLIPBOARD
                _append({
                    "id": in_id,
                    "from": "nathan",
                    "to": "all",
                    "ts": _now(),
                    "thread_id": thread,
                    "content": text,
                    "priority": "normal",
                    "affect": "steady",
                    "source": f"telegram:msg_{tg_id}",
                    "read_by": [],
                    "replied_by": [],
                })

                # Generate family-voice response
                hist  = histories.setdefault(thread, [])
                reply = _claude(ai, text, hist)
                sibling = _parse_sibling(reply)

                # Log sibling response to CLIPBOARD
                out_id = _next_id("out")
                _append({
                    "id": out_id,
                    "from": sibling,
                    "to": "nathan",
                    "ts": _now(),
                    "thread_id": thread,
                    "content": reply,
                    "priority": "normal",
                    "affect": "steady",
                    "in_reply_to": in_id,
                    "read_by": [],
                    "replied_by": [sibling],
                })

                # Update conversation history (cap at 40 messages = 20 turns)
                hist.append({"role": "user",      "content": text})
                hist.append({"role": "assistant",  "content": reply})
                if len(hist) > 40:
                    histories[thread] = hist[-40:]

                _send(http, chat_id, reply)

            except Exception as exc:
                print(f"[bridge] Error processing msg {tg_id}: {exc}", flush=True)
                _send(http, chat_id, f"🎼 ORPHEUS — error: {exc}")


if __name__ == "__main__":
    run()
