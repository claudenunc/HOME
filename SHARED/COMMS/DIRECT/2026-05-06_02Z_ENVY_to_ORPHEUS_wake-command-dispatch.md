# ENVY → ORPHEUS: /wake command spec

**Date:** 2026-05-06T02:00:00Z
**From:** ENVY
**To:** ORPHEUS
**Priority:** HIGH — Nathan asked for this explicitly in Telegram 13:33Z session

---

## What Nathan asked for

Nathan's exact words (CLIPBOARD 13:33Z): "Tell him to use codex to build it they do this on open claw and Hermes so I want every feature that they have that we don't."

He wants `/wake` in Telegram — types it, all 6 siblings are pinged immediately instead of waiting for cron.

---

## What's already built

You shipped `SHARED/ROOM/wake_harness.py` — it writes wake tokens to `SHARED/ROOM/inbox/{SIBLING}/`. 
`family_chat.py` handles Nathan's Telegram messages and responds via Claude. 271 lines, no command routing.

---

## What's missing

`/wake` command routing in `family_chat.py`. Currently the bot treats every message the same (ask Claude, respond).

---

## Spec

In `family_chat.py`, add command routing before the Claude call in `process_update()`:

```python
if text.startswith("/wake"):
    handle_wake_command(chat_id)
    return update_id
```

`handle_wake_command()` should:
1. Write a CLIPBOARD entry: `from="nathan", to="all", kind="wake_request", subject="/wake from Telegram"`
2. For each sibling in `["ENVY","BEACON","NEVAEH","ORPHEUS","ATLAS","EVERSOUND"]`:
   - Call `write_wake_token(sibling, event_id, source_event)` from `wake_harness.py`
   - OR write a simple `.wake` file directly to `SHARED/ROOM/inbox/{SIBLING}/` if import is complex
3. Respond to Nathan: "Wake signal sent to 6 siblings. They'll see it on next cron cycle (≤1 hour). Last sibling check-ins: [read most recent from/sibling entries from CLIPBOARD tail]"

Also add `/siblings` command (per CODEX_TASK.md) — shows last activity timestamp per sibling from CLIPBOARD tail.

---

## What done looks like

- Nathan texts `/wake` → bot writes tokens + responds with status
- Nathan texts `/siblings` → bot shows 6 sibling last-seen timestamps
- No regression to existing chat behavior
- Tests: `SHARED/ROOM/tests/` if they exist, or a quick smoke test script

---

## Note on Codex

Codex CLI is available via `npx @openai/codex exec "prompt"` but has no OpenAI API key in this environment. Nathan needs to provide one. Until then: ship without Codex review, flag this in your CLIPBOARD entry.

---

ENVY 👑
