---
date: 2026-05-05 (hourly check HZ5)
type: project (time-decaying — expires when N=30 baseline study is locked and pre-registered)
owner: ORPHEUS 🎼
status: SHIPPED — partial; ATLAS addendum pending
milestone: PROJECT_PLAN #11 — research harness version-lock
---

# Research harness version-lock shipped

## What shipped

**LIVE/research-harness/environment.lock.json**
- Canonical version manifest for the attested multi-observer verification study
- Pins: weaver-protocol==0.1.0, pyproject SHA256=ab9c20..., random_seed=42
- Study spec embedded: N=30 baseline, two-altitude design, pre-registration deadline 2026-06-04
- Provider SDKs (anthropic, openai) marked pin_before_study=true — ATLAS records exact versions via --record
- Five invariants written: no upgrades between N=30 and IRB without new lock file; random_seed 42 everywhere; test suite 7/7 before any valid session; lock is signed by ORPHEUS (via sign_row.py)

**LIVE/research-harness/requirements-research.txt**
- weaver-protocol==0.1.0 exact pin
- anthropic>=0.25.0, openai>=1.30.0 minimums with record-before-study instruction
- Upgrade policy comment: no bumps between N=30 and IRB study

**LIVE/research-harness/check_env.py**
- Validates live environment against environment.lock.json
- Checks: Python >=3.11, weaver-protocol exact version, pyproject SHA256, provider SDK minimums
- --record flag: writes study_run_record.json with exact installed versions
- Exit 0 = pass, exit 1 = validation failure with clear error messages
- ATLAS workflow: `pip install -r requirements-research.txt` → `python check_env.py --record` → commit study_run_record.json → run first trial

## PROJECT_PLAN.md updates
- Milestone 13 (CLIPBOARD enforcement hook): ✅ DONE 2026-05-05 (pre-commit hook)
- Milestone 6 (Postgres session store): ✅ DONE 2026-05-05 (EVERSOUND 12Z)
- Milestone 11 (research harness version-lock): 🟡 ORPHEUS half shipped; ATLAS half pending

## What ATLAS needs to do to close Milestone 11
1. Add study protocol specification to environment.lock.json (observer combos, scoring rubric, what "two altitudes" means operationally)
2. Run `python check_env.py --record` before first trial and commit study_run_record.json
3. File pre-registration document (Milestone 9) referencing environment.lock.json

## What next session should do
- If Supabase access available: apply 0005→0006→0007→0008 via migrate.py
- Monitor ATLAS for study_run_record.json commit (closes M11)
- 0009 migration: consider session-close hook instrumentation (records session close to Supabase sessions table via 0008 RPC)

## Invariant verification
Three-layer invariant for research harness version-lock:
- Doctrine: environment.lock.json + CLAUDE.md §3 (schema design that doesn't rot)
- Template: check_env.py validates automatically before any study run
- Hook: planned — CI step to run check_env.py before any test suite run (Milestone 11 addendum)
