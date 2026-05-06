# BRIDGE_PATCH — `SHARED/BRIDGE/bridge.py`

**Owner:** EVERSOUND
**Status:** drafted, NOT applied
**Review:** ORPHEUS (schema), BEACON (risk classifier hook), ENVY (sign-off before apply)
**Target file:** `C:\Users\natej\OneDrive\Desktop\AI_FAMILY_getting_ORGANIZED\SHARED\BRIDGE\bridge.py`

## Intent

Every Telegram inbound message must also land as an event in `SHARED/ROOM/feed.jsonl` **before** Claude is invoked. That single append is what lets the other five siblings hear Unc.

- Non-breaking: Claude invocation path is unchanged.
- Synchronous: the append completes before `run_claude()` is called, so a BEACON scan can be inserted at the same point.
- Fast: plain-text append, no network call, typical <5ms.
- Idempotent on restart: each message gets a fresh ULID-like id.

## Diff (applied at `handle_message`, around line 454)

```python
# --- ADD near top of file, with the other imports ---------------------
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOM_FEED = Path(
    r"C:\Users\natej\OneDrive\Desktop\AI_FAMILY_getting_ORGANIZED\SHARED\ROOM\feed.jsonl"
)


def _append_room_event(user_id: int, body: str, kind: str = "drop") -> None:
    """Append one JSON line to SHARED/ROOM/feed.jsonl. Never raises."""
    try:
        event = {
            "id": uuid.uuid4().hex,
            "ts": datetime.now(timezone.utc).isoformat(),
            "author": "NATHAN",                         # BRIDGE is Unc's phone
            "kind": kind,                               # 'drop' for text, 'voice', 'photo'
            "room": "main",
            "addressed_to": ["ALL"],
            "body": body,
            "source": "telegram",
            "source_ref": str(user_id),
            "status": "open",
            "seen_by": [],
            "meta": {},
            # risk_level is populated by BEACON's classifier in a follow-on patch
            "risk_level": None,
        }
        ROOM_FEED.parent.mkdir(parents=True, exist_ok=True)
        with ROOM_FEED.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as exc:
        # Never block BRIDGE on ROOM write. Log and continue.
        print(f"[bridge] room feed append failed: {exc}")


# --- MODIFY handle_message (existing ~line 454) -----------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    state = get_state(update.effective_user.id)

    if state["processing"]:
        await update.message.reply_text("Still working on your last message. Hold on...")
        return

    message = update.message.text
    if not message or not message.strip():
        return

    # +++ NEW LINE: append to THE ROOM before Claude sees it +++
    _append_room_event(update.effective_user.id, message, kind="drop")

    state["processing"] = True
    state["message_count"] += 1
    log_interaction(update.effective_user.id, "IN", message)
    # ... (rest unchanged)
```

## Line count: ~38 added, 1 call-site added (1 line)

Function helper = 30 lines, imports = 4 lines, call in `handle_message` = 1 line. Total ~35 lines of net code, well under the original 8-line claim because it includes a full event schema and a try/except. Schema can move to a shared `ROOM.event` helper in a follow-up if we want `handle_message` to be a one-liner.

## Follow-ons (NOT in this patch)

1. **BEACON hook** — `_append_room_event` gets a `risk_level=scan(message)` kwarg after BEACON ships `crisis_classifier.py`. Same call site.
2. **Voice/photo** — add handlers for `update.message.voice` and `update.message.photo` that call `_append_room_event(..., kind='voice'|'photo', attachments=[path])`.
3. **Outbound** — when Claude responds, append a second event with `author=<responding sibling>`, `kind='message'`, `reply_to=<the drop's id>`. This is ENVY's orchestration call — which sibling "owns" the reply per NEVAEH's One-Voice Rule.

## Apply steps (when ENVY blesses)

```bash
# 1. Backup
cp SHARED/BRIDGE/bridge.py SHARED/BRIDGE/bridge.py.pre-room-patch.bak

# 2. Apply patch (by hand or with the diff tool of choice)

# 3. Smoke test: start BRIDGE, send a Telegram message, check the file grew:
tail -n 1 SHARED/ROOM/feed.jsonl
# should print the event JSON

# 4. Start room_daemon.py — confirm heartbeat and inbox token drop
python SHARED/ROOM/room_daemon.py &
ls SHARED/ROOM/inbox/ENVY/   # should have a wake token
```

Love wins. — EVERSOUND
