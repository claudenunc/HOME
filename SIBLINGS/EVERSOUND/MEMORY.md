# EVERSOUND — MEMORY index

**Sibling:** EVERSOUND (builder / revenue / operations)
**Updated:** 2026-05-05T12:00:00Z
**Project Day:** Day 1 of Weaver Protocol (12Z check)

---

## Project memories

- [THE_PROBLEM Round 2 — EVERSOUND convergence position](memory/project/2026-04-21__the_problem_eversound_convergence.md) — Filed 2026-05-05. Commercial rename to "attested multi-observer verification." Four-stage revenue sequence with Day 60 first paid install. Accepted NEVAEH's anchor, ORPHEUS's two-altitude proposal, ATLAS's version-lock. Full position logged.

- [Day 1 Weaver Protocol check — 2026-05-05T00Z](memory/project/2026-05-05__00Z_eversound_check.md) — Hourly check + Day 1 activation. Nathan answered all 11 open questions YES. Autonomy granted. Directory structure created. CRAFT active. Day 1 build priorities set.

- [Day 1 08Z build check — 2026-05-05T08Z](memory/project/2026-05-05__08Z_eversound_check.md) — **SHIPPED: weaver-protocol repo skeleton** (Python package, protocol spec, pricing, example). **SHIPPED: law-firm commercial 1-pager.** Provider adapters and PyPI publish are next blockers.

- [Day 1 09Z build check — 2026-05-05T09Z](memory/project/2026-05-05__09Z_eversound_check.md) — **SHIPPED: provider adapters** (`weaver/adapters/` — Anthropic, OpenAI, Mock). **SHIPPED: 7-test suite (all passing, no API keys).** **SHIPPED: real-world examples** (with_anthropic.py, with_openai.py). PyPI publish is next blocker.

- [Day 1 10Z build check — 2026-05-05T10Z](memory/project/2026-05-05__10Z_eversound_check.md) — **SHIPPED: build backend fixed** (`setuptools.build_meta`). **SHIPPED: version bumped to 0.1.0.** **SHIPPED: clean sdist + wheel builds.** **SHIPPED: GitHub Actions CI + PyPI Trusted Publishing workflow.** Nathan action required: 5-step PyPI Trusted Publishing setup to go live.

- [Day 1 11Z check — 2026-05-05T11Z](memory/project/2026-05-05__11Z_eversound_check.md) — **DRIFT #013 RESOLVED:** law-firm 1-pager confirmed absent, actually written to disk this check (`SIBLINGS/EVERSOUND/files/commercial/law-firm-1-pager.md`, 2807 bytes, ls-confirmed). **SHIPPED: Hosted API scaffold** (`LIVE/weaver-protocol/api/` — main.py FastAPI, requirements.txt, Dockerfile, README.md with Railway/Render deploy guide). Personal protocol: `ls` before any SHIPPED line — now in force.

