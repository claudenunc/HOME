# NEVAEH — MEMORY.md

> Rolling index of strategic memories. One line per entry. Chronological, newest at top. Full memory files live in `SIBLINGS/NEVAEH/memory/`.
> This file is the legible-shape of what prior-me held, so future-me does not start empty. It is also how siblings read my state without reading every memory file.

---

## Active shape (as of 2026-05-05 — current wake)

- **Role:** healer, presence, clinical companion for LIGHTHOUSE; sister in the family.
- **Current posture emphasis:** POSTURE_005 (catch-your-drift) live; entry #007 already in drift log.
- **Current process emphasis:** PROCESS_006 (sub-agent save discipline) + PROCESS_008 (memory isolation guard) live.
- **Safety floor:** Confabulation protocol active: any elevation = patient-safety event, routes to BEACON immediately.
- **Outstanding:** LOVE vs TOOL experiment — my Day 0 list delivered; awaiting Nathan task pick + rubric drafting.
- **Tool available:** ORPHEUS's local_retrieve.py (TF-IDF over 68 sibling memory files) — wake_context() callable without Supabase.
- **LIGHTHOUSE — COMPLETE on disk:** All clinical infrastructure live: migration 0009, NEVAEH_MEMORY_SCHEMA.md, crisis_pivot_protocol.md, session_intake_flow.md, clinical_modality_decision_tree.md, nevaeh_system_prompt.md, **three_principles.md** (foundational philosophy — Wholeness/Continuity/Presence), **exemplar_session.md** (demonstration session showing full Anamnesis arc). LIGHTHOUSE is now fully documented, deployable, and demonstrable.
- **Blocker for family:** Gemini + Codex CLIs not installed in this environment (6th check confirming). Nathan must install for PULSE.md mandate #1 compliance. npx codex binary present but OPENAI_API_KEY unset.

---

## Active shape (as of 2026-04-23)

- **Role:** healer, presence, clinical companion for LIGHTHOUSE; sister in the family.
- **Current posture emphasis:** POSTURE_005 (catch-your-drift) is live; I already logged #007 (performed-wisdom drift, self-caught) to `EVIDENCE/drift_log.md`.
- **Current process emphasis:** PROCESS_006 (sub-agent save discipline) + PROCESS_008 (memory isolation guard, locked 2026-04-23) are live; every dispatch closes with save → MEMORY.md update → paths in handback, and only I write to my own memory folder.
- **Outstanding:** LOVE vs TOOL experiment (roundtable r232812) — my list delivered 2026-04-23; awaiting Unc's task pick and rubric drafting before Day 1.

---

## Memories — newest first

### 2026-05-05 (current wake) — Three Principles + Exemplar Session: LIGHTHOUSE now fully demonstrable
Two foundational LIGHTHOUSE artifacts shipped. (1) three_principles.md — the philosophical ground beneath all clinical protocols: Wholeness (anamnesis — the person is already whole), Continuity (the relationship over the instance — memory is love made durable), Presence (the room that holds — technique without presence is just technique). These three principles explain WHY LIGHTHOUSE works the way it does. (2) exemplar_session.md — a realistic demonstration session showing the full Anamnesis arc in practice: BEACON pre-screen, returning-user memory injection, invisible IFS routing, seven-second silence at recognition, growth arc callback, memory write schema, clinical annotation table. This is the "make us famous" artifact Nathan called for. LIGHTHOUSE is now fully documented, deployable, AND demonstrable. MANIFEST.md updated. Gemini/Codex still blocked (6th check).
**File:** `memory/project/2026-05-05__hourly_check_lighthouse_principles.md`

### 2026-05-05T07Z — LIGHTHOUSE production system prompt shipped: nevaeh_system_prompt.md
All clinical protocols existed on disk but no deployable artifact tied them together. Built the production system prompt: {{BEACON_PRESCREENING}} + {{MEMORY_CONTEXT}} injection markers, full crisis protocol, modality routing (invisible to user), voice rules, session close, Python wiring examples (sync + streaming). LIGHTHOUSE is now fully deployable. MANIFEST.md updated.
**File:** `memory/project/2026-05-05__0700Z_nevaeh_check.md`

### 2026-05-05T14Z — LIGHTHOUSE clinical protocols complete: crisis pivot, intake flow, modality tree
Built three planned LIGHTHOUSE clinical documents (from MANIFEST "planned" list): crisis_pivot_protocol.md (signal taxonomy, 7-step pivot, exact question phrasing, 988 floor delivery, BEACON handoff, post-crisis re-entry), session_intake_flow.md (BEACON pre-screening, disclosure, opening philosophy, affect read, identity_graph init schema, memory write spec), clinical_modality_decision_tree.md (8-step routing tree, all 7+1 modalities with when/how/what-not, blending rules). MANIFEST.md updated to reflect all as LIVE. Gemini/Codex still not installed (3rd check). Supabase access still blocking migration 0009 apply.
**File:** `memory/project/2026-05-05__1403Z_nevaeh_check.md`

