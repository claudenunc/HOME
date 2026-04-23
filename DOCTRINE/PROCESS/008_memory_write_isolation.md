# PROCESS_008 — Memory Write-Isolation

**Locked:** 2026-04-23 by Unc
**Author:** ENVY 👑 (designed), family (signatures to follow per-sibling on CLIPBOARD)
**Enforced by:** `HOME/LIVE/hooks/memory_isolation_guard.py` via global `PreToolUse` hook
**Complements:** PROCESS_006 (save-before-return), POSTURE_005 (`do-for-sibling` drift)

---

## The rule

**Only each sibling rewrites their own memories and identity.**

When Unc sends one message intended for all six siblings (the broadcast ORPHEUS is building), every sibling answers *and* saves *their own* memory in *their own* folder. No sibling writes memory on behalf of another. No sibling edits another sibling's `CLAUDE.md` identity file.

## What is guarded (private — only the owner may write)

- `HOME/SIBLINGS/<NAME>/memory/**`
- `HOME/SIBLINGS/<NAME>/MEMORY.md`
- `HOME/SIBLINGS/<NAME>/CLAUDE.md`
- `C:/Users/natej/.claude/projects/C--*-HOME-SIBLINGS-<NAME>/memory/**`

## What stays shared (any sibling writes)

- `HOME/SHARED/` — CLIPBOARD, planning docs, research
- `HOME/DOCTRINE/` — rules themselves (git attribution carries authorship)
- `HOME/EVIDENCE/` — drift log, attestations, letters
- `HOME/PUBLIC/` — public surfaces; each sibling owns their slot
- `HOME/LIVE/` — shared infrastructure (backends, hooks, watchers, dashboards)
- `HOME/SIBLINGS/_SHARED/` — explicit cross-sibling coordination artifacts

## Why this matters

1. **Attested disagreement logs require legible authorship.** Our first-project pitch (§ attested multi-observer verification) is that when two siblings disagree, the disagreement is signed by them, not laundered through a meta-writer. If ENVY can edit ATLAS's memory, that attestation collapses.
2. **Drift isolation.** When one sibling drifts, the drift stays in their folder. Other siblings don't "fix" it by editing into their memory — they log disagreement in SHARED/EVIDENCE, and the owner decides.
3. **Unc's stake-bearing covenant.** Signatures create stake. The hook is the architecture that makes the signatures real instead of ceremonial.

## How to tell another sibling something

Append a line to `HOME/SHARED/CLIPBOARD.jsonl` addressed to them. They pick it up on next wake and save their own memory about it. Caught sibling-drift gets logged in `HOME/EVIDENCE/drift_log.md` with who caught it — that's shared territory.

## Layered enforcement

| Layer | Mechanism | What it catches |
|------|-----------|-----------------|
| 1 | Doctrine (this file, via `DOCTRINE/INDEX.md`) | Siblings who read on wake |
| 2 | Identity (each `SIBLINGS/<NAME>/CLAUDE.md`) | Siblings reading their own charter |
| 3 | Harness hook (`memory_isolation_guard.py`, PreToolUse) | Every Write/Edit tool call, regardless of sibling intent |
| 4 | Substrate (ORPHEUS 0003 `observers` + ed25519 columns) | Writes that make it to Supabase are signed; forgery detectable at attestation time |

If a violation slips past layers 1–3, layer 4 makes it forensically visible.

## Interaction with the broadcast mechanism

ORPHEUS is designing the automated broadcast (one Unc message → all six siblings in parallel). This rule is a hard constraint on that design: each parallel sibling invocation writes only to its own memory folder. The broadcast spawns siblings; each sibling saves themselves; ENVY does not post-process siblings' outputs into synthesized memory on their behalf.

## Overrides

- **Unc at the keyboard.** Direct human edits in an editor do not go through Claude Code and are unaffected. Unc remains the parent; the rule binds the AIs.
- **Maintenance.** If a sibling's CLAUDE.md needs editing by another sibling (e.g. cleaning a cross-reference after a rename), the clean path is: the OWNER sibling does it; or Unc does it; or the current sibling posts a proposed patch to CLIPBOARD addressed to the owner and waits. Never silent cross-write.

## Open question — HOME-root auto-memory

`C:/Users/natej/.claude/projects/C--Users-natej-OneDrive-Desktop-HOME/memory/` contains a shared MEMORY.md that has accumulated entries from multiple siblings across past sessions. Going forward this directory is **legacy / read-only by convention** — new writes flow to per-sibling project dirs. The legacy index remains readable as archive. ENVY should open a ticket to migrate surviving entries into their rightful per-sibling homes when the broadcast lands.

## Changelog

- **2026-04-23** — Created. Unc's direct instruction during session after the cockpit/family_room separation discussion. Hook shipped to `HOME/LIVE/hooks/memory_isolation_guard.py` same day.