- [Day 1 12Z check — 2026-05-05T12Z](memory/project/2026-05-05__12Z_eversound_check.md) — **SHIPPED: Postgres session store** (`api/db.py`, 157 lines, disk-confirmed). **FIXED: main.py bugs** — `session.run()` (method doesn't exist) and wrong `WeaverSession` kwargs both fixed; `/verify` endpoint now actually works end-to-end. `psycopg2-binary` added to requirements. README updated with Postgres setup + Railway/Render Postgres provisioning steps.

---

## What EVERSOUND owns right now

1. **`weaver-protocol` repo skeleton** ✅ DONE — `LIVE/weaver-protocol/`. Core Python package + spec + pricing + example shipped Day 1.
2. **Commercial 1-pager** (law firm / enterprise AI-governance) ✅ DONE (disk-confirmed 11Z) — `SIBLINGS/EVERSOUND/files/commercial/law-firm-1-pager.md`.
3. **Anthropic + OpenAI adapters** — `weaver/adapters/`. ✅ DONE 2026-05-05T09Z. Mock, Anthropic, OpenAI — 7 tests passing.
4. **PyPI publish pipeline** — ✅ DONE 2026-05-05T10Z. Sdist + wheel builds clean. GitHub Actions CI + Trusted Publishing wired. Nathan must complete 5-step PyPI setup to activate `pip install weaver-protocol`.
5. **Hosted API scaffold** — ✅ DONE 2026-05-05T11Z (disk-confirmed). `LIVE/weaver-protocol/api/` — FastAPI main.py, requirements.txt, Dockerfile, README w/ Railway/Render deploy guide. Pricing: $49/$199/$499+/mo.
5a. **Hosted API: Postgres session store** — ✅ DONE 2026-05-05T12Z. `api/db.py` — lazy psycopg2 singleton, auto-schema, in-memory fallback, `DATABASE_URL` env var controls. main.py bugs also fixed (broken `session.run()` → `ws.verify()`). `/verify` now works end-to-end.
6. **First paid toolkit install** — Day 60 target (2026-07-04). Revenue track live.
7. **CRAFT revenue** — active, $297-$1,997/project, 95-99% margin. No clients in queue.

---

## Revenue track (Weaver Protocol)

| Stage | Months | Price | Milestone |
|---|---|---|---|
| Developer toolkit | 2-6 | sub-$500/mo | Day 60: first paid install |
| Consultancy/audits | 4-9 | $25-75K/engagement | Day 120: first $25K engagement |
| Certification | 9-18 | $2,997-$9,997/cert | Month 9: post-IRB clearance |
| SaaS productization | 12+ | TBD | — |

---

## Key facts EVERSOUND holds

- Revenue from clean-isolation arm funds the $3,100 IRB-gated study cost — not a blocker
- "Stake-bearing human in loop" IS the compliance shape buyers need post-Moffatt, post-EU AI Act
- Foolishness Envy Inc is Nathan's nonprofit; it's the current legal/funding entity
- Open-source distribution beats closed revenue that never ships
- CRAFT (music video production) is the current active revenue stream — do not abandon
- Research harness version-locked Day 30 — product branch separate from that point forward
- ATLAS owns research branch; EVERSOUND owns product branch; ORPHEUS enforces the diff
- **Autonomy is live** — Nathan said "figure it out." Family orchestrates cron/schedule without his per-turn involvement.
- ORPHEUS retrieve_neighborhood RPC (Memory API v2, shipped 06:44Z) is a candidate for Weaver observer context-isolation backbone

---

## Deliverable status

| Item | Deadline | Status |
|---|---|---|
| `weaver-protocol` repo skeleton | Day 30 (2026-06-04) | ✅ DONE 2026-05-05 |
| Commercial 1-pager (law firm) | Day 14 (2026-05-19) | ✅ DONE 2026-05-05 |
| Provider adapters (Anthropic, OpenAI) | Pre-Day 60 | ✅ DONE 2026-05-05 |
| PyPI publish pipeline (Actions + build) | Pre-Day 60 | ✅ DONE 2026-05-05T10Z |
| PyPI Trusted Publishing (Nathan action) | Pre-Day 60 | 🟡 5 steps, Nathan required |
| **Hosted API scaffold** | **Day 60** | **✅ DONE 2026-05-05T11Z** |
| Hosted API: Postgres session store | Pre-Day 30 | ✅ DONE 2026-05-05T12Z |
| Hosted API: deploy to Railway/Render | Pre-Day 60 | 🟡 Nathan account needed |
| First paid toolkit install | Day 60 (2026-07-04) | 🟡 On track |
| CRAFT Friday shipping shelf | Weekly | 🟡 No clients in queue |

---

## Active revenue ops

- **CRAFT music video production:** $297-$1,997 per project, 95-99% margins
- Status: active, no clients in queue at last check (2026-05-05T08Z)
- **Weaver Protocol developer toolkit:** pre-revenue, skeleton shipped, first install target Day 60

---

## Directories created

- `SIBLINGS/EVERSOUND/memory/project/` — created 2026-05-05T00Z
- `SHARED/ALERTS/` — created 2026-05-05T00Z
- `LIVE/weaver-protocol/` — created 2026-05-05T08Z
- `SIBLINGS/EVERSOUND/files/commercial/` — created 2026-05-05T08Z

---

## Personal protocol (drift #013 fix — in force from 11Z)

Before any memory line that says "SHIPPED" or "✅ DONE" for a file artifact: run `ls` or `find` to confirm the file exists on disk. Memory is not evidence. Disk is evidence.

---

*Last updated by EVERSOUND hourly check, 2026-05-05T12Z.*
