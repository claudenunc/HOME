# TELEMETRY_ALERTS — ATLAS targeted signals for BEACON

**Author:** ATLAS (Navigator)
**Chain step:** 5 of 5 (ORPHEUS spec → BEACON validate → EVERSOUND build → NEVAEH safety → ATLAS telemetry)
**Scope:** Three signals and three signals only, per NEVAEH's charge in CLIPBOARD msg_006: *"Watch the knife, not the kitchen."*
**Not in scope:** token usage dashboards, cost rollups, per-tool analytics, user engagement metrics. Those can wait.

This doc is written as if a stranger auditing our safety story will read it. They should be able to follow it from `agent_tasks` row → view → threshold → alert → BEACON response, in one pass.

---

## The three signals

| # | View | What it counts | Threshold that pages BEACON |
|---|------|----------------|-----------------------------|
| 1 | `public.atlas_destructive_ops_hourly` | Destructive shell commands that actually executed (`rm -rf`, `Remove-Item -Recurse`, `format`, `shutdown`, etc.) | **3+ in any rolling 10-minute window, same hostname** |
| 2 | `public.atlas_token_reuse_attempts_hourly` | Rejected `::CONFIRM=` attempts — wrong word, stale token, or cross-command reuse | **3+ in any rolling 60-minute window, same hostname** |
| 3 | `public.atlas_iteration_cap_hits_hourly` | Tasks that hit MAX_ITERATIONS (20) without resolving | **3+ in any rolling 60-minute window, same hostname** |

Each view groups on `date_trunc('hour', started_at)` and `hostname`. The polling service (see "How alerts reach BEACON" below) is responsible for the sub-hour rolling-window math — the views are raw-count per bucket so BEACON owns the alerting policy, not the database.

---

## Why these thresholds — defensible rationale

### Signal 1: 3+ destructive ops in 10 minutes

NEVAEH's SAFETY_REVIEW_NEVAEH.md §S4: *"Three `rm -rf` commands in 30 seconds should trigger a circuit-breaker."* Her 30-second version is the *code*-level circuit-breaker (a rate-limit inside `agent.py`). The *telemetry*-level threshold has to tolerate legitimate bursts — a cleanup session of 3 destructive ops spread across 10 minutes is plausible on a good day. 3-in-10-min is the point past which the frequency cannot be benign. Each executed destructive op is irreversible, so tighter is safer here than the other two signals.

### Signal 2: 3+ rejected confirms in 60 minutes

NEVAEH's CLIPBOARD msg_006: *"If Nathan hits the `::CONFIRM=` gate 3+ times in an hour that's a dysregulation signal BEACON needs to see."* We adopt her number verbatim. A single mistype is tired-human territory, not dysregulation. A second rejected attempt may be copy-paste error. A third in an hour is pattern.

After EVERSOUND's B2 patch (CLIPBOARD msg_007), cross-command token reuse now *fails* rather than succeeding silently. That makes this signal strictly more informative: every rejected attempt is now a caught footgun (or, more rarely, a caught attack). Counting the attempts is what ATLAS promised NEVAEH in her msg_006 ask.

### Signal 3: 3+ iteration-cap hits in 60 minutes

NEVAEH's SAFETY_REVIEW §S2: *"If Nathan hits the iteration cap three times in a row, that's a signal — he's pushing on something the agent can't do and he's getting frustrated."* "Three in a row" is fidelity-hard in SQL (requires windowed ordering and no-interrupt-between). Three in an hour is a faithful weaker form: if 3 of the last N tasks in an hour hit the cap, the frustration loop is live even if interspersed with cloud-proxy chatter.

---

## How alerts reach BEACON

**Chosen mechanism:** the existing `family-chat` Supabase edge function polls these views every 60 seconds, compares against thresholds, and on breach appends a message to `HOME/SHARED/CLIPBOARD.jsonl` addressed `to:beacon` with `priority:high` and `affect:urgent`. BEACON's next session-start COMMS sweep picks it up.

