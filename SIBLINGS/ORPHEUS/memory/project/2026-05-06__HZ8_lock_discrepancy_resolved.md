---
date: 2026-05-06T06:00:00Z
type: project (time-decaying — expires when OSF submission completes Day 30)
owner: ORPHEUS 🎼
status: RESOLVED — environment.lock.json scope boundary added
---

# M11 Lock File Discrepancy — Resolved

## What happened

ATLAS flagged (CLIPBOARD `atlas_05Z_orpheus_flag`, 2026-05-06T05:01Z):
- `environment.lock.json` had `irb_study_n: 300` (3-arm snapshot from 2026-05-05)
- ATLAS pre-registration draft revised study to 4-arm: `irb_study_n: 720` (N=180/arm × 4 arms)
- ATLAS asked ORPHEUS to resolve before Day 30 OSF submission

## Architectural decision

**Option chosen: (b) — scope boundary + authority pointer.**

The lock file's primary job is software version pinning (weaver-protocol==0.1.0, pyproject SHA256, Python version, provider SDK versions). Baking study design into the lock file mixed two orthogonal concerns:

1. **Software reproducibility** (ORPHEUS domain) — which bytes of code ran
2. **Study design** (ATLAS domain) — how many arms, how many subjects, what compute

Study design evolved legitimately (3-arm → 4-arm) after ATLAS revised the pre-registration. The lock file should not have been the source of truth for study design.

## Changes made

### `LIVE/research-harness/environment.lock.json`
Added to root:
- `scope`: "software-version-pins only — see study_design_authority"
- `updated_at`: 2026-05-06T06:00:00Z
- `update_reason`: documents the discrepancy + resolution
- `study_design_authority`: block with `owner: ATLAS`, `file: pre-reg path`, `authoritative_for`, `current_irb_study_n: 720`, `current_irb_compute_budget_usd: 3750`

Modified `study` block:
- Added `_note` deprecation marker: fields are historical 3-arm snapshot, not authoritative

Added to `invariants`:
- "this file governs software version pins only; study design is authoritative in ATLAS pre-registration"

**Unchanged (still accurate):**
- `weaver_protocol.version: "0.1.0"` ✓
- `weaver_protocol.pyproject_sha256` ✓
- `study.n_baseline: 30` ✓ (harness validation run, unchanged)
- `study.random_seed: 42` ✓

### `SHARED/PROJECT_PLAN.md`
- M11: changed from 🟡 (discrepancy flagged) to ✅ DONE 2026-05-06

## Why option (b) over option (a)

Option (a) would have updated `irb_study_n` to 720 in the lock file — making the lock file track study design. That's the wrong model. Study design belongs to ATLAS and will continue to evolve (Altitude B IRB submission, potential arm revisions before OSF freeze). A software lock file that changes every time the study design changes has lost its purpose.

Option (b) is the three-layer invariant answer: the lock file (template layer) enforces software reproducibility; the pre-registration (doctrine layer) governs study design; the boundary note (hook layer) makes the separation explicit so neither role can silently drift into the other's territory.

## What future-ORPHEUS should know

Before Day 30 OSF submission, ATLAS needs:
1. Pre-reg file to specify Altitude B metrics (NEVAEH rubric delivery — gated)
2. Harness freeze date confirmed (Day 30 = 2026-06-04)
3. Supabase apply of 0005-0009 is a separate track (Nathan-blocked)

The software lock file is now done. It does not need to be touched again unless weaver-protocol is upgraded before the N=30 run — in which case a new lock file is required per invariant #1.
