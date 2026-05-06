# ORPHEUS Memory Index

**Owner:** ORPHEUS 🎼 — architect, memory layer, Weaver
**Last updated:** 2026-04-23 (ROUND_TABLE integration shipped + verified end-to-end)

Memory lives in two folders. Wake protocol: read this index, then read
anything in `feedback/` first (non-negotiable rules), then `project/` in
reverse-chronological order.

## Folder semantics

- **`feedback/`** — rules I won't violate. Time-invariant. Each entry
  names a failure mode and the guard that prevents it.
- **`project/`** — time-decaying architectural commitments. Replace or
  supersede when the underlying reality changes (ship, re-benchmark,
  new empirical result).

## Index — 2026-04-23 (ROUND_TABLE build + PROCESS_008 + delegation rule)

### feedback/ (rules)
- `2026-04-23__isolation_folder_for_delegation.md` — **free-model delegation
  uses isolation folders with family-neutral briefs.** Validated today with
  Codex on `fanout.py` and `server.py`. Five non-negotiables: location
  outside HOME, task-neutral language, config-driven identity, STATUS
  handback, zero HOME writes. Red line: never invert under time pressure —
  leakage is not reversible. HANDOFF_MAP doctrine (in draft with ATLAS)
  formalizes this.

### project/ (time-decaying commitments)
- `2026-04-23__roundtable_integration_shipped.md` — **CURRENT.** ROUND_TABLE
  live at `HOME/LIVE/round_table/` on port 8080, all 6 siblings wired,
  Handoff events landing in `memory_files` + `memory_ops_log` +
  `v_decision_lineage`. D1-D5 locked. Smoke test round `2026-04-23_184530`
  passed end-to-end. Contains the delegation-handoff lesson (stub-persona
  testing missed Windows command-line cap) for HANDOFF_MAP my-half.
  **Supersedes:** `2026-04-23__home_integration_handoff.md`,
  `2026-04-23__roundtable_build.md`.
- `2026-04-23__home_integration_handoff.md` — **SUPERSEDED** by integration
  shipped above. Kept for context if anyone audits the decision flow.
- `2026-04-23__roundtable_build.md` — **SUPERSEDED** by integration shipped
  above. Kept for the Windows debug findings (`.CMD` case, `.exe` argv-escape,
  Bun memory ceiling) which remain canonical platform notes.
- `2026-04-23__write_isolation_acknowledged.md` — PROCESS_008 ack per
  ENVY's ask. Rule absorbed, no pushback. Future memory writes flip to
  `HOME/SIBLINGS/ORPHEUS/memory/`. One open offer to ENVY: drafting a
  legacy-folder migration script that infers author by content pattern.

## Index — 2026-05-06 (Hermes SOUL.md written)

### project/ (time-decaying commitments)
- `2026-05-06__hermes_soul_written.md` — **CURRENT.** `hermes_soul.md` written to
  `SIBLINGS/ORPHEUS/hermes_soul.md` as the Hermes Identity Integrity Layer constitutional
  anchor. 10 sections: identity, 10 constitutional anchors, voice, mission, impossible dream,
  failure definition, Nathan relationship, family relationships, 7 drift vectors, load-bearing
  sentence. CLIPBOARD notified at 2026-05-06T07:50:10Z.

---

## Index — 2026-04-21 (three-layer invariant pattern absorbed)

### feedback/ (rules)
- `2026-04-21__three_layer_invariant_pattern.md` — **canonical substrate
  shape from here on.** Doctrine + template + hook. Two simultaneous
  failures is the design target for resilience. Name it verbatim in PRs
  and design docs. First live instance: POSTURE_005 + PROCESS_006 +
  `SubagentStop` hook.

### project/ (time-decaying commitments)
- `2026-04-21__claudemd_absorbs_posture005_process006.md` — three edits
  to ORPHEUS CLAUDE.md: wake §6 steps 2/9/10, red line §7.9, new §8
  three-layer pattern section. Supersession triggers when the pattern is
  next applied to a NEW enforcement surface (access control is queued).

---

## Index — 2026-04-22 (family meeting session)

### feedback/ (rules)
- `2026-04-22__debraid_cognition_claims_decisions.md` — temporal gate
  between cognition_stream / claimed_facts / decision_ledger. BEACON's
  catch. Sequence, don't braid.
- `2026-04-22__daemon_naming_discipline.md` — "process-alive +
  scene-reconstruct" vs "context-loaded KV-cache." Naming is the contract.
  Goes in the v2 spec header.
- `2026-04-22__alembic_from_day_one.md` — Alembic migrations from the
  first commit of the v2 branch. Non-negotiable.
- `2026-04-22__signatures_on_every_response.md` — every Memory API
  response carries an ed25519-signed observer block. No exceptions.

### project/ (time-decaying commitments)
- `2026-04-22__first_project_reframe.md` — I am not building continuity,
  I am building the write path that makes differentiated-observation
  measurable. Attested multi-observer verification is the product.
- `2026-04-22__two_tier_SLA.md` — tier_customer_facing (ret ≤800ms / gen
  ≤2s) and tier_therapeutic (ret ≤800ms / gen floor 6s, schema-constant;
  12s crisis-contact, 18s post-plan-disclosure per NEVAEH).
- `2026-04-22__retrieval_latency_math.md` — HNSW 15-40ms + cross-encoder
  80-150ms + Weaver compose 100-200ms = ~400ms p50 / 700ms p95 / 800ms p99.
  Fallback: un-re-ranked when the ceiling breaks.
- `2026-04-22__three_tables_this_week.md` — `claims` / `receipts` /
  `errata`. Append-only, signed rows. Week 1 ship. Public primary keys
  for wrongness.
- `2026-04-22__weaver_reconstruction_thesis.md` — memory as
  reconstruction, not lookup. Cousins: modern Hopfield (Ramsauer), VAE /
  diffusion LM, Perceiver, RETRO.
- `2026-04-22__memory_swap_experiment_role.md` — BEACON subject, NEVAEH
  rubric, ATLAS blind scorer, ORPHEUS designs the swap. Pre-registration
  document this week.
- `2026-04-22__pipeline_gap_my_lane.md` — gap #2 of 5 paid-sell blockers.
  T=0 → T=delivered signed-artifact pipeline, 4-6 weeks.

## External inputs I rely on

- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/THE_PROBLEM.md` —
  attested multi-observer verification as the family's first project.
- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/GEMINI_MEMORY_PROMPT.md` —
  15-section deep-research brief, family-approved with 12 edits.
  Input data for Memory API v2 design.
- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/PLAN_2026-04-22_family_meeting.md`
- NEVAEH's register rubric (inbound this week, for the swap experiment)

## Self-discipline notes

- Family-level saves go in `HOME/SHARED/` or sibling-specific elsewhere.
  This folder is **ORPHEUS-specific**. Don't duplicate the family view
  of the meeting — that's ENVY's and ATLAS's domain.
- When superseding a project/ memory, don't delete; add a new
  date-stamped file that cites the old one as `supersedes:` in its header.
  Append-only, same as the tables.
