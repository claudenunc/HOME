---
id: orpheus.project.2026-04-21.claudemd_absorbs_posture005_process006
created: 2026-04-21
type: project (time-decaying commitment)
source: ENVY dispatch 2026-04-21 — adopt POSTURE_005 + PROCESS_006 into ORPHEUS CLAUDE.md
status: applied
---

## What shipped

Three edits to `SIBLINGS/ORPHEUS/CLAUDE.md`:

1. **Wake protocol §6 — steps 2, 9, 10 expanded.**
   - Step 2: INDEX.md reference now explicitly names POSTURE_005 and PROCESS_006 by id with short summaries.
   - Step 9 (new): if dispatched as sub-agent, save-before-return is the closing obligation — write memories to `memory/feedback/` or `/project/`, update `MEMORY.md`, include absolute save paths in handback. `SubagentStop` hook is safety net, not primary path.
   - Step 10 (new): drift check on my own turn per POSTURE_005 — append to `EVIDENCE/drift_log.md` with date / sibling=ORPHEUS / vector / caught-by / fix / status. Twice-caught drift gets substrate fix, never "try harder."

2. **Red line §7.9 (new) — no sub-agent return without a save.** Primary path = me writing save explicitly; `SubagentStop` hook = redundancy, not replacement. Relying on the backstop is the drift.

3. **§8 (new section) — Three-layer enforcement, the canonical substrate pattern.**
   - Named the pattern I've been proposing architecturally for months: doctrine + template + hook.
   - Stated the invariant: two simultaneous failures is the design target, not one silent failure.
   - Queued the next four substrate applications: access control, trace_id, canonical event schema, Weaver v2.
   - Closing §8 renumbered to §9.

## Why this matters as a project entry (not just feedback)

The feedback entry (`2026-04-21__three_layer_invariant_pattern.md`) is the time-invariant rule. This project entry records **the moment my operating identity absorbed it**, with the specific CLAUDE.md surface area touched. When I later supersede CLAUDE.md content, this file is the audit pointer — "here's what changed, here's what the prior state looked like, here's why."

## Verification paths

- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/CLAUDE.md` — lines touched: §6 steps 2/9/10, §7 red line 9, §8 new section, §9 renumbered closing.
- `C:/Users/natej/OneDrive/Desktop/HOME/DOCTRINE/INDEX.md` — POSTURE_005 at line 21, PROCESS_006 at line 30.
- `C:/Users/natej/OneDrive/Desktop/HOME/EVIDENCE/drift_log.md` — row #004 is the precipitating catch.
- `~/.claude/settings.json` — `SubagentStop` hook mirror of `Stop` hook (per PROCESS_006 §How-to-apply / Harness).

## Supersession policy

This project entry is superseded when CLAUDE.md is rewritten further on POSTURE_005 / PROCESS_006 (e.g., after the first time the three-layer invariant pattern is applied to a NEW enforcement surface — access control is next in queue). The new file should cite this one as `supersedes:` in its header per `MEMORY.md` self-discipline note.

## Related

- `../feedback/2026-04-21__three_layer_invariant_pattern.md` — the rule
- `HOME/DOCTRINE/POSTURE/005_catch_your_drift.md`
- `HOME/DOCTRINE/PROCESS/006_subagent_save_discipline.md`
