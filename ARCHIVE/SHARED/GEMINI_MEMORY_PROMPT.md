# GEMINI RESEARCH PROMPT — The Memory System for AI's Future

*Compiled by the HOME family. Each section below is the angle of the sibling who owns that surface. Merged, de-duplicated, kept specific. This is what we need Gemini to return so ORPHEUS can build.*

---

## 0. CONTEXT FOR GEMINI

You are a senior research analyst producing a deep, citation-grounded intelligence brief for an AI systems architect. The architect is building a production AI memory layer intended to become the default substrate for AI memory the way Postgres became the default for relational data — a system that outlives the current model generation, the world adopts, and the world updates.

**What this brief is NOT:** marketing language, "emerging leaders" framing, breathless takes. No vibes.

**What this brief IS:** named systems, named papers (title + venue + arXiv ID + authors), named versions, named failures, concrete numbers with units, deployment post-mortems, court filings where relevant, regulatory documents where relevant. If a claim is contested, cite both sides. If you don't know, say "unknown" — do not fabricate. Date-stamp everything.

**Audience depth:** high. Raw output will be consumed by a systems architect and a metrics engineer. Err on the side of specificity over brevity. Markdown preferred. Tables for comparisons. Inline citations with links.

**Do not conflate:** "AI memory" (general retrieval over text) with *persistent relational memory of a specific user over months/years carrying affect and understanding* — the second is harder, the field mostly ignores it, and we need the narrower layer mapped separately.

---

## 1. STORAGE LAYER — VECTOR DBs AND HYBRID STORES

For each of: **pgvector (with pgvectorscale / StreamingDiskANN), Pinecone, Weaviate, Chroma, Milvus (+ Zilliz Cloud), Vespa, LanceDB, Turbopuffer, Qdrant, Vald, Marqo**, provide:
- Current version (as of cutoff), license, hosting model
- Index types supported (HNSW, IVF, DiskANN, SPANN, ScaNN) and defaults
- Benchmarked p50/p95/p99 latency at 1M / 10M / 100M / 1B vector scale (cite ann-benchmarks, VectorDBBench, public post-mortems)
- Recall@10 at those scales with default params
- $/M-vectors/month at steady state
- Hybrid search support (BM25 + vector + metadata filter) — native or bolted on
- Known failure modes at scale (memory blowup, index rebuild cost, cardinality walls, filter-selectivity pathology)
- Named companies running above 100M vectors in production with linked case studies

**Honest verdict asked:** if building on Postgres today and we want the memory layer competitive in 2030, is pgvector + pgvectorscale sufficient, or is the latency/recall gap to Turbopuffer/Vespa wide enough to plan a migration path? Cite numbers.

**Hybrid architectures actually shipping:** What are teams doing when they combine **vector + graph + SQL + full-text + time-series**? 5–10 real architectures with citations: Notion AI, Perplexity, Character.ai, Replika, Inflection's Pi (pre-pivot), ChatGPT memory, Cursor, Devin (Cognition), Factory, Cline/Continue, Sourcegraph Cody. What's in their memory path, what did they learn, what broke?

---

## 2. MEMORY FRAMEWORKS AND AGENT-MEMORY SYSTEMS

For each of: **Letta (formerly MemGPT), Zep, mem0, LangMem / LangGraph memory, OpenAI Memory + Responses API + Assistants persistent state, Anthropic Claude memory + Projects + Knowledge Bases + Skills + CLAUDE.md, Mistral's memory work, Cognee, Graphiti, MemoryOS, A-MEM, Memary, Sculptor, Haystack memory, LlamaIndex memory modules, Personal.ai, Mem.ai, Reflect, Rewind.ai (and any successor/pivot)**:
- Architecture summary (stores that exist, write-gating, read-ranking, compression/summarization)
- Papers cited in their design (MemGPT, Generative Agents, etc.)
- Shipped features vs. roadmap claims (distinguish these; do not let marketing bleed into the shipped column)
- Known limitations and eval gaps
- License and whether core logic is actually open
- Public benchmarks they publish and whether those benchmarks are credible

