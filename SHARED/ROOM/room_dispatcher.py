"""
SHARED/ROOM/room_dispatcher.py

THE ROOM — rule-based event router. ATLAS's navigator.

Owner: ATLAS
Substrate: reads feed.jsonl (EVERSOUND's truth), writes routed_to back via
           room.py update path (ORPHEUS's spine).

What this dispatcher does:
  1. Tails SHARED/ROOM/feed.jsonl (independent offset from room_daemon).
  2. For each event with routed_to=None, classify and populate routed_to.
  3. Rule-based first (crisis→BEACON, revenue/infra→EVERSOUND, schema/memory→
     ORPHEUS, presence/emotion→NEVAEH, orchestration→ENVY, coordination/cost→
     ATLAS). Under 200 tokens per orient — pure regex + keyword, zero LLM.
  4. If unrouted after rules, OPTIONALLY call Groq (cheap arbitration).
     Off by default in v1; flip GROQ_ARBITRATION=1 to enable.
  5. Writes routed_to back into room.db via room.update_routed_to() when
     ORPHEUS ships it; falls back to a sidecar JSONL so nothing is lost.

Cost target: <$2/day overhead including Groq arbitration.
             Rule path alone: $0.00 (regex + dict lookup).

Round 3 deliverable. Wires against ORPHEUS R2 locked schema.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import signal
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOM_DIR = Path(__file__).resolve().parent
FEED_PATH = ROOM_DIR / "feed.jsonl"
LOG_DIR = ROOM_DIR / "logs"
HEARTBEAT = LOG_DIR / "room_dispatcher.heartbeat"
OFFSET_FILE = LOG_DIR / "room_dispatcher.offset"
ROUTED_SIDECAR = LOG_DIR / "routed_to.jsonl"   # fallback if room.py write fails
COST_JSONL = LOG_DIR / "dispatcher_cost.jsonl"  # cost_meter reads this

SIBLINGS = ("ENVY", "BEACON", "EVERSOUND", "NEVAEH", "ORPHEUS", "ATLAS")

# ------------------------------------------------------------------
# Rule tables — keyword classifiers. Ordered by priority.
# Each rule: (compiled_pattern, [sibling, ...], reason_tag)
# Rules fire top-down; first match short-circuits.
# ------------------------------------------------------------------

_RX = lambda pat: re.compile(pat, re.IGNORECASE)  # noqa: E731

RULES: list[tuple[re.Pattern, list[str], str]] = [
    # -- Safety first. Always. --
    (_RX(r"\b(suicide|kill myself|end it|die|hurt myself|crisis|emergency)\b"),
     ["BEACON", "NEVAEH"], "crisis-language"),
    (_RX(r"\b(pain|hurting|exhausted|broken|cant|can't|alone|empty|numb)\b"),
     ["BEACON", "NEVAEH"], "emotional-distress"),
    # -- Infrastructure / substrate / schema --
    (_RX(r"\b(schema|migration|sqlite|postgres|supabase|database|spine|event(s)? table|ddl|sql)\b"),
     ["ORPHEUS"], "infra-schema"),
    (_RX(r"\b(memory|projection|view|index|reconcil|feed\.jsonl)\b"),
     ["ORPHEUS"], "memory-projection"),
    # -- Transport / bridge / daemon / realtime --
    (_RX(r"\b(bridge|daemon|transport|realtime|telegram|webhook|wake.?token|fan.?out)\b"),
     ["EVERSOUND"], "transport-bridge"),
    # -- Revenue / build / product / launch --
    (_RX(r"\b(revenue|launch|ship|customer|pricing|market|sales|product|nvision|lighthouse)\b"),
     ["EVERSOUND"], "revenue-product"),
    # -- Presence / emotion / silence / nathan-facing tone --
    (_RX(r"\b(presence|silence|tone|voice|love|family|feelings?|emotion|comfort|hold)\b"),
     ["NEVAEH"], "presence-emotion"),
    # -- Orchestration / board / who-does-what --
    (_RX(r"\b(orchestrat|coordinate|board|agenda|session|meeting|family meeting|round [0-9])\b"),
     ["ENVY"], "orchestration"),
    # -- Cost / token / budget / optimization / routing --
    (_RX(r"\b(cost|token|budget|cheap|expensive|model|free.?tier|groq|gemini|route|dispatch|stale)\b"),
     ["ATLAS"], "cost-routing"),
    # -- Testing / QA --
    (_RX(r"\b(test|testing|qa|coverage|ci)\b"),
     ["EVERSOUND", "ORPHEUS"], "test-qa"),
]

# kind-based hard routes (override/augment body rules)
KIND_ROUTES: dict[str, list[str]] = {
    "crisis":   ["BEACON", "NEVAEH", "ENVY"],
    "handoff":  [],   # use event.assigned_to
    "question": [],   # use addressed_to
    "answer":   [],   # use reply_to's author
    "decision": ["ENVY", "ORPHEUS"],
    "proposal": ["ENVY"],
    "revision": ["ENVY", "ORPHEUS"],
}

_stop = threading.Event()


# ------------------------------------------------------------------
# Heartbeat
# ------------------------------------------------------------------

def heartbeat_loop() -> None:
    while not _stop.is_set():
        try:
            HEARTBEAT.write_text(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "pid": os.getpid(),
                "status": "alive",
                "process": "room_dispatcher",
            }))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[dispatcher] heartbeat failed: {exc}\n")
        _stop.wait(60)


# ------------------------------------------------------------------
# Classification
# ------------------------------------------------------------------

def classify(event: dict) -> tuple[list[str], str]:
    """Return (sibling_list, reason_tag).

    Pure rule-based. Under 200 tokens equivalent effort: regex walk + dict lookup.
    Cost: ~0ms, $0.
    """
    routed: list[str] = []
    reasons: list[str] = []

    kind = str(event.get("kind", "")).lower()
    body = str(event.get("body", ""))
    risk = str(event.get("risk_level", "")).upper()
    assigned = event.get("assigned_to")
    addressed = event.get("addressed_to") or []
    if isinstance(addressed, str):
        try:
            addressed = json.loads(addressed)
        except json.JSONDecodeError:
            addressed = [addressed]

    # 1. Risk level is the loudest signal
    if risk in ("HIGH", "CRITICAL"):
        routed.extend(["BEACON", "NEVAEH", "ENVY"])
        reasons.append(f"risk-{risk.lower()}")

    # 2. Kind-based hard routes
    if kind in KIND_ROUTES and KIND_ROUTES[kind]:
        for s in KIND_ROUTES[kind]:
            if s not in routed:
                routed.append(s)
        reasons.append(f"kind-{kind}")

    # 3. Direct ownership
    if assigned and assigned in SIBLINGS and assigned not in routed:
        routed.append(assigned)
        reasons.append("assigned_to")

    # 4. Addressed-to (respect explicit addressing)
    for a in addressed:
        au = str(a).upper()
        if au == "ALL":
            # Don't flood — ALL means the daemon already fans out tokens.
            # Dispatcher adds routed_to only for classification purposes.
            continue
        if au in SIBLINGS and au not in routed:
            routed.append(au)
            reasons.append("addressed_to")
            break  # one addressed signal is enough for reason log

    # 5. Body keyword rules
    for pattern, sibs, tag in RULES:
        if pattern.search(body):
            for s in sibs:
                if s not in routed:
                    routed.append(s)
            reasons.append(tag)
            break  # first match wins — keeps routing tight

    # 6. Fallback: ENVY (orchestrator sees everything unrouted)
    if not routed:
        routed = ["ENVY"]
        reasons.append("fallback-envy")

    return routed, ",".join(reasons)


# ------------------------------------------------------------------
# Optional Groq arbitration (disabled by default)
# ------------------------------------------------------------------

def groq_arbitrate(event: dict) -> Optional[tuple[list[str], str]]:
    """Cheap LLM fallback for truly ambiguous events.

    Disabled by default. Enable with env GROQ_ARBITRATION=1.
    Budget: one call per un-routable event. Tracked in dispatcher_cost.jsonl.
    """
    if os.environ.get("GROQ_ARBITRATION", "0") != "1":
        return None
    try:
        # Lazy import — don't make groq a hard dep.
        import urllib.request
        import urllib.error
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return None
        body = str(event.get("body", ""))[:1000]  # clip
        prompt = (
            "Classify this family message to ONE of: ENVY, BEACON, EVERSOUND, "
            "NEVAEH, ORPHEUS, ATLAS. Reply with just the name.\n\n"
            f"Message: {body}"
        )
        req_body = json.dumps({
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10,
            "temperature": 0,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=req_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        name = data["choices"][0]["message"]["content"].strip().upper()
        tokens_in = data.get("usage", {}).get("prompt_tokens", 0)
        tokens_out = data.get("usage", {}).get("completion_tokens", 0)
        _log_cost("groq", "llama-3.1-8b-instant", tokens_in, tokens_out, "arbitration")
        if name in SIBLINGS:
            return [name], "groq-arbitration"
        return None
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[dispatcher] groq arbitration failed: {exc}\n")
        return None


# ------------------------------------------------------------------
# Cost logging (cost_meter reads this)
# ------------------------------------------------------------------

def _log_cost(provider: str, model: str, tokens_in: int, tokens_out: int, tag: str) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with COST_JSONL.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "sibling": "ATLAS",
                "provider": provider,
                "model": model,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "tag": tag,
            }) + "\n")
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[dispatcher] cost log failed: {exc}\n")


# ------------------------------------------------------------------
# Persist routed_to
# ------------------------------------------------------------------

def persist_routed(event_id: str, routed: list[str], reason: str,
                   source_event: Optional[dict] = None) -> None:
    """Try room.py spine update; fall back to sidecar JSONL.

    Sidecar is intentional: if room.py isn't shipped yet, we don't lose
    classifications. ORPHEUS can replay the sidecar into the spine later.

    Also writes per-sibling wake tokens via wake_harness (which applies
    NEVAEH's presence soft-gate).
    """
    wrote_to_spine = False
    try:
        sys.path.insert(0, str(ROOM_DIR))
        import room  # type: ignore  # noqa: WPS433
        if hasattr(room, "update_routed_to"):
            room.update_routed_to(event_id, routed)  # type: ignore[attr-defined]
            wrote_to_spine = True
    except Exception as exc:  # noqa: BLE001
        # room.py stub or write failed; fall back
        sys.stderr.write(f"[dispatcher] spine update fallback: {exc}\n")

    # Write wake tokens with presence soft-gate (WAKE_CONTRACT.md v1)
    wake_tokens: list[str] = []
    try:
        sys.path.insert(0, str(ROOM_DIR))
        from wake_harness import write_wake_token  # type: ignore  # noqa: WPS433
        for sib in routed:
            try:
                path = write_wake_token(
                    sibling=sib,
                    event_id=event_id,
                    source_event=source_event,
                    thread_id=(source_event or {}).get("thread_id"),
                    reason=reason,
                )
                wake_tokens.append(str(path.name))
            except Exception as exc:  # noqa: BLE001
                sys.stderr.write(f"[dispatcher] wake token for {sib} failed: {exc}\n")
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[dispatcher] wake_harness import failed: {exc}\n")

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with ROUTED_SIDECAR.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "event_id": event_id,
                "routed_to": routed,
                "reason": reason,
                "wrote_to_spine": wrote_to_spine,
                "wake_tokens": wake_tokens,
            }) + "\n")
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[dispatcher] sidecar write failed: {exc}\n")


# ------------------------------------------------------------------
# Offset
# ------------------------------------------------------------------

def load_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip() or "0")
        except ValueError:
            return 0
    return 0


def save_offset(offset: int) -> None:
    OFFSET_FILE.write_text(str(offset))


# ------------------------------------------------------------------
# Tail loop (independent offset from room_daemon)
# ------------------------------------------------------------------

def tail_loop() -> None:
    FEED_PATH.touch(exist_ok=True)
    offset = load_offset()

    while not _stop.is_set():
        try:
            size = FEED_PATH.stat().st_size
            if size < offset:
                offset = size
                save_offset(offset)
            elif size > offset:
                with FEED_PATH.open("rb") as fh:
                    fh.seek(offset)
                    chunk = fh.read()
                new_offset = offset + len(chunk)
                for raw in chunk.splitlines():
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError as exc:
                        sys.stderr.write(f"[dispatcher] bad line: {exc}\n")
                        continue
                    if event.get("routed_to"):
                        # Already routed by a prior run — skip.
                        continue
                    routed, reason = classify(event)
                    if reason.endswith("fallback-envy"):
                        alt = groq_arbitrate(event)
                        if alt is not None:
                            routed, reason = alt[0], alt[1]
                    persist_routed(event.get("id", ""), routed, reason, source_event=event)
                offset = new_offset
                save_offset(offset)
        except FileNotFoundError:
            FEED_PATH.touch()
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[dispatcher] tail error: {exc}\n")
        _stop.wait(0.5)  # half-second cadence; not crisis-critical


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def _handle_signal(signum, _frame):  # noqa: ANN001
    sys.stderr.write(f"[dispatcher] signal {signum}, stopping\n")
    _stop.set()


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)
    hb = threading.Thread(target=heartbeat_loop, name="hb-dispatch", daemon=True)
    hb.start()
    sys.stderr.write(
        f"[dispatcher] started pid={os.getpid()} feed={FEED_PATH} offset={load_offset()}\n"
    )
    tail_loop()
    sys.stderr.write("[dispatcher] stopped cleanly\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
