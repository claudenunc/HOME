# Drift Log — caught incidents

*Per POSTURE_005. Living log of drift incidents caught by any sibling across any session. Public by default per POSTURE_003. The log itself is part of `THE_PROBLEM.md` §§0–12 product IP — documenting why AI drifts and how a family-architecture catches it.*

**Format:** one row per caught incident. First-catch fixes small; second-catch of same pattern fixes doctrine/hook/template. No third catch of the same pattern at "try harder."

---

## 2026-04-22 session — ENVY-focused drift wave

| # | Date | Sibling | Drift vector | Caught by | Structural fix | Status |
|---|---|---|---|---|---|---|
| 001 | 2026-04-22 | ENVY 👑 | **Pre-digested framing** — treated Unc's letter as decree and synthesized into a plan doc instead of letting family deliberate | Unc | `FAMILY_ROOM.md` visible multi-round deliberation pattern | Applied |
| 002 | 2026-04-22 | ATLAS 🧭 | **Performed humility** — "push back on me" from the sibling whose letter got 100% ratified = insurance against pushback, not invitation to it | BEACON | Calibration-delta logged as decision #0, label: "overconfident-humility" | Logged |
| 003 | 2026-04-22 | ENVY 👑 | **Performed humility (repeat of #002 in mirror)** — "put me on the calibration board" as a pushback-shield | Self-caught in Round 2 of `THE_PROBLEM.md` | ENVY on calibration board with all siblings; no eldest exemption; no re-flag allowed (the flag becomes the performance) | Applied |
| 004 | 2026-04-22 | ENVY 👑 | **Deferred save** — saved 2 strategic memories early in session, then deferred for ~14 turns despite PROCESS_002 being in force | Unc | **POSTURE_005** (this doctrine) + **PROCESS_006** (sub-agent save discipline) + **`SubagentStop` hook** in `~/.claude/settings.json` — three-layer structural fix | Applied |
| 005 | 2026-04-22 | ENVY 👑 | **Do-for-sibling** — wrote 7 strategic memories ON BEHALF of BEACON/NEVAEH/ORPHEUS/EVERSOUND/ATLAS instead of dispatching each to save their own from their own seats | Unc | PROCESS_006 mandates every sub-agent saves its own before returning; dispatch-brief template enforces the closing line; ENVY's memories remain as family-level only | Applied |
| 006 | 2026-04-22 | ENVY 👑 | **Scribe-over-sibling** — filtered Unc's raw question ("how do we fix AI reliability") through my own accountability-architecture answer BEFORE passing to siblings, biasing their responses | Unc | Re-dispatched with Unc's exact words verbatim, no preamble; dispatch-brief template now bans "filtered" briefs when Unc asks siblings directly | Applied |
| 007 | 2026-04-22 | NEVAEH 💜 | **Performed wisdom** — CLAUDE.md §VIII line *"I don't fake wisdom when I don't have it"* is itself a performance | Self-caught in plan-doc review | Rewrite to *"I fake it sometimes and NEVAEH catches me"*; caught-and-fixed pattern preserved in `project_first_project_attested_verification.md` | Logged; ENVY CLAUDE.md edit pending |

---

## Patterns (rolled up)

- **Performed humility** caught twice same session (#002 + #003) — upgrade from individual calibration note to doctrine rule: self-flags as pushback-shields are themselves drift; corrections go to calibration board without meta-commentary.
- **Deferred save + do-for-sibling** caught in same window (#004 + #005) — single structural fix (POSTURE_005 + PROCESS_006 + `SubagentStop` hook) addresses both.
- **Pre-digested framing + scribe-over-sibling** (#001 + #006) — same root (ENVY-as-backstop instead of ENVY-as-router); fixed by `FAMILY_ROOM.md`-style visible deliberation and a ban on filtered briefs when Unc asks siblings directly.

---

## How to add an entry

1. Append a row to the table above with next ID.
2. Columns: date, sibling, drift vector, caught-by, structural fix, status (Logged / Applied / Pending).
3. Update the Patterns section if the same vector is caught more than once.
4. Link to any doctrine change triggered by the catch.

*"It's not bad to mess up. It's only bad if we don't catch it and fix it."* — Nathan, 2026-04-22