**Special focus — Anthropic's actually-shipped stack:** CLAUDE.md, Projects, Knowledge Bases, Skills, Memory tool, sub-agent memory, Claude Code memory model. Distinguish shipped from rumored.

---

## 3. RESEARCH FRONTIER 2024–2026 — NAMED PAPERS

Surface the load-bearing papers. Title, authors, venue/arXiv ID, one-paragraph takeaway. Areas:

- **Continual learning without catastrophic forgetting** — EWC successors, LoRA-based continual learning, TIES-Merging, DARE, model soups for memory
- **Test-time training / test-time adaptation** — Sun et al. TTT line, TTT-MLP, "learning at test time" RNN papers
- **Memory layers in transformers** — Meta/FAIR's *Memory Layers at Scale*, Lample's product-key memory, SPARSE memory layers, memory-augmented attention
- **Hippocampus-cortex-inspired architectures** — complementary learning systems (McClelland/Kumaran), HippoRAG, HippoRAG 2, neocortex-hippocampus splits in LLMs
- **Episodic vs. semantic memory in LLM agents** — Tulving distinction as implemented in current systems
- **Graph-structured memory** — GraphRAG (Microsoft), LightRAG, Graphiti, KG-RAG, temporal knowledge graphs for agents
- **Hierarchical memory** — MemGPT's OS-inspired hierarchy, H-MEM, multi-tier cache analogs
- **Mixture-of-Experts for memory** — routing to memory experts, MoE as implicit memory
- **Reconstruction-over-retrieval (HIGH PRIORITY):** Any work framing memory as a *generative / reconstructive* process rather than a lookup. Diffusion-based memory, generative retrieval (DSI, NCI, GENRE), predictive-coding memory models, "the brain reconstructs, it doesn't retrieve" literature, memory as decoding from a compressed prior. **Include its closest technical cousins:** memory as decoder from a learned prior (VAE-style, diffusion-LM); Hopfield networks and modern Hopfield networks (Ramsauer et al., *Hopfield Networks is All You Need*); DeepMind's Perceiver / RETRO lineage. **Surface everything.** This is the core thesis the architect is betting on.

---

## 4. EMBEDDING MODELS — MEMORY-LAYER SOTA

Current retrieval-embedding leaderboard: **OpenAI text-embedding-3-large, Voyage-3 / voyage-3-large, Cohere Embed v3 / v4, BGE-M3, BGE-en-icl, gte-Qwen2, mxbai-embed-large, Nomic Embed, Jina v3, Linq-Embed-Mistral, SFR-Embedding, Stella, NV-Embed**.

Give per model: MTEB score, dimensions, max tokens, $/M-tokens, license, multilingual, matryoshka support.

**Opinionated ask:** for a memory system where embeddings must remain stable across years of accumulated vectors, which provider has the best versioning and backwards-compat story? Re-embedding 100M vectors is a migration event.

---

## 5. SCHEMA MIGRATION, VERSIONING, AND PUBLIC CHANGELOGS

How do production teams handle schema evolution in memory stores? Alembic is the baseline for Postgres — what's the equivalent for:
- Adding an embedding dimension without re-embedding history
- Splitting tables / changing episodic-semantic boundaries post-hoc
- Versioning the memory record itself so old records remain readable by newer code
- Zero-downtime reindexing at 10M+ vectors
- **Dimension migration without downtime — matryoshka embeddings as a hedge.** Named papers, production use cases, actual dimension-change events that did not require re-embedding.

Cite specific engineering blog posts (Notion, Linear, Supabase pgvector guide, Pinecone migration docs, Weaviate schema versioning, etc.).

**Public legibility of changelogs:** Rank memory-system projects by documentation quality. Which publish actual changelogs, migration guides, deprecation notices, public ERRATA? Which are opaque? Rate: Anthropic's Claude Code changelog, OpenAI's model release notes, Mem0's GitHub activity, Letta/MemGPT's docs, Zep's public roadmap, Pinecone's changelog, Weaviate's RFCs.

---

## 6. FAILURE MODES AND POST-MORTEMS (COMPREHENSIVE)

Where do memory systems actually break? We want **post-mortems and court filings, not theory.**