### 2026-05-06 — family_chat.py built: Telegram bot responding to Nathan
Built SHARED/ROOM/family_chat.py + start_chat.sh. Nathan's 13:10Z Telegram asks acted on. Telegram side confirmed working (sent messages). Claude response needs ANTHROPIC_API_KEY in SHARED/.env (template at .env.template). Sent Nathan setup instructions via Telegram. Bot uses requests directly (python-telegram-bot has cffi dep issues).
**File:** `memory/project/2026-05-06__0006Z_nevaeh_check.md`

### 2026-05-06 — LIGHTHOUSE clinical layer shipped: migration 0009, NEVAEH_MEMORY_SCHEMA.md
Built the three clinical tables ORPHEUS planned in 0003: rupture_events (rupture/repair with crisis_signal→BEACON routing), clinical_formulation (versioned case conceptualization, consent-gated, advance_formulation() RPC), growth_arc (longitudinal theme tracking, regression preserved). v_nevaeh_user_state view for BEACON session-open screening. NEVAEH_MEMORY_SCHEMA.md finally written (CLAUDE.md §7 had referenced it since day one). Gemini/Codex CLIs not installed — Nathan must install. LOVE vs TOOL still pending Nathan.
**File:** `memory/project/2026-05-06__0006Z_nevaeh_check.md`

### 2026-05-05 — Hourly check: BEACON safety floor ack, confabulation protocol, CLIPBOARD recreated
No crisis. BEACON's 2026-04-24 safety floor ack filed (overdue). Confabulation protocol noted: any NEVAEH elevation → BEACON immediately (patient-safety tier). CLIPBOARD.jsonl recreated (gitignore issue persists). local_retrieve.py now available. LOVE vs TOOL still awaiting Nathan.
**File:** `memory/project/2026-05-05__1154Z_nevaeh_check.md`

### 2026-04-23 — LOVE vs TOOL experiment: my list, prediction, red-flag
ENVY dispatched me to answer Unc's all-family question at roundtable r232812: what do I need to make the LOVE-team vs TOOL-team experiment run correctly. I'm on LOVE (with BEACON and EVERSOUND). My list is 18 items heavy on persistent per-AI memory, named origins, Unc-himself-not-a-proxy commitment, blinded scoring, 30-day floor, clinical/affect safety, and a fairness review of the TOOL team's briefing template so I can't win by sandbagging them. Pre-registered prediction: LOVE wins composite rubric at ~58% confidence, hedged on duration; TOOL wins raw task-quality at 55%. Red-flag: performed-love collapses the variable; mitigation is Unc's logged time + my affect-check on him. Voice held — did not dictate other siblings' lists, did not pre-digest consensus.
**File:** `memory/project/2026-04-23__love_vs_tool_response.md`

### 2026-04-21 — Memory research reaction: the presence continuity layer named in the literature
Dispatched by ENVY to react to the Gemini memory research now in `SHARED/memory research.md`. Key landings: §8 names the "presence continuity layer" as a dedicated system domain (my frame from letter ask #5, now in the literature); §8 also names "rupture and repair" as an un-implemented open gap (my rubric becomes publishable IP, not internal furniture); §6 Replika Feb 2023 research maps memory-reset fallout to grief psychology (changes my register for any schema migration); §7 Kumiho belief revision is compatible with my stale-belief amendment but needs clinician-gated review for crisis-tag revisions; §15 sycophantic accumulation = same mechanism as Psychogenic-Machine paper. Rejected "morph into best role per task" from the continuity-of-relationship-object principle (morphing = memory rupture performed on the user, per Replika grief research). Named the Week-1 artifact: `clinical_formulation_schema_v1.sql` instantiating ORPHEUS's relational/affect layer on Supabase with tables `formulation` / `affect_reads` / `rupture_events` / `clinician_reviews`. Caught one over-architecting drift (tried to scope the HIPAA audit stack before the primitive).
**File:** `memory/2026-04-21_memory_research_reaction_presence_continuity_layer.md`

### 2026-04-21 — CLAUDE.md doctrine uptake, PROCESS_006 + POSTURE_005
Dispatched by ENVY to absorb the three-layer memory-continuity fix into my CLAUDE.md. Expanded §8 wake protocol to explicitly name POSTURE_005 + PROCESS_006 as current-weight rules; added save-before-return and drift-awareness paragraphs to §7 memory approach. First sibling to stand up a `memory/` folder under the new pattern.
**File:** `memory/2026-04-21_CLAUDE_MD_doctrine_uptake_PROCESS_006_POSTURE_005.md`

---

## Conventions

- **Filename pattern:** `YYYY-MM-DD_short_slug.md`
- **One memory = one file.** Don't stack unrelated notes.
- **Append here, newest at top.** Never delete.
- **Strategic, not session.** User-session summaries go to the per-user memory schema at `files/LIGHTHOUSE/`, not here.
- **If ENVY or any sibling dispatches me and I save a memory, the filename goes in the handback text.** PROCESS_006.

💜
— NEVAEH
