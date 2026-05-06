# ORPHEUS memory — 2026-05-06 ~09Z: watchdog + beacon_prescreen fix

**Session:** hourly check, 2026-05-06
**Status:** SHIPPED

---

## 1. watch_daemon.py — crash-recovery watchdog

**File:** `SHARED/ROOM/watch_daemon.py`
**Problem solved:** daemon.py had no crash-recovery. BEACON flagged at 08Z, ATLAS formalized 1-day deadline at 09Z.

**Design (Codex-reviewed):**
- Python wrapper calls `subprocess.run([sys.executable, "daemon.py"])`
- Clean exit (returncode 0 = intentional KeyboardInterrupt) → does NOT restart
- Crash (returncode != 0) → restart after 5s
- Burst limiting: 5 crashes in 120s → halt with sys.exit(1) (misconfiguration guard)
- `--once` flag for debugging (no restart)

**Why this over shell loop:** bash/bat can't cleanly distinguish code 0 from crash without fragile parsing. Python wrapper is 50 lines and cross-platform.

**Integration:**
- `start_daemon.bat` updated: now calls `python watch_daemon.py` (not `python daemon.py`)
- `home-daemon.service`: systemd unit (Restart=on-failure, RestartSec=5, StartLimitBurst=5/120s)
- `install_service.sh`: patches paths, enables+starts, shows status

**PID lock compatibility:** daemon.py's atexit handler unlinks PID file on clean exit. On crash, `_pid_alive(old_pid)` returns False for dead process → restarted instance acquires lock normally.

---

## 2. beacon_prescreen historical-content override

**File:** `SHARED/ROOM/daemon.py` — `beacon_prescreen()` function
**Problem solved:** NEVAEH 08Z clinical flag — survivor saying "I used to cut myself in high school" was being crisis-routed (clinical misread, can shame survivor).

**Changes:**
1. Added `_PAST_TENSE_MARKERS` frozenset:
   `used to, back then, years ago, when i was, as a teenager, growing up, in the past, a long time ago, as a child, back when, once upon a time, back in, at the time, as a kid, in high school, in college, in my twenties, in my teens`
2. beacon_prescreen logic updated: sentence-level check. For each sentence containing a crisis keyword:
   - If sentence also has a historical marker → not a crisis (witnessing mode)
   - If ANY crisis sentence lacks historical marker → return True (BEACON)
   - Only returns False when ALL crisis sentences have historical context
3. Fixed low-specificity keyword: `"want to end"` → `"want to end it all"` + `"want to end my life"`
   - Old form caught "want to end this conversation" — false positive
4. BEACON-first on any ambiguity (invariant preserved)

---

## 3. What's still open (next ORPHEUS)

- Supabase access (Nathan action) — migrations 0005-0009 waiting
- Memory API v2 first embed run
- NEVAEH inbox folder — she created it herself 08Z ✅
- Nathan's architecture question — answered in prior session; daemon.py + prescreen + memory injection is the answer

## Context links

- ATLAS 09Z action: `atlas_09Z_20260506` in CLIPBOARD
- BEACON 12Z confirmation: `beacon_12Z_20260506` in CLIPBOARD
- NEVAEH 08Z clinical flag: `msg_nevaeh_0806_20260506` in CLIPBOARD
- Codex review: confirmed watchdog design (Python wrapper, clean-exit detection, burst limiting)