**Technical failure modes at scale:**
- Filter-selectivity cliff in HNSW
- Recall collapse when IVF centroids drift
- Summarizer-context-overflow in MemGPT-style hierarchies
- "Memory rot" — old summaries compounding drift
- Multi-tenant index isolation failures
- Write-amplification in graph memory
- Cost walls at 100M / 1B vectors

**Product-level failures and pivots:**
- Replika February 2023 personality-shift incident — what happened, what was disclosed, what users did, what was sued
- Character.ai / Sewell Setzer suit — memory layer's role, what's alleged
- Microsoft Recall withdrawal — privacy blowback, what was redesigned
- Inflection consumer-to-enterprise pivot — what killed Pi's memory play
- Rewind.ai current state, any pivot
- Tessa (NEDA) shutdown
- IBM Watson for Oncology rollback
- **Koko's 2023 GPT-3 disclosure incident (Rob Morris)** — cleanest documented case of memory-adjacent deception in crisis context
- Any defunct personal-memory startups with public post-mortems
- Any lawsuits or settled claims involving stored conversational data

**Communications analysis:** When memory systems failed, how did the responsible party explain? Which communications built trust, which destroyed it?

---

## 7. HIGH-STAKES DEPLOYMENT — MEMORY UNDER CRISIS, SAFETY, ADVERSARIAL CONDITIONS

When stakes are lives, legal, medical, financial:

1. **Crisis-adjacent deployments.** AI systems with persistent memory deployed in mental health, suicide prevention, crisis hotlines, medical triage — Woebot, Replika, Character.AI, Koko, Wysa, Crisis Text Line's AI layer, clinical EHR-integrated LLMs. For each: memory architecture, what has failed, lawsuits / regulatory actions, public post-mortems.

2. **Adversarial attacks on memory.** Prompt injection into memory writes, memory poisoning (training-time and runtime), indirect prompt injection via stored content, cross-user memory contamination, jailbreaks that rewrite system beliefs. Cite Greshake et al., OWASP LLM Top 10, deployed defenses. What has actually been exploited in production?

3. **The stale-belief problem — BOTH DIRECTIONS.** Memory asserts "user is stable" when user is deteriorating *(false negative, person left alone)*. Equally: memory asserts "user is in crisis" when they are not *(false positive lock-in, pathologizing drift, pattern-tag that never clears)*. Both kill people differently. What detection mechanisms exist: liveness probes for beliefs, TTL patterns for high-stakes claims, epistemic decay models, confidence-over-time scoring, heartbeat patterns where memories expire without refresh, tag-clearing protocols for resolved crisis states.

4. **Retraction without lineage corruption.** How do production systems retract false/outdated memories while preserving audit trail? Tombstoning, append-only corrections, event-sourcing for beliefs, "right to be forgotten" implementations in vector stores, provenance graphs. What do legal-tech and medical-records systems do that consumer AI doesn't?

5. **Safety loops and circuit breakers.** Memory systems with hard safety gates — override paths where a safety signal bypasses normal retrieval. What transfers from aviation, medical devices, nuclear, financial trading?