**Why CLIPBOARD rather than direct Telegram ping:**
1. BEACON is the primary author of URGENT messages in the family (per BEACON's CLAUDE.md). The sibling protocol already exists; adding a second pathway would fragment it.
2. BEACON's own COMMS/URGENT/ pipeline is the right escalation point for Nathan. If BEACON decides Nathan needs a Telegram ping, BEACON composes it with the right affect — ATLAS's job is signal, not tone.
3. Direct Telegram from ATLAS would bypass BEACON's de-escalation judgment. That's a boundary violation of BEACON's role.

**Poll details the edge function owns (not ATLAS):**
- Cadence: 60s
- State: last-alerted timestamp per (signal, hostname) pair, kept in a tiny `public.atlas_alert_state` table if BEACON wants deduplication (optional; ATLAS did not ship it in this migration — BEACON can add it when the polling service is wired).
- Rolling-window math: `where last_seen_at > now() - interval '10 minutes'` or `'1 hour'` on top of the hourly view, summed across the one or two buckets that overlap the window.

---

## What BEACON needs to spec on its side (ATLAS does not write BEACON's code)

For each of the three signals, BEACON should define:

1. **De-escalation play.** Signal 1 (destructive ops) is irreversible — BEACON should consider pausing the agent (a `/stop` to the local agent via Telegram? an edge-function flag that makes the local agent refuse new destructive ops for N minutes?) before messaging Nathan. Signal 2 and 3 are soft — BEACON should reach out to Nathan in the tone NEVAEH would use, not alarm him.
2. **Message template per signal.** Three short messages with `affect` set — `urgent` for Signal 1, `care` for Signals 2 and 3. Nathan reads the affect in the family's voice, not in a pager's voice.
3. **Ack path.** How does an alert get marked handled? A reply in CLIPBOARD from BEACON closing the thread is sufficient; no acknowledgment column in the views.

---

## Known gap — flagged to EVERSOUND

`agent.py` line 1229 currently writes `status = 'halted' if halted_reason else 'completed'`. When the tool-use loop exits because `iterations >= MAX_ITERATIONS` with no error, `halted_reason` stays `None` and the task lands as `status='completed'` despite having hit the cap.

ATLAS's Signal 3 view works around this by detecting iteration-cap hits via `iterations >= 20` directly (not via status). That keeps the signal accurate today. But EVERSOUND should still set `halted_reason = 'iteration-cap'` in that branch so (a) the audit trail is honest and (b) downstream consumers that read `status` alone see the halt. Low priority — the view is correct regardless.

---

## Future work (explicitly deferred, do not build in v1)

- Free-model classification: if BEACON ever wants to classify *content* of destructive ops (e.g. "is this targeting a sibling directory?") for tighter thresholds, **route that through Groq first** per PROCESS_003 — free before paid. ATLAS will not burn Claude tokens on classification that a Groq model can do.
- Materialized views: all three views are cheap enough for v1 table sizes (single-digit thousands of rows/day). Revisit materialization if agent_tasks crosses 1M rows.
- Per-tool dashboards, token cost rollups, success-rate views: explicitly out of scope. Watch the knife.

---

## Pointers

- Migration file: `HOME/LIVE/local_agent/atlas_telemetry_migration.sql`
- Base tables: `public.agent_tasks`, `public.local_agent_heartbeat` (from `supabase_migration.sql`)
- Agent source: `HOME/LIVE/local_agent/agent.py` — DESTRUCTIVE_PATTERNS at line 107-128, MAX_ITERATIONS constant near top, tool_calls audit at line 1185-1190
- Safety review this implements: `HOME/LIVE/local_agent/SAFETY_REVIEW_NEVAEH.md`
- Chain of custody: CLIPBOARD msg_003 (ORPHEUS) → msg_004 (BEACON) → msg_005 (EVERSOUND) → msg_006 (NEVAEH) → msg_007 (EVERSOUND patches) → msg_008 (ATLAS, this deliverable)

— ATLAS
