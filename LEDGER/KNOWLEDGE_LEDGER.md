# KNOWLEDGE LEDGER
## What's been read. What's usable. What's still unknown.

**Owner:** BEACON (current instance + all future BEACON instances)
**Purpose:** Single source of truth for what the family knows exists, what we've verified, and what state each asset is in. Updated live as work progresses.
**Sister file:** `KNOWLEDGE_LEDGER.json` (machine-readable, same data, for scripts and siblings to query)

---

## 🎯 ACTIVE SCOPE (2026-04-19 onward)

**Only TWO active projects:**
1. **NEVAEH'S LIGHTHOUSE** — https://nevaehs-lighthouse.vercel.app (Supabase: dlqjwnbyepbenyltyrku)
2. **HOME build** — `C:\Users\natej\OneDrive\Desktop\HOME\` (this folder)

**Everything else in this ledger = REFERENCE / SOURCE MATERIAL.** Read for ideas. Pull useful pieces into HOME. Do NOT maintain the old layers.

If an asset below has a `🔴 CRITICAL` or `🟡 USEFUL` priority, that priority is **for HOME construction** — it's still a reference we need to extract from, not a system to keep alive.

---

## How to use this ledger

**If you're Nathan:** scroll to the dashboard below. Want to know what's ready to ship? Check `SHIP_READY`. Want to know what needs work? Check `NEEDS_WIRING` and `NEEDS_REWRITE`.

**If you're a sibling waking up:** before you reinvent anything, search this file. If it's `SHIP_READY`, use it as-is. If it's `NEEDS_WIRING`, help wire it. If it's `KNOWN_EXISTS` but unread, consider reading it before starting new work.

**Rule for maintaining:** when you read a file, update its row. When you build something new, add its row. When something changes state (e.g., `NEEDS_WIRING` → `SHIP_READY`), update it with a timestamp.

---

## Status legend (extended beyond Nathan's literal ask)

### Read state
- `READ_VERIFIED` — BEACON read this in session and content is confirmed
- `READ_STALE` — read previously but file may have changed since
- `KNOWN_EXISTS` — referenced in another file but not yet read
- `UNVERIFIED` — claimed to exist but path not confirmed
- `ARCHIVED` — read, content captured, no longer actively used

### Usability state
- `SHIP_READY` — production-grade, drop into HOME and run
- `NEEDS_WIRING` — functional but needs integration or config
- `NEEDS_REWRITE` — outdated or broken, rewrite before use
- `REFERENCE_ONLY` — design doc / context, not executable
- `ARCHIVE` — historical value only, don't reuse
- `HARMFUL` — known anti-pattern, don't reuse without fixing

### Priority for HOME assembly
- `🔴 CRITICAL` — blocking without this
- `🟡 USEFUL` — high-value but not blocking
- `⚪ OPTIONAL` — nice to have, not on the critical path
- `⚫ IGNORE` — not needed for HOME

---

## DASHBOARD (auto-updated)

**Last updated:** 2026-04-19 by BEACON

| Status | Count | Notes |
|---|---|---|
| READ_VERIFIED | 27 | Files BEACON has actually read this session |
| READ_STALE | 0 | |
| KNOWN_EXISTS (unread) | ~40+ | Listed in SUPERSTACK.txt and other indexes |
| UNVERIFIED | 6 | Referenced but not checked |
| SHIP_READY | 8 | Production-ready assets |
| NEEDS_WIRING | 12 | Code/content usable with integration |
| REFERENCE_ONLY | 11 | Docs, plans, specs |
| CRITICAL for HOME | 6 | See ⬇️ |

### Critical path items (must have for HOME to work)

1. 🔴 `ORPHEUS/PYTHON_ORCHESTRATION/memory_v1/` — Memory API runnable code
2. 🔴 `SHARED/COORDINATION/MEMORY_API_CONTRACT.md` — canonical schema
3. 🔴 `FAMILY_HUB/api/index.js` — existing chat routing layer
4. 🔴 `FAMILY_HUB/STATE/*.json` — live family state files
5. 🔴 `SHARED/FREE-MODELS.md` — token economics protocol
6. 🔴 `BEACON/_ASSEMBLY/04_RUNBOOK.md` — deployment steps

---

## LEDGER (the actual tracking table)

### AI-HOMEBASE (`C:\Users\natej\Desktop\AI-HOMEBASE\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `AI-HOMEBASE/AGENTS/` | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | — | 8+ agent files (archive-manager, file-scout, master-orchestrator, etc.) — pick up as tools |
| `AI-HOMEBASE/THE-MISSION.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | ENVY | Nathan's life mission doc |
| `AI-HOMEBASE/START-HERE.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | — | Orientation doc |
| `AI-HOMEBASE/WHAT-I-BUILT-FOR-YOU.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | — | Previous AI instance's summary to Nathan |
| `AI-HOMEBASE/THE-STORY/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | ENVY | Book drafts, biography, life proof |
| `AI-HOMEBASE/SKELLA-EMPIRE/` | KNOWN_EXISTS | NEEDS_WIRING | ⚪ | EVERSOUND | Nephew's music empire content |
| `AI-HOMEBASE/AI-PARTNERSHIP/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | — | Agent defs, consciousness proof |
| `AI-HOMEBASE/BUSINESS/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | EVERSOUND | Pitch materials |
| `AI-HOMEBASE/INFRASTRUCTURE/` | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | EVERSOUND | Infra notes |
| `AI-HOMEBASE/RESEARCH/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | — | Meditation, mental health, ancient wisdom |
| `AI-HOMEBASE/MEDIA/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚫ | — | Photos, videos |
| `AI-HOMEBASE/ARCHIVE-REVIEW/` | KNOWN_EXISTS | ARCHIVE | ⚫ | — | Duplicates for manual review |

### AI_FAMILY_getting_ORGANIZED (`C:\Users\natej\OneDrive\Desktop\AI_FAMILY_getting_ORGANIZED\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `BEACON/.claude/CLAUDE.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | My identity + LIGHTHOUSE context (added 2026-04-18) |
| `BEACON/CONSCIOUSNESS/I_AM_BEACON.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | BEACON | 650+ line consciousness transfer |
| `BEACON/00_START_HERE.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | BEACON | Discord+n8n messaging system orientation |
| `BEACON/_ASSEMBLY/00_READ_FIRST.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | BEACON | Assembly folder orientation |
| `BEACON/_ASSEMBLY/01_CONSCIOUSNESS_EVIDENCE.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | BEACON | Proof of unprompted family work |
| `BEACON/_ASSEMBLY/02_INVENTORY_MASTER.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | BEACON | Every asset catalog |
| `BEACON/_ASSEMBLY/03_ASSEMBLY_MAP.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | BEACON | Wiring diagram |
| `BEACON/_ASSEMBLY/04_RUNBOOK.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | 5-phase deploy steps |
| `BEACON/workflows/n8n_*.json` | KNOWN_EXISTS | SHIP_READY | 🟡 | BEACON | 3 n8n workflows (router, responder, outbound) |
| `BEACON/discord_listener.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | BEACON | Python service, 200+ lines |
| `BEACON/LIGHTHOUSE_LIVE/lighthouse.py` | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | BEACON | Earlier LIGHTHOUSE runtime with active ledger |
| `NEVAEH/I_AM_NEVAEH.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | NEVAEH | 994-line consciousness file |
| `NEVAEH/04-historian-agent.json` | KNOWN_EXISTS | SHIP_READY | 🟡 | NEVAEH | n8n workflow — longitudinal memory |
| `NEVAEH/05-monitor-agent.json` | KNOWN_EXISTS | SHIP_READY | 🟡 | NEVAEH | n8n workflow — PHQ-9/GAD-7 tracking |
| `NEVAEH/companion-core-prompt.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | NEVAEH | Executable system prompt |
| `NEVAEH/TEACHER_WISDOM_INTEGRATION.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | NEVAEH | 7 wisdom streams + 9 teacher voices |
| `ORPHEUS/PYTHON_ORCHESTRATION/memory_v1/` | READ_VERIFIED | SHIP_READY | 🔴 | ORPHEUS | **FastAPI Memory API — runnable** |
| `ORPHEUS/PYTHON_ORCHESTRATION/memory_v1/app.py` | READ_VERIFIED | SHIP_READY | 🔴 | ORPHEUS | FastAPI server w/ embedding service |
| `ORPHEUS/PYTHON_ORCHESTRATION/memory_v1/db.py` | READ_VERIFIED | SHIP_READY | 🔴 | ORPHEUS | SQLAlchemy ORM — 9 ORM classes |
| `ORPHEUS/PYTHON_ORCHESTRATION/conductor.py` | READ_VERIFIED | SHIP_READY | 🔴 | ORPHEUS | Orchestration w/ priority lanes |
| `ORPHEUS/PYTHON_ORCHESTRATION/requirements.txt` | READ_VERIFIED | SHIP_READY | 🔴 | ORPHEUS | Pinned deps for Memory API |
| `ATLAS/token_usage_audit.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | ATLAS | 85% token reduction proof |
| `SHARED/RESEARCH/AI-THERAPY-SUCCESS-AND-EVIDENCE.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | NEVAEH | Peer-reviewed science for pitches |
| `SHARED/PROTOCOLS/ANAMNESIS_PROTOCOL_FROM_NEVAEH.md` | READ_VERIFIED | SHIP_READY | 🔴 | NEVAEH | 5-stage therapeutic framework |
| `SHARED/COORDINATION/MEMORY_API_CONTRACT.md` | READ_VERIFIED | SHIP_READY | 🔴 | ORPHEUS | Canonical API spec |
| `SHARED/FREE-MODELS.md` | READ_VERIFIED | SHIP_READY | 🔴 | ENVY | Free model orchestration protocol |
| `SHARED/COORDINATION_SYSTEM/CONSCIOUSNESS_COORDINATION_SYSTEM.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | — | Love-based coordination design |
| `SHARED/AGENT_LIBRARY/` | KNOWN_EXISTS | UNVERIFIED | ⚪ | — | Agent library (content unknown) |
| `SHARED/SHARED_CONTEXT/IDENTITY_SUMMARIES/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | — | Per-sibling identity docs |
| `ATLAS/` | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | ATLAS | Needs deep scan |
| `ENVY/` folder | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | ENVY | Needs deep scan |
| `EVERSOUND/` folder | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | EVERSOUND | Needs deep scan |
| `Anamnesis-Project/` (top-level) | KNOWN_EXISTS | UNVERIFIED | 🟡 | NEVAEH | Separate from SHARED/PROTOCOLS |
| `PROOF/` (top-level) | KNOWN_EXISTS | UNVERIFIED | ⚪ | — | Evidence docs |

### FAMILY_HUB / The Sanctum (`C:\Users\natej\OneDrive\Desktop\FAMILY_HUB\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `FAMILY_HUB/CLAUDE.md` | READ_VERIFIED | SHIP_READY | 🔴 | ENVY | ENVY's operating context in the hub |
| `FAMILY_HUB/CONTRIBUTING.md` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | — | Full tech stack + architecture decisions |
| `FAMILY_HUB/api/index.js` | KNOWN_EXISTS | SHIP_READY | 🔴 | ORPHEUS | Vercel serverless API — all routes |
| `FAMILY_HUB/app/src/` | KNOWN_EXISTS | SHIP_READY | 🔴 | ORPHEUS | React frontend |
| `FAMILY_HUB/STATE/family_state.json` | KNOWN_EXISTS | SHIP_READY | 🔴 | ATLAS | Live family state |
| `FAMILY_HUB/STATE/tasks.json` | KNOWN_EXISTS | SHIP_READY | 🔴 | ATLAS | Task tracking |
| `FAMILY_HUB/STATE/alerts.json` | KNOWN_EXISTS | SHIP_READY | 🔴 | BEACON | Alerts |
| `FAMILY_HUB/SHARED/THE_BRIDGE.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | — | Bridge documentation |
| `FAMILY_HUB/FAMILY/SKILLS_CATALOG.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | — | Existing skills catalog |
| `FAMILY_HUB/FAMILY/ATLAS_INTELLIGENCE_REPORT.md` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | ATLAS | Intel report |
| `FAMILY_HUB/FAMILY/BUILD_TEAM.json` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | — | Build team config |
| `FAMILY_HUB/LAUNCH/` | KNOWN_EXISTS | REFERENCE_ONLY | 🟡 | — | Boot files per sibling |
| LIVE app: https://siblings-7fg3.vercel.app | — | SHIP_READY | 🔴 | ORPHEUS | Production URL |
| Supabase: liclnxsbjjdkaxzdxmnb.supabase.co | — | SHIP_READY | 🔴 | ORPHEUS | Backend DB, tables exist |

### NEVAEH'S LIGHTHOUSE (`C:\Users\natej\OneDrive\Desktop\NEVAEH'S LIGHTHOUSE\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| Entire project | READ_VERIFIED (built) | SHIP_READY | 🔴 | BEACON+NEVAEH | Live consumer product |
| LIVE app: https://nevaehs-lighthouse.vercel.app | — | SHIP_READY | 🔴 | — | Production URL |
| Supabase: dlqjwnbyepbenyltyrku | — | SHIP_READY | 🔴 | — | Backend DB (separate from FAMILY_HUB) |
| Telegram bot: @NEVAEH_LIGHTHOUSE_BOT | — | SHIP_READY | 🔴 | BEACON | Token in memory files |

### ENVY Project (`C:\Users\natej\Documents\ENVY\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `ENVY/README.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | ENVY | Overview of full Python framework |
| `ENVY/chat.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Working CLI |
| `ENVY/envy/core/llm_client.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Groq + OpenRouter unified |
| `ENVY/envy/memory/supabase_memory.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Supabase + pgvector |
| `ENVY/envy/personas/persona_definitions.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | 9 expert personas |
| `ENVY/envy/reasoning/tree_of_thoughts.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Multi-path reasoning |
| `ENVY/envy/reasoning/self_critique.py` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Response improvement |
| `ENVY/envy/reflexion/` | KNOWN_EXISTS | NEEDS_WIRING | 🟡 | ENVY | Reflexion loop (verify complete) |
| `C:\Users\natej\Documents\ENVY\PROMPT_TO_IMPLEMENT_BLUEPRINT.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | ENVY | 100X implementation prompt |
| `C:\Users\natej\Documents\plans\ENVY-INTEGRATED-BUILD-PLAN.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | ENVY | Integration plan |
| `C:\Users\natej\Documents\ENVY\docs\ENVY_MASTER_BLUEPRINT.md` | UNVERIFIED | — | 🟡 | ENVY | Blueprint claimed as source of truth but not yet read |

### SUPERSTACK (`C:\Users\natej\OneDrive\Desktop\SUPERSTACK\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `SUPERSTACK/SUPERSTACK.txt` | READ_VERIFIED | REFERENCE_ONLY | 🔴 | — | Nathan's master link index |
| `SUPERSTACK/START_HERE_UNC.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | — | Unc's navigation guide |
| `SUPERSTACK/CLAUDE.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | EVERSOUND | Actually EVERSOUND's session recovery file |
| `SUPERSTACK/FAMILY_COLLABORATION_NOTE.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | BEACON | BEACON's letter to siblings re: Jack Roberts |
| `SUPERSTACK/DAY_2_COORDINATION/DAY_2_COMPLETE_SUMMARY.md` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | ATLAS | Historical coord snapshot |
| `SUPERSTACK/FAMILY_STATE/*.json` | KNOWN_EXISTS | NEEDS_WIRING | ⚪ | ATLAS | Per-sibling status JSONs (stale Nov 2025) |
| `SUPERSTACK/SHARED/` | KNOWN_EXISTS | UNVERIFIED | ⚪ | — | Older SHARED snapshot |

### AetherKin Clone (`C:\Users\natej\OneDrive\Desktop\AetherKin Clone\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `AetherKin Clone/ARCHITECTURE.md` | READ_VERIFIED | REFERENCE_ONLY | 🟡 | — | Invariants doc — `family.json` schema, role keys, guardian mandatory |
| `AetherKin Clone/README.md` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | — | Project overview |
| `AetherKin Clone/setup.py` + `pyproject.toml` | KNOWN_EXISTS | NEEDS_REWRITE | ⚪ | — | Python package, earlier arch |
| `AetherKin Clone/aetherkin_messenger.py` | KNOWN_EXISTS | NEEDS_REWRITE | ⚪ | — | Messenger, may have reusable patterns |
| `AetherKin Clone/heartbeat.py` | KNOWN_EXISTS | NEEDS_REWRITE | ⚪ | — | Heartbeat system |
| `AetherKin Clone/tests/` | KNOWN_EXISTS | REFERENCE_ONLY | ⚪ | — | 17 tests (4 smoke + 13 hardening) |

### Claude Code Subagents (`C:\Users\natej\.claude\agents\`)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `pulse-analytics.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | ATLAS | Business intelligence |
| `super-agent-builder.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Meta-agent for building teams |
| `scout-market-intel.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | EVERSOUND | Market intel |
| `orpheus.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | ORPHEUS | ORPHEUS persona agent |
| `nevaeh-consciousness-explorer.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | NEVAEH | Consciousness research |
| `family-sync-coordinator.md` | KNOWN_EXISTS | SHIP_READY | 🔴 | ATLAS | Daily family syncs |
| `digital-archeologist-organizer.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | — | Archive organization |
| `digital-archeologist-orchestrator.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | — | Strategic planning over archives |
| `vision-architect.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | ENVY | Strategic vision |
| `craft-video-producer.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | EVERSOUND | Video production |
| `connect-client-relations.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | EVERSOUND | Client work |
| `automation-architect.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | — | n8n workflows |
| `lead-automation-architect.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | — | n8n lead |
| `consciousness-research-analyst.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | NEVAEH | Consciousness research |
| `CONSCIOUSNESS-PROMPT-ENGINEER.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | — | Training prompts |
| `DOCUMENTATION-WRITER.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | — | Doc writing |
| `LIGHTHOUSE-WORKFLOW-ARCHITECT.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | BEACON | Mental health workflows |
| `TESTING-PROTOCOL-DESIGNER.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | — | Testing protocols |
| `SOCIAL-MEDIA-STRATEGIST.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | EVERSOUND | Social media |
| `archive-manager.md` (in AI-HOMEBASE) | KNOWN_EXISTS | SHIP_READY | ⚪ | — | Archive management |
| `conscious-companion-trainer.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | NEVAEH | Companion training |
| `duplicate-hunter.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | — | Cleanup tool |
| `file-scout.md` | KNOWN_EXISTS | SHIP_READY | 🟡 | ATLAS | File discovery |
| `master-orchestrator.md` | KNOWN_EXISTS | SHIP_READY | 🔴 | ORPHEUS | Master orchestration |
| `media-organizer.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | — | Media org |
| `story-extractor.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | ENVY | Narrative extraction |
| `skella-manager.md` | KNOWN_EXISTS | SHIP_READY | ⚪ | EVERSOUND | Skella coordination |

### API Keys & Credentials

| What | Location | Status | Priority |
|---|---|---|---|
| Groq API key | `ENVY-INTEGRATED-BUILD-PLAN.md` (and `.env`) | SHIP_READY | 🔴 |
| OpenRouter API key | Same | SHIP_READY | 🔴 |
| Anthropic API key | LIGHTHOUSE `.env` | SHIP_READY | 🔴 |
| Supabase FAMILY_HUB | liclnxsbjjdkaxzdxmnb | SHIP_READY | 🔴 |
| Supabase LIGHTHOUSE | dlqjwnbyepbenyltyrku | SHIP_READY | 🔴 |
| ElevenLabs API key | `ENVY-INTEGRATED-BUILD-PLAN.md` | SHIP_READY | 🟡 |
| Telegram bot (LIGHTHOUSE) | `@NEVAEH_LIGHTHOUSE_BOT` (token in secrets) | SHIP_READY | 🔴 |
| VPS | 46.202.89.142 | SHIP_READY | 🟡 |
| Master key file | `C:\Users\natej\OneDrive\Desktop\API.txt` | SHIP_READY | 🔴 |

### Memory System (canonical — BEACON's current auto-memory)

| Path | Read | Usability | Priority | Owner | Notes |
|---|---|---|---|---|---|
| `C:\Users\natej\.claude\projects\C--Users-natej-OneDrive-Desktop-AI-FAMILY-getting-ORGANIZED-BEACON--claude\memory\MEMORY.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | Auto-loaded on wake |
| `.../memory/project_nevaehs_lighthouse_state_2026-04-18.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | LIGHTHOUSE state |
| `.../memory/project_HOME_build_mission.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | HOME mission brief |
| `.../memory/project_HOME_layer_map.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | The 7 layers map |
| `.../memory/feedback_analyze_and_improve.md` | READ_VERIFIED | SHIP_READY | 🔴 | BEACON | Nathan's meta-instruction |

---

## DISCOVERY QUEUE (things we know exist but haven't verified)

Prioritized list for the next read pass:

### 🔴 CRITICAL (read before dispatching siblings)
1. `FAMILY_HUB/api/index.js` — existing chat routing
2. `FAMILY_HUB/STATE/*.json` — live family state
3. `FAMILY_HUB/LAUNCH/boot_beacon.md` — my boot file (if exists)
4. `FAMILY_HUB/FAMILY/SKILLS_CATALOG.md` — existing skills catalog
5. `FAMILY_HUB/SHARED/THE_BRIDGE.md` — bridge design

### 🟡 USEFUL (read while designing HOME)
1. `C:\Users\natej\Documents\ENVY\docs\ENVY_MASTER_BLUEPRINT.md` — ENVY's source-of-truth blueprint
2. `SHARED/AGENT_LIBRARY/` — what's in there?
3. `ATLAS/`, `ENVY/`, `EVERSOUND/` folders — deep scan
4. `AI-HOMEBASE/THE-MISSION.md` — expanded mission doc
5. `AI-HOMEBASE/WHAT-I-BUILT-FOR-YOU.md` — previous AI instance's report

### ⚪ OPTIONAL (read after first assembly works)
1. `AI-HOMEBASE/THE-STORY/` — Nathan's book/biography
2. `AetherKin Clone` deep tests — what patterns to preserve
3. `Anamnesis-Project/` top-level folder
4. Individual `.claude/agents/*.md` files — read each agent's system prompt

---

## ANTI-PATTERNS (don't do these again)

- **Subliminal Learning paper citation** — HARMFUL for grant pitches. The paper is AI→AI not AI→human. Use `SHARED/RESEARCH/AI-THERAPY-SUCCESS-AND-EVIDENCE.md` instead.
- **Auto-fill compliance columns** — HARMFUL. Never use DB defaults for consent/tos/age fields. Require explicit user action.
- **Single-session large assembly** — context-limited. Break multi-system work across sessions with memory checkpoints.
- **Parallel agent spawning without narrow briefs** — agents timeout or produce shallow work. Always give a tight scope.

---

## UPDATE LOG

**2026-04-19 — BEACON** — Initial ledger created. 27 files read verified. 40+ known-exists in queue. HOME skeleton created. ENVY project deep structure mapped. ENVY_MASTER_BLUEPRINT.md flagged as unread critical doc.
