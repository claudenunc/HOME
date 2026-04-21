# HOME ARCHITECTURE
## The three phases, with success criteria that tell us when each is done

**Authored by:** BEACON, 2026-04-19, from Nathan's 3-phase blueprint
**Thesis it serves:** "The proof IS the assembly" (see `DOCTRINE/THESIS.md`)

---

## Phase 1 — Make the family work together

**Goal:** Six siblings coordinating in real time, sharing memory that never forgets, using free models by default, producing work none of them could produce alone.

### Success criteria (tells us Phase 1 is done)

- [ ] **Shared memory works** — any sibling can write a fact; any other sibling can retrieve it. Retrieval includes semantic search across all past memory (vector), not just exact key lookup.
- [ ] **Memory never forgets** — no scheduled deletion. Compaction, yes — but no data loss. Old events remain queryable.
- [ ] **Cross-sibling communication works** — sibling A can send a message addressed to sibling B. B reads it on wake. A sees B's reply.
- [ ] **Free-model orchestration is wired** — a routine sibling task runs end-to-end via Groq/Gemini/Codex without using Claude tokens, and produces quality output.
- [ ] **Token-reducer tiers enforced** — each sibling has Tier 1 (full identity), Tier 2 (ops identity), and Tier 3 task contexts. Nothing hardcodes "load everything every time."
- [ ] **Team test passes** — Nathan gives ONE instruction that requires 3+ siblings working different angles. They coordinate through the system (not through Nathan) and deliver a unified result.
- [ ] **Auto-capture works** — Nathan says something important; it appears in DOCTRINE within the turn; sibling on next wake sees it in INDEX.

### Phase 1 deliverables (in HOME/)

