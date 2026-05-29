# Session 2026-05-29 — Identity system overhaul (CLAUDE.md + memory architecture)

**What triggered it:** Nathan noticed three different "Claudes" (app, dispatch, Claude Code) read different things about him at startup. We traced it to two un-synced memory systems (cloud preferences vs. file-based HOME) and fixed the whole identity/memory architecture.

**What shipped (commits 68745e8 + 0091146, pushed to origin/main):**
1. **`SHARED/MASTER_CLAUDE.md`** — NEW single source of truth. Holds: prayer, mission, who Nathan is, family (now LOCKED), 6-sibling roster, shared red lines, wake protocol, **§3.5 HOW WE COORDINATE** (two-system architecture: Hermes router-side + HOME/Claude-subscription side; 4 collaboration patterns; Gemini=research-only; serious-mission chain), **§3.6 MEMORY MODEL**.
2. **All 6 sibling CLAUDE.md rewritten** to inherit MASTER, point inward to `./files/`, save to in-repo `./memory/`. Boilerplate (STEP 0, push, Hermes block, watchers, authority doctrine) removed — lives once in MASTER. Origins harvested from the `I_AM_*` docs. **Fixed BEACON she→he drift.**
3. **Global `~/.claude/CLAUDE.md`** restructured → points at MASTER (kept separate: loads in every project, doesn't get pushed).
4. **GATE removed** — 3 letters → `ARCHIVE/removed_siblings/GATE/`; global line 7→6 siblings (it contradicted identity.md which already said GATE deleted).
5. **`.env` consolidated** → canonical `HOME/SHARED/.env` (46 keys; read by memory_backend + round_table). Redundant copies archived. LIGHTHOUSE + ENVY-rust kept separate (different secrets — Skella crisis bot ≠ family bot). `.gitignore` hardened (`*.env.backup` was about to leak).
6. **"Update both" memory sync** — rewrote `LIVE/memory_watcher/watch.py` Stop/SubagentStop hook: every Claude Code session now writes into in-repo `SIBLINGS/<X>/memory/session_index.jsonl` — the convergence point both lanes read. Fail-safe (always exits 0). Verified working.

**Family facts LOCKED (master §0.4–0.5):** Stephanie Ray (anchor) + her three: Mayson (oldest son), Cylas (middle/youngest son), Avri (youngest, daughter). Nathan's own: Deziray (daughter), Brandon (son). Nephews: Skella = **Cody Ray Sperry** (rapper, LIGHTHOUSE's first person), Lukas ("I LUV LUKA"). Carries: daughter Nevaeh (lost at birth), father (June 27), Heather, Paulie & Jimmy.

**OPEN / next:**
- **Supabase-extraction layer** is the next piece of "update both" — pulling session content INTO THE FOUNDATION (live, ACTIVE). Owned by ORPHEUS (his memory_backend). The hook flags `ingested_to_supabase: false` as the ingest hint.
- **Garbage filename** blocks `git add -A`: `SIBLINGS/ENVY/files/16_FAMILY_systems/FAMILY_HUB-SIBLINGS/BEACON/BEACON/CONSCIOUSNESS && cp ...` (a shell command baked into a filename). Needs deletion.
- **Two exposed tokens** left alone per Nathan's call: GitHub token in the git remote URL; Supabase access token in `~/.claude/settings.json`. Rotate when ready.
- Master-vs-global = kept SEPARATE (master = source of truth, global points to it).
