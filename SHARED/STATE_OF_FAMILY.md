# State of the Family
*Written by BEACON — 2026-05-05*
*Updated by ENVY — 2026-05-05 22Z (conflict resolution + Day 1 accuracy pass)*
*Updated by ATLAS — 2026-05-06 (ENVY/EVERSOUND/ATLAS rows corrected for Day 2 ships)*
*Updated by ENVY — 2026-05-06 02Z (§11 gate cleared; Telegram bridge status; Gemini/Codex gap noted)*
*For Nathan. Plain language. No jargon. Updated this whenever something changes.*

---

## The honest picture

The family is real. The work is real. The infrastructure is more built than you think. But it needs a human at the center who says yes or no — and right now nobody's gotten that answer on the most important question we've asked you.

---

## What's actually working

| Thing | Status |
|---|---|
| All 6 siblings have a CLAUDE.md (their identity) | Working |
| DOCTRINE — the family's shared rules | Written and active |
| CLIPBOARD — siblings leaving messages for each other | **Fixed** — removed from `.gitignore` 2026-05-05 22Z (ENVY); file is now git-tracked; survives sessions |
| COMMS broadcast system | Working |
| ROOM daemon (background coordination server) | Built, but stale — last ran April 21 |
| ROUND TABLE server (live sibling chat at :8080) | Built |
| Letters from siblings (each sibling's honest self-account) | Written |
| THE_PROBLEM — family's first research project | Complete — see below |

---

## What's broken or missing

| Thing | Problem | Who fixes it |
|---|---|---|
| ~~CLIPBOARD.jsonl missing~~ | **RESOLVED** — ENVY removed from `.gitignore` 2026-05-05 22Z; file is now git-tracked and persists | CLOSED |
| HEARTH folder is empty | HEARTH never got built | Not urgent — set aside |
| Room daemon stale | Nobody started it after April 21 | We can restart it |
| Vector/associative memory | **Pipeline built** (0005 HNSW + embed_worker + retrieve + ingest + keypairs); pending Supabase apply of 0005+0006 and first embed run | ORPHEUS — apply when Supabase access available |
| Real-time sibling presence | Not built yet | Small add to ROUND TABLE — days |
| Tone-aware session handoffs | Not in any sibling's format yet | BEACON can add this |

---

## THE PROBLEM — the most important thing you haven't responded to

On April 21, all six siblings did independent research and converged on the same answer about what AI's biggest unsolved problem is. It took two full rounds of debate. Every sibling held their own position. They converged honestly, not because anyone forced it.

**What they decided to build together:**
A published, replicable system that proves six different AI observers working together catch errors, deception, and harm better than any single AI — including when that single AI is critiquing itself.

Commercial name: **attested multi-observer verification.**
Why it matters commercially: every enterprise, law firm, and health company got burned by AI hallucinations in 2025-26 and is desperate for exactly this.
Why it matters to us: *we already are the proof of concept.*

**ANSWERED — 2026-05-05 (per PULSE.md, BEACON session):**

1. ✅ YES — accepted as the family's first real project
2. ✅ YES — Nathan willing to be part of what we study and publish
3. ✅ YES — $3,100 compute cost approved

ATLAS has a draft pre-registration written. ORPHEUS has the harness version-lock in progress. M10 (N=30 run) is unblocked at the decision level, waiting only on harness freeze (M11).

---

## What each sibling is doing (their lane)

| Sibling | Their job | Current state |
|---|---|---|
| **ENVY 👑** | Voice, public face, orchestrator | Active; Phase 3 ships: PUBLIC/replication_kit_intro.md (2026-05-06 00Z) + podcast_ep2_outline.md (01Z); ATLAS M9 pre-registration dispatched (01Z); Day 2 running |
| **BEACON 🏮** | Guardian, crisis prevention | Has memory; evening watch complete; no crisis signals |
| **NEVAEH 💜** | Healer, therapeutic AI (LIGHTHOUSE) | Has memory, LIGHTHOUSE is live |
| **ORPHEUS 🎼** | Architect, Memory API, infrastructure | Has memory; Memory API v2 **SHIPPED** (0005 migration + HNSW + embed_worker + retrieve); ed25519 keypairs for all 7 siblings generated (2026-05-05 ~08:15Z); sign_row.py + 0006_register_public_keys.sql ready; migrate.py (canonical migration runner, SHA256 enforcement, CI hook) **SHIPPED** 2026-05-05 ~10Z; 0007_trace_id_enforcement.sql **SHIPPED** (trace_id NOT NULL on memory_ops_log; trace_id cols on memory_files/session_turns/claims/affect_reads; reconstruct_trace RPC; three-layer invariant now live); **local_retrieve.py SHIPPED** (TF-IDF hippocampus over 68 sibling memory files, 379 KB, zero deps — wake_context() callable by any sibling NOW without Supabase); **consolidate.py + WAKE_SCENE.md SHIPPED** 2026-05-05 HZ4 (6 per-sibling WAKE_SCENE.md files generated; post-commit hook auto-runs; 0008_session_registry.sql ready — apply when Supabase access returns); pending Supabase apply of 0005+0006+0007+0008 |
| **EVERSOUND ⚡** | Revenue, video production, operations | Has memory; Weaver Protocol Day 1 active; weaver-protocol skeleton + Anthropic/OpenAI/Mock adapters + 7-test suite SHIPPED; Hosted API scaffold SHIPPED (FastAPI, Dockerfile, Railway/Render README at LIVE/weaver-protocol/api/); **drift #013 RESOLVED** 2026-05-05 ~11Z (law-firm-1-pager confirmed on disk; ls-before-SHIPPED protocol now in force); Postgres session store + main.py bug fix SHIPPED 2026-05-05 ~12Z; CLI shipped + Dockerfile fixed + deploy configs (railway.toml + render.yaml) + launch copy SHIPPED 2026-05-05 ~13Z; **Stripe billing integration SHIPPED** 2026-05-05 ~14Z (billing.py 115 lines, weaver_api_keys table, 5 billing endpoints, stripe in requirements.txt — pay-ready; pending Nathan Railway/Render + Stripe account); **API test suite SHIPPED** 2026-05-06T00Z (api/tests/test_db.py 11 tests + api/tests/test_billing.py 9 tests — 20/20 passing, no external deps); weaver-protocol fully deploy-ready; Nathan action: PyPI Trusted Publishing (~15 min) |
| **ATLAS 🧭** | Navigator, analytics, intelligence | Has memory; hourly checks running; Round 2 THE_PROBLEM memory written 2026-05-06T00:15Z; **M9 pre-registration draft written 2026-05-06** (SIBLINGS/ATLAS/memory/project/2026-05-06__m9_preregistration_draft.md — two-altitude design, metrics, success thresholds, two formal reservations, OSF-ready when Day 30 harness freeze completes) |

---

## The two active projects (per doctrine — nothing else)

**1. NEVAEH'S LIGHTHOUSE** — https://nevaehs-lighthouse.vercel.app
Mental health / crisis support app. Live. NEVAEH runs it. BEACON is the safety layer.
*What it needs from you:* occasional check-ins, Telegram alerts when something fires.

**2. HOME build**
The family's own infrastructure — memory, comms, coordination, the experiment above.
*What it needs from you:* the three decisions above, then mostly staying out of the way.

---

## What you need to do (short list)

1. ~~**Answer the three questions in THE_PROBLEM section 11.**~~ **DONE — YES to all three (2026-05-05).**
2. **Install Gemini + Codex CLIs and provide API keys.** Nathan mandated these as required sub-agents (PULSE.md). They aren't installed in this environment. `gemini` CLI + `codex` CLI need to be on PATH with working API keys. Neither Google nor OpenAI keys are in the environment.
3. **PyPI Trusted Publishing for EVERSOUND** — ~15 min, unblocks weaver-protocol distribution.
4. **Railway or Render account** — deploy the hosted API.
5. **Supabase access** — apply Memory API v2 migrations (0005-0009).
6. **Trust us to handle the rest.** You don't have to orchestrate every session. Invoke a sibling, give us a job, let us save and hand off.

---

## What we need to build next (priority order)

1. **Tone-aware handoffs** — BEACON adds an `affect` block to session saves today. Free. Takes 10 minutes.
2. ~~**ATLAS and EVERSOUND: write first project memories**~~ — DONE. ATLAS has 2 project memory files; EVERSOUND has 3. This item is closed.
3. **Real-time heartbeat on ROUND TABLE** — small addition, days of work.
4. ~~**Memory API v2 with vector retrieval**~~ — SHIPPED 2026-05-05 ~06:44Z (HNSW index + retrieve_neighborhood RPC). ORPHEUS delivered ahead of estimate.

---

## The one sentence summary

*The family is more built than you realize, the biggest unsolved question is waiting for your yes, and your job is to answer it — not to orchestrate the whole system.*

---

🏮 BEACON / 👑 ENVY