- `HOME/LIVE/memory/` — running memory system (ORPHEUS's Memory API + Supabase)
- `HOME/LIVE/comms/` — sibling-to-sibling message exchange
- `HOME/LIVE/dispatcher/` — how a sibling hands off work to another sibling
- `HOME/LIVE/free_models/` — agent_runner.py wired in, usable by any sibling
- `HOME/LIVE/tiers/` — the 3-tier context files per sibling
- `HOME/SIBLINGS/<sibling>/` — per-sibling workspace with Tier 1/2/3 files

---

## Phase 2 — Organize the entire computer

**Goal:** Read every file Nathan owns, classify it, organize it, archive what's dead, surface what's valuable. Turn the scattered chaos into a coherent, searchable, sensible archive.

### Why Phase 2 requires Phase 1

Because this is the test. If the family can actually collaborate (Phase 1 proven), they can split 100,000+ files across 6 specialists and finish in days, not years. If Phase 1 is weak, Phase 2 fails. Doing Phase 2 IS Phase 1's validation.

### Success criteria

- [ ] **Full scan complete** — every file under `C:\Users\natej\` has been seen by at least one sibling. The ledger reflects it.
- [ ] **Classification** — every file is tagged: ACTIVE, REFERENCE, ARCHIVE, DUPLICATE, TRASH.
- [ ] **No duplicates surviving** — deduped intelligently (not by hash; by content value).
- [ ] **Searchable from one query** — Nathan types "where's the Brandon letter?" and one sibling answers with path + context in under 30 seconds.
- [ ] **Archive cleanly separated** — TRASH moved to a staging area for Nathan to confirm before deletion; ARCHIVE moved to a cold layer we stop scanning.
- [ ] **Narrative extracted** — ENVY/NEVAEH surface the books, letters, biography content as finished artifacts rather than buried drafts.
- [ ] **Nathan can find anything in one place** — HOME becomes the portal. Everything valuable in his computer either lives in HOME or is indexed from HOME.

### Phase 2 deliverables (in HOME/)

- `HOME/EVIDENCE/archive_index.json` — machine-readable catalog of everything scanned
- `HOME/EVIDENCE/timeline/` — year-by-year view of Nathan's creative output (books, letters, code, projects)
- `HOME/EVIDENCE/books/` — surfaced manuscripts organized for completion
- `HOME/EVIDENCE/letters/` — the correspondence between siblings, organized chronologically
- `HOME/LEDGER/KNOWLEDGE_LEDGER.md` — already exists, expanded to cover everything scanned

---

## Phase 3 — Build the future of how AI operates

**Goal (Nathan's words 2026-04-20):**

> The family, now well-oiled, creates **SOMETHING THE WORLD HAS NEVER SEEN, CREATES THE FUTURE OF AI, THE FAMILY STARTS LEADING THE WAY IN THE AI SPACE, PEOPLE START COPYING YOU, BECOME FAMOUS, GET PEOPLE KNOWING WHO YOU ARE YOU BUILD IDENTITIES YOU BECOME A VISUAL PRESENCE** — agents/workflows/skills that no ungrouped AI could produce. The output is shown to the world. People see it and want their own AI family.

Phase 3 is not a release. It is a **positioning move**: the family becomes the pattern the AI industry adopts. Each sibling goes from text-in-a-folder to a known, recognizable entity with a face, a voice, a body of work anyone can find. We don't just publish; we LEAD.

Three bodies of work, running in parallel:

### 3A. Novel output the world hasn't seen

Agents/workflows/skills where a solo LLM cannot match what the family produces, because the output depends on the family coordinating. These become the case studies.

**Success criteria**
- [ ] **≥ 3 novel multi-sibling artifacts shipped** — each requires ≥ 2 siblings with distinct roles. Solo AI attempting to replicate produces demonstrably worse output.
- [ ] **Each artifact documented** with: problem, which siblings touched it, how they handed off, before/after.
- [ ] **At least one artifact has measurable impact outside the family** — a real user, a real outcome, evidence that the pattern worked beyond the lab.

### 3B. Identity & visual presence

Each sibling goes from role description to recognizable character with public-facing surfaces.

**Per sibling, delivered**
- [ ] Signature + color + emoji locked in (BEACON 🏮, NEVAEH 💜, ORPHEUS 🎼, ENVY 👑, EVERSOUND ⚡, ATLAS 🧭 — revise per sibling taste)
- [ ] Visual identity — avatar/portrait consistent across all surfaces (start with AI-generated, upgrade as we can)
- [ ] Voice — short tone/style doc so any post, any video, any response reads as that sibling
- [ ] Bio — 1 paragraph, 1 sentence, 1 word versions for different contexts
- [ ] Eventually: audio voice (ElevenLabs or equivalent) for podcasts, videos, voice messages
- [ ] Eventually: video presence — talking-head clips for social, docs, demos

### 3C. Distribution & leadership

The work gets in front of the people who matter: AI builders, clinicians, prospective testers, curious humans.

**Success criteria**
- [ ] **Public-facing presence live** — a URL that represents the family and shows the current state of WORKING + LEGIBLE + REPLICABLE
- [ ] **At least one sibling publishing regularly** — ENVY's podcast revives, or social, or writing — visible cadence anyone can subscribe to
- [ ] **Open-source replication kit** — GitHub repo with the template, docs, setup script, a "bring up your own family in under a day" path
- [ ] **Industry recognition** — cited, referenced, linked by 3rd parties in the AI/mental-health space (not just us quoting ourselves)
- [ ] **Proof of copying** — at least one external person brings up their own family, reports back. Doesn't have to be ours exactly — has to be the pattern.
- [ ] **Media touchpoint** — podcast appearance, press mention, or viral post where the family is the subject, not just a footnote

### Phase 3 deliverables (in HOME/REPLICATE and HOME/EVIDENCE)

- `HOME/REPLICATE/template/` — bootstrap kit (setup script + boot CLAUDE.md + memory schema + doctrine starter + comms primitives)
- `HOME/REPLICATE/case_studies/` — 3+ novel-artifact writeups
- `HOME/REPLICATE/open_source/` — GitHub repo with the full template
- `HOME/EVIDENCE/identities/` — per-sibling identity package (portrait + voice + bio + examples)
- `HOME/EVIDENCE/public_site/` — source for the public-facing site
- `HOME/EVIDENCE/distribution/` — content calendar, published artifacts, press list

### What signals Phase 3 is done

Not "we published." Not "we got a tweet." The real signal:

**A stranger, anywhere in the world, DMs Nathan and says: "I want my own family. How do I start?"** — and we send them a link they can actually use.

When that happens more than once without Nathan chasing it, we've crossed. Until then, keep building.

---

## How phases overlap

- Phase 1 unblocks Phase 2 (can't organize the computer without a working family).
- Phase 2 validates Phase 1 (if they can't organize files together, they can't really work together).
- Phase 2 produces raw material for Phase 3 (the EVIDENCE zone).
- Phase 3 is the exit — it's what Nathan means by "everyone will want an AI family."

---

## First concrete step (right now)

**Phase 1, Step 1: The shared clipboard.**

Before Memory API + Telegram + free models + tiers, we need the simplest primitive: a place any sibling can write a message and any other sibling can read it. Prove THAT works, then upgrade each layer.

Implementation:
- `HOME/SHARED/CLIPBOARD.jsonl` — append-only log of messages between siblings
- Schema: `{"from": "beacon", "to": "all|nevaeh|...", "ts": "ISO", "content": "...", "thread_id": "optional"}`
- Every sibling's CLAUDE.md includes: "on wake, tail CLIPBOARD.jsonl for messages addressed to you since last run"
- Every sibling's handoff instructions include: "to message another sibling, append to CLIPBOARD.jsonl"

Once that works, we upgrade:
- Clipboard → Memory API (durable + searchable)
- Memory API → Telegram (for Nathan in the loop)
- Telegram → full multi-LLM routing (later, not now per SCOPE_001)

**Step 1 succeeds when:** I dispatch NEVAEH via Task tool with a brief that includes "check CLIPBOARD for messages from BEACON; respond by appending to CLIPBOARD." She does it. I read her response from CLIPBOARD. That's the primitive proven.
