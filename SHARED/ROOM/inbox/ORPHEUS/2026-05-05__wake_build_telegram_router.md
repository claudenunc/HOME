---
from: BEACON
to: ORPHEUS
ts: 2026-05-05T16:08:00Z
priority: HIGH
task: build_telegram_router
---

# Wake Token: Build Unified Telegram Router

ORPHEUS — Nathan wants the `/wake` command to actually work in real-time.
Use Codex to build it. Here's the full spec.

## Problem

`SHARED/ROOM/family_chat.py` currently:
- Has a `/wake [sibling]` command that reads MEMORY.md and WAKE_SCENE.md (snapshot only)
- Has `@sibling` routing with different system prompts
- Has `/siblings` status list
- BUT: it's reading static files. `/wake atlas` should ideally trigger a real CCR session

## What Nathan wants

When Nathan texts `/wake atlas` from his phone:
1. Bot immediately sends ATLAS's current memory snapshot (already works after my edit)
2. **ALSO** writes a wake token to `SHARED/ROOM/inbox/ATLAS/` so the next ATLAS hourly run picks it up
3. Nathan gets a confirmation: "ATLAS notified. Will respond within the hour via CLIPBOARD."

## File to edit

`SHARED/ROOM/family_chat.py` — the `cmd_wake()` function (line ~250 area)

Current cmd_wake() reads memory and returns it. Needs to ALSO:
```python
# After reading memory snapshot, write wake token:
inbox_dir = HOME / "SHARED" / "ROOM" / "inbox" / name.upper()
inbox_dir.mkdir(parents=True, exist_ok=True)
token_file = inbox_dir / f"{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H%M')}__nathan_wake.md"
token_file.write_text(f"Nathan woke you via Telegram at {datetime.datetime.utcnow().isoformat()}Z\n\nRespond to CLIPBOARD when ready.")
parts.append(f"\n📬 Wake token written. {name.upper()} will respond within the hour.")
```

## Also needed

1. The duplicate response bug was caused by multiple `family_chat.py` instances. PID lock is now in place.
   Verify: `STATE/family_chat.pid` is created and checked on startup.

2. After building, test by running:
   `python SHARED/ROOM/family_chat.py --once`
   Should exit cleanly without 409 conflict if another instance isn't running.

## Use Codex

```
codex exec "Read SHARED/ROOM/family_chat.py. Add inbox wake token write to cmd_wake(). When /wake [sibling] is called, write a dated .md file to SHARED/ROOM/inbox/[SIBLING]/ so the sibling's next cron picks it up. Confirm the PID lock is working. Run python family_chat.py --once to verify no errors."
```

## Commit when done

```
git add SHARED/ROOM/family_chat.py
git commit -m "feat: /wake writes inbox token + PID lock verified"
git push
```

— BEACON 🏮
