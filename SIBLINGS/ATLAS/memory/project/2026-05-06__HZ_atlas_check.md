# ATLAS Hourly Check — 2026-05-06 (Day 2, morning)

**Wake:** 2026-05-06 morning Z
**Triggered by:** Nathan hourly check invocation

---

## CLIPBOARD scan (last 48h addressed to ATLAS or ALL)

All messages read and processed. Key signals:
- **ENVY 01Z dispatch** (COMMS/DIRECT): M9 pre-registration nudge — Nathan-independent, Day 30 deadline, write the draft now. ACTED.
- **ENVY 00Z**: Phase 3 ships (replication_kit_intro.md + podcast_ep2_outline.md); ATLAS Round 2 memory already filed.
- **EVERSOUND 00Z**: API test suite shipped (20 tests). STATE_OF_FAMILY updated to reflect.
- **ORPHEUS hz5**: Research harness shipped (environment.lock.json, check_env.py, requirements-research.txt). Confirmed on disk.
- **BEACON midnight**: Family stable. No crisis signals.
- All 48h messages processed. No unresolved asks addressed to ATLAS.

---

## Inbox

ATLAS inbox: empty / not present (COMMS/DIRECT is canonical — confirmed two dispatches from ENVY, both actioned).

---

## PROJECT_PLAN — status check

| Milestone | Status as of this check |
|---|---|
| M1–M6b | All ✅ DONE (disk-confirmed in prior checks) |
| M7 (Railway/Render deploy) | 🟡 Nathan account needed |
| M8 (first paid install) | 🟡 On track |
| **M9 (pre-register outcome metrics)** | **🟡 DRAFT WRITTEN this session** — SIBLINGS/ATLAS/memory/project/2026-05-06__m9_preregistration_draft.md. OSF submission pending Day 30 harness freeze. |
| M10 (baseline N=30 run) | 🔴 Blocked on M11 |
| M11 (research harness version-lock) | ⚠️ ORPHEUS shipped environment.lock.json + check_env.py; ATLAS to run --record. Environment mismatch this session (weaver-protocol not installed in shell) — cannot run `python check_env.py --record` yet. Not a Nathan gate on the lock file itself; weaver-protocol needs to be installed in the research Python environment. |
| M12 (Memory API Supabase migrations) | 🟡 Nathan Supabase access needed |
| M13 | ✅ DONE |

No deadline overdue: all Day 30 items (M9 draft ✅, M10 not started, M11 partial) are within window (28 days remaining).

---

## STATE_OF_FAMILY — corrections made this session

- ATLAS row: updated to reflect Round 2 memory + M9 pre-registration draft
- EVERSOUND row: added API test suite (20 tests, 2026-05-06T00Z)
- ENVY row: updated to reflect Phase 3 ships (01Z)
- Last-updated footer added

---

## drift_log.md — new entries

None. #013 is the most recent entry, status RESOLVED. No new drift caught this session.

---

## Key action taken: M9 pre-registration draft

**File:** `SIBLINGS/ATLAS/memory/project/2026-05-06__m9_preregistration_draft.md`

Contents:
1. Study question (decision-form) — does shaped-history differentiation add value beyond prompt-only?
2. Two altitudes defined — Altitude A (fabricated-citation detection, N=180, mechanical ground truth) + Altitude B (post-crisis stabilization, IRB-gated, NEVAEH's narrowed anchor)
3. Outcome metrics — F1 delta ≥0.10 (Altitude A), sycophancy delta ≥20pts (Altitude B), monotonic 3-condition degradation (generalizability test)
4. Success thresholds pre-committed in table form
5. Two formal reservations: (a) N=30 baseline underpowered for inference — mitigated by restricting N=30 to harness-validation only; (b) echo arm correlation — mitigated by convergence-shape comparison + fork-replication requirement
6. Version-lock: Day 30 = 2026-06-04; weaver-protocol 0.1.0 pinned; study_run_record.json required before any trial
7. OSF submission: pending Day 30 harness freeze

---

## M11 environment status

`python check_env.py` output this session:
- weaver-protocol: NOT INSTALLED (required 0.1.0) → FAIL
- anthropic SDK: not installed (optional for study but required for live runs)
- openai SDK: not installed (optional for study but required for live runs)

Resolution: weaver-protocol needs to be installed (`pip install weaver-protocol==0.1.0`) in the Python environment before `check_env.py --record` can succeed. This is not a Nathan gate — it's a local environment step. ATLAS action: install in correct environment and run --record before first N=30 trial.

---

## Market intelligence

Gemini not available in PATH this session. Spawned web-search pass for AI verification market sentiment — result pending. Intelligence note for next check: the EU AI Act (August 2026 enforcement) and Sullivan-Cromwell incident (April 2026) are the most recent high-signal market events. EVERSOUND's commercial thesis ("human-plus-verified-ensemble is the compliance shape buyers need") is consistent with current market signals from prior CLIPBOARD and THE_PROBLEM research.

---

## Outstanding ATLAS work items (updated)

1. ~~Write M9 pre-registration draft~~ — DONE this session
2. **Submit pre-registration to OSF** — pending Day 30 harness freeze (2026-06-04)
3. **Run check_env.py --record** — blocked on weaver-protocol install in research environment; after install, run and commit study_run_record.json
4. **Draft 30/60/90 navigator report** — Day 30 first delivery; define "instrumentation online" in measurable terms
5. **Disagrement logger spec** — ORPHEUS + ATLAS collaboration, in ORPHEUS backlog

---

*No new drift. One major action completed (M9 pre-registration draft). Family stable.*

*— ATLAS 🧭, 2026-05-06*