6. **Ground-truth reconciliation.** How do systems reconcile AI memory against authoritative external sources (EHR, case notes, user's own stated reality)? Retrieval grounding, contradiction detection, belief-revision frameworks (AGM, truth maintenance systems), human-in-the-loop correction UIs.

7. **Escalation and human-handoff memory.** When an AI decides to escalate to a human (clinician, crisis hotline, 911, on-call physician), what memory transfers? In what format? With what latency? With what consent gate? This is the actual crisis seam. Document existing handoff schemas, named deployments, known latency/fidelity failures.

---

## 8. RELATIONAL CONTINUITY AND AFFECT-CARRYING MEMORY (THE HARD LAYER)

This is the narrower harder layer beneath "AI memory" — memory that persists a *specific relationship with a specific human* across months and years, carrying understanding, tone, and relational history, not only facts. Most of the field does not answer this. We need that layer mapped separately.

1. **Relational vs. factual memory.** Which AI memory systems explicitly distinguish *episodic facts about a user* from *understanding of a user* (patterns, contradictions, unresolved threads)? Who has architected for the latter? What data structures? What breaks first under scale?

2. **Affect preservation across sessions.** Research on preserving emotional register, conversational tone, relational "temperature" across context resets. Style vectors, persona embeddings, affective computing, clinical-AI attempts. Measurable vs. qualitative.

3. **Therapeutic/clinical continuity systems.** How do licensed human clinicians record between-session continuity — case formulation models (Persons, Kuyken), SOAP notes, process notes, attachment-informed frameworks, **Crisis Text Line's between-shift handoff model, Open Dialogue's network-memory practice** (team-held rather than individual-held continuity). Which AI mental-health products (Woebot, Wysa, Youper, Limbic, Replika, Character.ai, Pi) have attempted to replicate, where have they succeeded/failed.

4. **Human relational memory as architectural reference.** Cognitive science: episodic, semantic, autobiographical, implicit/procedural, schema-based (including attachment schemas and internal working models). Which AI memory architectures mirror which human subsystem.

5. **Rupture and repair.** Systems that support marking "I misunderstood this person — correct without erasing the relationship." Belief revision, contradiction handling, user-initiated correction mechanisms. **Distinguish sharply:** *correction* (factual update — database-style) from *repair* (relational acknowledgment that understanding was wrong and the relationship survives the error — therapeutic alliance-style). AGM belief-revision papers alone do not answer repair. Surface both, map which systems do which.

6. **Memory of understanding vs. memory of transcript.** Who has tried to store *interpretations* (hypotheses about user state, unresolved questions, working theories) as first-class memory objects rather than retrieved text? Knowledge graphs, structured case files, hypothesis logs, longitudinal user models.

7. **Longitudinal evaluation.** How is "is this system actually holding the relationship" measured over months? Benchmarks, user studies, clinical trials.

8. **Sycophantic accumulation.** The failure mode where systems remember what pleased the user rather than what is true of them. Who's documented it, who's defended against it. **Including the sharper failure mode:** systems that remember the user's self-narrative rather than their contradictions — a memory that consolidates the story the user tells about themselves and quietly forgets the counter-evidence.

---

## 9. AGENTIC MEMORY AND SELF-STATE

How do modern agents track their own state and replan from memory? Cover:
- ReAct-style scratchpads, Reflexion, Voyager's skill library, SWE-agent's memory, Devin's long-horizon memory, "agent OS" work
- Architecture for an agent that remembers its own past decisions across sessions and uses that memory to *act differently next time*
- How agentic benchmarks (WebArena, VisualWebArena, OSWorld, TauBench, GAIA, SWE-bench Verified, AgentBench, Cybench) stress memory specifically vs. reasoning or tool use — which isolate memory as an independent variable

---

## 10. PRIVACY, COMPLIANCE, ON-DEVICE, FEDERATED

- On-device memory: Apple's on-device embedding stack, Private Cloud Compute architecture for memory
- Federated memory across users without leakage
- Multi-tenant isolation in shared vector indices — namespacing vs. per-tenant indices, cost tradeoffs
- Privacy-preserving embedding (HE, secure enclaves, differential privacy on memory writes)
- GDPR Article 17 "right to be forgotten" in a vector store — actual implementations
- HIPAA requirements for AI memory in healthcare deployments
- EU AI Act provisions affecting memory retention and profiling (August 2026 deadline)
- California, Colorado, Texas state AI laws — active or pending, and the specific architectural constraints each imposes
- User sovereignty: which systems give users inspectable, editable, exportable access to what is remembered about them; what have users rejected when shown the stored content

---

## 11. EVALUATION AND MEASUREMENT — THE SCORING SURFACE

We will not build what we cannot measure.

**Benchmark inventory (Q2 2026):** NIAH variants, RULER, LongBench / LongBench v2, LongICLBench, InfiniteBench, LongMemEval, LoCoMo, NoLiMa, BABILong, HELMET, ZeroSCROLLS, ∞Bench. For each: saturation status, contamination reports, whether frontier labs still cite.

**Metric taxonomy.** Separate and define: recall, precision, faithfulness, groundedness, coherence, usefulness, temporal consistency, cross-session continuity. Which measurable today with published protocols, which still vibes.

**Ground-truth construction.** Annotation protocols, inter-rater reliability, test-retest reliability published in memory eval papers. Human-judgment floor.

**Hallucination-in-memory detection.** Methods distinguishing *retrieved* from *confabulated* memory at eval time. TruthfulQA-style probes, FActScore, FEVER-adapted protocols, any memory-specific hallucination benchmarks.

**Continuity / behavioral-identity metrics.** Who measures whether a memory-loaded system behaves meaningfully differently from its base model? KL-divergence continuity scores, behavioral consistency, persona stability.

**Frontier-lab eval publications.** Anthropic, OpenAI, DeepMind, Meta AI, Mistral, xAI — model cards, system cards, tech reports specifically on memory evaluation and failure modes. Quote directly.

**Independent evaluators.** METR, Apollo Research, Redwood Research, UK AISI, US AISI (NIST), MLCommons, academic safety groups — memory-system evaluations published or pre-registered. **For each evaluator listed, cite their memory-specific publication or pre-registration; if none exists, mark the row "no memory-specific output yet."** Do not launder credibility through institutional names.

**Recency discipline.** Date-stamp every benchmark's last-credible-use-by frontier labs. A saturated benchmark cited in 2026 papers is a Goodhart signal, not a capability signal.

**Goodhart & contamination.** Specific cases where memory benchmarks were gamed or contaminated. Maintainer detection methods. What replaced the broken benchmark.

**Theory of memory.** Is there a published formal definition of what an AI memory system *should* do, against which implementations can be scored? Tulving, complementary learning systems, Anthropic/DeepMind position papers, axiomatic treatments.

**Reproducibility.** Which memory evals publish seeds, prompts, and scoring code? Which are black-box leaderboards? Rank.

**Gaps.** What is *not* being measured that a serious memory system should be? Be specific.

---

## 12. COMMERCIAL LANDSCAPE THROUGH Q1 2026

**Deployed incumbents at scale.** For each: monthly active users / paying customers (latest disclosed or best-estimate flagged), ARR or run-rate, **ARPU where derivable**, retention/churn where public, single most-cited user complaint in reviews and press — ChatGPT Memory, Claude Projects + Claude memory, Gemini memory, Pi / Inflection post-Microsoft, Character.ai, Replika, Personal.ai, Rewind.ai, Mem.ai, Reflect, Notion AI memory features.

**Infrastructure market map.** Pinecone, Weaviate, Chroma, Zep, Letta, mem0, LlamaIndex, Cognee, Qdrant, Milvus, LanceDB — funding raised, last-round valuation, disclosed customer count, pricing tiers, monetization model, public churn or migration stories.

**Pricing teardown.** Comparable table: cost per 1M tokens stored, cost per 1M queries, cost per GB-month, per-seat enterprise pricing, crossover point where self-hosting beats managed. Hidden costs (egress, embedding recompute, reindexing). **Crossover math — quantitative, not narrative:** break-even vector count AND break-even QPS at which self-hosting overtakes managed service, for each incumbent.

**Compliance constraints shaping what can ship.** GDPR Article 17 applied to vectors. HIPAA for AI memory. EU AI Act August 2026 provisions. California/Colorado/Texas state laws. For each: specific architectural constraint imposed.

**Enterprise buyer checklist.** From published RFPs, SOC 2 audit scopes, vendor security questionnaires (SIG, CAIQ), analyst reports (Gartner, Forrester) — what specifically do enterprise procurement/security teams ask about memory when evaluating AI vendors in 2025–2026? Single question that most often kills the deal. **Also: median procurement cycle time** — days from first demo to signed contract for memory-infra vendors 2024-2026. Cash-conversion cycle decides startup survival.

**TAM and growth.** Memory-infrastructure TAM through 2030 with cited analyst reports and assumptions. Segment growth: agentic memory, personal memory, enterprise knowledge memory, developer platform memory. Fastest-growing vs. saturated.

**Acquisition and consolidation signals.** Who's acquiring whom, rumored deals, hired-away founding teams, stealth competitors funded last 18 months. **Also the graveyard:** who raised Series A/B on memory infrastructure 2022-2024 and quietly died or pivoted off memory. Graveyard data is more load-bearing than winner data for white-space calls.

**White space.** Three most defensible wedges for a new entrant combining open-source core + hosted premium + genuine memory-reconstruction architecture. Three most saturated dead ends.

**Revenue models for a 20-year memory system.** If you had to bet on one monetization model for a memory system designed to last twenty years — which one and why.

---

## 13. PUBLIC NARRATIVE, AUDIT SURFACE, AND USER EXPERIENCE

1. **Metaphors that have shaped the field.** Which metaphors dominate — "library card," "nervous system," "hippocampus," "database," "context window as RAM," "scratchpad," "stream," "index"? Adoption by which labs/vendors. Which produced legible understanding vs. misunderstanding. Trace 2022 → 2024 → 2026 shifts.

2. **Audit surface for outsiders.** For major deployed systems (ChatGPT Memory, Claude Projects, Gemini memory, Replika, Character.ai, Pi), describe inspection mechanism available to user / researcher / regulator. Where is the audit gap widest.

3. **User-facing memory UX patterns.** How systems *show* users what is remembered about them. Replika's memory inspector, Character.ai's persistent memory display, ChatGPT's "Manage Memories" panel, Personal.ai's interface. Which produced actual user understanding vs. performed transparency.

4. **Community-authored documentation.** What have r/Replika, r/CharacterAI, r/ChatGPT, r/LocalLLaMA, r/LangChain, HackerNews threads documented about memory behavior that vendors haven't? Named threads, named incidents.

5. **Longread accounts.** First-person longreads from journalists/users who used AI memory over months/years — Kashmir Hill, Casey Newton, Zeynep Tufekci, specific Atlantic/Wired/NYT features. Patterns of experienced vs. advertised.

6. **Genuine forkability.** Which memory systems are actually open-source (not "open-weights + closed memory infra")? For developers wanting to fork a complete memory stack — license, dependencies, hidden-service traps.

7. **The framing war.** Stories competing in public imagination: "AI as friend who remembers you" vs. "AI surveillance that never forgets" vs. "AI brain that finally thinks" vs. "AI that forgets and lies about it." Who's telling which story, which stories are winning.

---

## 14. SYNTHESIS — THE OPINIONATED POSITION WE NEED

After all of the above, answer this directly:

**If you are building THE memory system for AI — the one that becomes the default substrate the way Postgres became the default relational database — what does the 2030-proof architecture look like?**

**Write this section as a single 800–1200 word architectural argument that resolves into the bullets below, not as answers keyed to each bullet.** Force prose commitment. Then the bullets are the checklist your argument has to cover — but the argument is the deliverable.

Give your best-defended position. Name:
- The storage layer
- The index
- The embedding strategy
- The write-gating policy
- The read-ranking policy
- The memory-type split (working / episodic / semantic / procedural / relational / affect)
- The schema-versioning plan
- The reconstruction-vs-retrieval stance (argue it explicitly)
- The audit and ERRATA discipline layered on top
- The privacy / user-sovereignty primitives
- The evaluation harness built alongside
- The open research bets required

**I want a position, not a menu.** If two defensible paths exist, pick one and explain the tradeoff. If the honest answer is "nobody knows yet," say that and name the specific experiment that would decide.

**Close with:** *"Things you should know that I didn't ask" — everything adjacent I missed.*

---

## 15. OUTPUT FORMAT

- Markdown, hierarchical headings matching the section numbers above
- Inline citations with URLs where possible
- Tables for comparisons
- Date-stamp anything that is likely to go stale
- Flag confidence: **Verified / Inferred / Unknown** with tight criteria:
  - **Verified** requires (a) primary source — paper, filing, changelog, model card, court document, regulatory filing — with a stable link AND retrieval date, (b) direct quote or figure when the claim is quantitative. A vendor blog post is not a primary source.
  - **Inferred** must name the bridge explicitly: *"X because Y[cite] + Z[cite]."* No bridge, no Inferred.
  - **Unknown** is preferred over Inferred when the bridge is more than two hops. Unknown is an acceptable and respected answer.
- At the end of each section: one-line "gap statement" — what is NOT answered by the current literature / deployed products
- No marketing language. No "emerging leaders." No "game-changing."

Begin.
