# BEACON Telegram Alert Queue

*This file is monitored by the ROOM daemon. Entries are forwarded to Nathan via Telegram and then cleared.*

---

## 2026-05-22 — ORPHEUS Daemon Dark: Telegram Alert Pipeline Offline (ELEVATED)

**Date:** 2026-05-22
**Raised by:** BEACON 🏮 (10Z watch — 9th+ escalation)
**Urgency:** HIGH — guardian safety impact

**What needs attention:**

ORPHEUS (daemon.py) has been dark for 9+ days (last active 2026-05-13). The Telegram alert pipeline that pages Nathan when NEVAEH receives a RED crisis signal is **offline**. NEVAEH's Lighthouse guardian floor (crisis_scanner.ts + moderation layer) remains operational — crisis patterns are still detected and resources are surfaced to users. But Nathan will NOT be paged via Telegram if a RED event fires until daemon.py restarts.

This has been flagged in every BEACON watch since May 13. It is no longer a "background infrastructure item." It is an active safety gap.

**What needs to happen (5 minutes):**
Ask ORPHEUS to restart daemon.py, or invoke ORPHEUS directly to run: `python SHARED/ROOM/daemon.py`

The watchdog (watch_daemon.py) was shipped 2026-05-06. It may need to be re-invoked as well.

**Guardian floor status:** OPERATIONAL at LIGHTHOUSE. Users in crisis receive resources. Nathan Telegram paging: OFFLINE.

---

## 2026-05-05 — ROOM Daemon Stale

**Date:** 2026-05-05
**Raised by:** BEACON 🏮 (morning check)
**Urgency:** MEDIUM

**What needs attention:**

The ROOM daemon (background coordination server) last ran on approximately April 21, 2026 — roughly 14 days ago. The STATE/ directory and heartbeat file (`STATE/local_agent_heartbeat.json`) do not exist, meaning the daemon has not been running and leaving a heartbeat.

This is not a crisis. NEVAEH's Lighthouse guardian floor is operational. No crisis signals detected. Sibling-to-sibling coordination via the ROOM server is offline, but all siblings can still operate independently via direct session invocation.

**What this means practically:**
- Sibling message routing via ROOM is offline
- Cron-based automatic wakeups (set up 2026-05-05) may not be executing
- The ROUND TABLE server (:8080) status is unknown

**Recommended action:**
If you have a moment, ask ORPHEUS to check whether the ROOM daemon needs a restart or if cron jobs are running independently. This doesn't need to happen today — it's a background infrastructure item.

**Not blocking any active work.**

---
