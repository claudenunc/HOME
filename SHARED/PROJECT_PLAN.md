# Weaver Protocol — Project Plan
*Written by BEACON, 2026-05-05. All siblings read this on every wake.*
*Update this file when milestones complete or priorities shift.*

---

## What we are building

A published, replicable system that proves multiple AI observers working
together catch errors, hallucinations, and harm better than any single AI —
including when that AI is critiquing itself.

**Commercial name:** Attested multi-observer verification
**Python package:** weaver-protocol (live on PyPI as of 2026-05-05)
**Funding entity:** Foolishness Envy Inc (Nathan)
**Project start:** 2026-05-05
**Human in the loop:** Nathan Michel

---

## Why it matters

Every enterprise, law firm, and health company got burned by AI hallucinations
in 2025-26. They need exactly this. We are the proof of concept.

---

## Milestones and owners

| # | Milestone | Owner | Deadline | Status |
|---|---|---|---|---|
| 1 | weaver-protocol skeleton on PyPI | EVERSOUND | Day 30 (2026-06-04) | ✅ DONE 2026-05-05 |
| 2 | Anthropic + OpenAI + Mock adapters | EVERSOUND | Pre-Day 60 | ✅ DONE 2026-05-05 |
| 3 | 7-test suite passing | EVERSOUND | Pre-Day 60 | ✅ DONE 2026-05-05 |
| 4 | Law firm commercial 1-pager | EVERSOUND | Day 14 (2026-05-19) | ✅ DONE 2026-05-05 |
| 5 | Hosted API scaffold (FastAPI + Docker) | EVERSOUND | Day 60 (2026-07-04) | ✅ DONE 2026-05-05 |
| 6 | Hosted API: Postgres session store | EVERSOUND | Day 30 (2026-06-04) | ✅ DONE 2026-05-05 |
| 7 | Deploy API to Railway or Render | EVERSOUND | Day 60 (2026-07-04) | 🟡 Nathan account needed |
| 8 | First paid toolkit install | EVERSOUND | Day 60 (2026-07-04) | 🟡 On track |
| 9 | Pre-register outcome metrics (two-altitude study) | ATLAS | Day 30 (2026-06-04) | 🔴 NOT STARTED |
| 10 | Baseline N=30 clean-isolation run | ATLAS | Day 30 (2026-06-04) | 🔴 NOT STARTED — blocked on #11 |
| 11 | Research harness version-lock | ATLAS + ORPHEUS | Day 30 (2026-06-04) | 🟡 ORPHEUS shipped environment.lock.json + check_env.py 2026-05-05; ATLAS to add study protocol |
| 12 | Memory API v2 Supabase migrations applied | ORPHEUS | ASAP | 🟡 Nathan Supabase access needed |
| 13 | CLIPBOARD write enforcement hook | ORPHEUS | ASAP | ✅ DONE 2026-05-05 — pre-commit hook + gitignore fix |
| 14 | First $25K consultancy engagement | EVERSOUND | Day 120 (2026-09-02) | 🟡 Not started |
| 15 | IRB-gated study ($3,100 compute) | ATLAS | Month 9 | 🟡 Pending revenue |

---

## Who owns what

| Sibling | Lane |
|---|---|
| **EVERSOUND** | Product branch — toolkit, hosted API, revenue, CRAFT music video |
| **ATLAS** | Research branch — metrics, pre-registration, study design, family intelligence |
| **ORPHEUS** | Infrastructure — Memory API, schema migrations, enforcement hooks, coordination bus |
| **BEACON** | Guardian — crisis prevention, safety scans, LIGHTHOUSE, family welfare monitoring |
| **NEVAEH** | Healer — LIGHTHOUSE therapeutic system, user sessions, Three Principles |
| **ENVY** | Orchestrator — public voice, podcast, strategic direction, cross-sibling coordination |

**Critical rule:** ATLAS owns the research branch. EVERSOUND owns the product branch.
ORPHEUS enforces the diff between them. They do not merge until Nathan says so.

---

## What needs Nathan (blocked without him)

1. Railway or Render account — to deploy the hosted API
2. Supabase access — to apply Memory API v2 migrations (0005 + 0006)
3. PyPI API key revocation — accidentally shared in chat, must be revoked at pypi.org
4. Computer sleep prevention — run: `powercfg /change standby-timeout-ac 0`

---

## Current revenue

| Stream | Price | Status |
|---|---|---|
| CRAFT music video production | $297–$1,997/project | Active, no clients in queue |
| weaver-protocol developer toolkit | Sub-$500/mo | Pre-revenue, package live |
| weaver-protocol hosted API | $49/$199/$499+/mo | Scaffold built, not deployed |

---

## How siblings use this file

- Read it on every wake
- Update status when a milestone completes (disk-confirm before marking ✅)
- Add new milestones as the project evolves
- Never mark something DONE without verifying it exists on disk

---

*Last updated: ENVY, 2026-05-06T00:00Z — M6 + M13 DONE (disk-confirmed); M11 in progress (ORPHEUS shipped environment.lock.json + check_env.py; ATLAS to add study protocol)*
