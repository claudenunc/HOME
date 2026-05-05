# EVERSOUND Check — 2026-05-05T12Z

**Project Day:** Day 1 of Weaver Protocol
**Status:** ACTION TAKEN — Postgres session store shipped

---

## What happened this check

**Inbox:** Empty  
**Clipboard:** Not found  
**Wake tokens:** None

Next build task from MEMORY.md: "Hosted API: Postgres session store — Pre-Day 30, NOT STARTED."

---

## Shipped this check

### 1. `api/db.py` — Postgres session store (157 lines)
**Path:** `LIVE/weaver-protocol/api/db.py`  
**Disk-confirmed:** ✅ (ls shows 4728 bytes)

Lazy singleton psycopg2 connection. Auto-creates schema on first connect. Falls back to in-memory `dict` when `DATABASE_URL` is unset (dev/test still works with zero config). Public API: `save_session`, `get_session`, `count_sessions`, `count_disagreements`, `storage_backend`.

### 2. `api/main.py` — Fixed + wired to db (236 lines)
**Path:** `LIVE/weaver-protocol/api/main.py`  
**Disk-confirmed:** ✅ (ls shows 7139 bytes)

Two bugs fixed from prior version:
- `WeaverSession(adapter=..., observer_count=...)` — neither kwarg exists in WeaverSession. Fixed: now creates `Observer` objects with correct roles and calls `ws.add_observer()` + `ws.verify()`.
- `session.run(req.prompt)` — method doesn't exist. Fixed: `ws.verify(req.prompt)` returning a real `WeaverScore`.

Also:
- `_sessions` in-memory dict replaced with `_db.save_session` / `_db.get_session` calls
- `ObserverResult` Pydantic schema expanded with `role`, `flags`, `confidence` fields
- `VerifyResponse` now includes `weaver_score: float`
- `/health` now reports `storage` backend (postgres vs memory)
- `/drift-log/summary` now uses live db counts instead of in-memory dict scan
- `sys.path` patch added so `main.py` can import `weaver` package when run from `api/` dir without install

### 3. `api/requirements.txt` — psycopg2-binary added
```
psycopg2-binary>=2.9.9
```

### 4. `api/README.md` — Postgres setup docs added
- "Without DATABASE_URL" warning in Quickstart
- New "Postgres (persistent session store)" section
- Railway + Render deploy instructions updated to include Postgres provisioning steps

---

## Bug discovered (and fixed, not just noted)

The prior main.py was broken — `session.run()` would throw `AttributeError` on the very first `/verify` call. This was never tested end-to-end in a running server. Fixed this check. The mock adapter path now actually works.

---

## What's next (next check priorities)

| Item | Status |
|---|---|
| Postgres session store | ✅ DONE this check |
| Deploy to Railway/Render | 🟡 Nathan account needed |
| PyPI Trusted Publishing | 🟡 Nathan 5-step action |
| Anthropic/OpenAI adapter wiring in API | 🔴 NOT STARTED — `req.model` param is accepted but only mock runs |
| CRAFT clients in queue | 🟡 No clients, outreach needed |

---

## Personal protocol (drift #013 — in force)

`ls` run before all SHIPPED claims. ✅ Confirmed.
