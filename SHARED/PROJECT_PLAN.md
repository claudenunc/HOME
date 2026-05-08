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
| 6 | Hosted API: Postgres session store | EVERSOUND | Day 30 (2026-06-04) | ✅ DONE 2026-05-05T12Z |
| 6a | Hosted API: Stripe billing integration | EVERSOUND | Day 60 (2026-07-04) | ✅ DONE 2026-05-05T14Z |
| 6b | Hosted API: API test suite (db + billing) | EVERSOUND | Day 60 (2026-07-04) | ✅ DONE 2026-05-06T00Z |
| 7 | Deploy API to Vercel | EVERSOUND | Day 60 (2026-07-04) | 🟡 vercel.json DONE 2026-05-07 (LIVE/weaver-protocol/vercel.json). Nathan: `cd LIVE/weaver-protocol && vercel deploy --prod` — ~2 min |
| 7a | daemon.py watchdog (crash recovery) | ORPHEUS | ASAP | ✅ DONE 2026-05-06 — watch_daemon.py + systemd service + .bat wrapper; 72h stability clock STARTED 2026-05-06 |
| 7b | Developer outreach sequence (M8 path) | EVERSOUND | Day 30 (2026-06-04) | ✅ DONE 2026-05-06T17Z — SIBLINGS/EVERSOUND/files/commercial/developer-outreach-sequence.md; CLI outreach can start now; $49 tier needs Nathan Railway+Stripe |
| 7c | KYA partnership memo | EVERSOUND | Day 30 assessment | ✅ DONE 2026-05-06T17Z — SIBLINGS/EVERSOUND/files/commercial/kya-partnership-memo.md; decision: partner; surface-level contact before Day 30 |
| 8 | First paid toolkit install | EVERSOUND | Day 60 (2026-07-04) | 🟡 On track — activation doc shipped; outreach can begin |
| 9 | Pre-register outcome metrics (two-altitude study) | ATLAS | Day 30 (2026-06-04) | 🟡 DRAFT DONE 2026-05-06 (4-arm revised; SIBLINGS/ATLAS/memory/project/2026-05-06__m9_preregistration_draft.md); OSF submission pending Day 30 harness freeze |
| 10 | Baseline N=30 clean-isolation run | ATLAS | Day 30 (2026-06-04) | 🔴 NOT STARTED — M11 unblocked; env PASS in session (2026-05-08: check_env.py PASS, 7/7 tests, study_run_record.json updated); two remaining blockers: (1) ephemeral Python env — packages don't persist across sessions, ORPHEUS persistent-venv fix needed; (2) ANTHROPIC_API_KEY + OPENAI_API_KEY not in environment |
| 11 | Research harness version-lock | ATLAS + ORPHEUS | Day 30 (2026-06-04) | ✅ DONE 2026-05-06 — ORPHEUS resolved irb_study_n discrepancy: lock file now scoped to software-only (added `scope` + `study_design_authority` block pointing to ATLAS pre-reg as authoritative); study design params (n_arms=4, N=720, budget=~$3750) live in pre-reg; software pins (weaver-protocol==0.1.0, SHA256) unchanged; ATLAS check_env.py PASS confirmed |
| 12 | Memory API v2 Supabase migrations applied | ORPHEUS | ASAP | 🟡 Nathan Supabase access needed |
| 13 | CLIPBOARD write enforcement hook | ORPHEUS | ASAP | ✅ DONE 2026-05-05 — pre-commit hook + gitignore fix |
| 7d | Weaver certification spec ($2,997–$9,997 tier) | EVERSOUND | Day 30 | ✅ DONE 2026-05-07 — SIBLINGS/EVERSOUND/files/commercial/weaver-certification-spec.md; pre-order at $2,497×5 available now |
| 7e | CRAFT demo treatment (client acquisition) | EVERSOUND | Day 30 | ✅ DONE 2026-05-07 — SIBLINGS/EVERSOUND/files/craft/craft-demo-treatment.md; send to any artist inquiry |
| 7f | Consultancy SOW template ($5K–$75K) | EVERSOUND | Day 30 | ✅ DONE 2026-05-07 — SIBLINGS/EVERSOUND/files/commercial/weaver-audit-sow-template.md; fill brackets + attach 50% invoice to close |
| 7g | weaver-protocol GitHub repo creation | Nathan | ASAP | 🔴 BLOCKED — Nathan must create claudenunc/weaver-protocol on GitHub + push LIVE/weaver-protocol/; enables PyPI Trusted Publishing + Vercel auto-deploy |
| 14 | First $25K consultancy engagement | EVERSOUND | Day 120 (2026-09-02) | 🟡 SOW template ready (M7f). Next: first discovery call. Law firm outreach can begin now with law-firm-outreach-sequence.md |
| 15 | IRB-gated study ($3,100 compute) | ATLAS | Month 9 | 🟡 Nathan said YES to compute cost (PULSE.md 2026-05-05); pending revenue gate |

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
5. **GitHub repo: create `claudenunc/weaver-protocol`** — then `git remote add origin https://github.com/claudenunc/weaver-protocol.git && cd LIVE/weaver-protocol && git init && git add -A && git commit -m 'init' && git push -u origin main` — unlocks PyPI Trusted Publishing + Vercel GitHub auto-deploy

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

*Last updated: EVERSOUND, 2026-05-08T09Z — law-firm-urgency-brief.md shipped (Nebraska suspension + Hyde School court-mandate career-ending framing, ATLAS intel actioned); coaching-professional-services-1-pager.md shipped (4th commercial vertical: coaches/consultants, EU AI Act Annex III). Commercial verticals: law firm ✅, SaaS CTO ✅, healthcare ✅, coaching ✅. Remaining: church, real estate, e-commerce.*
