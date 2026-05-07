# EVERSOUND Check — 2026-05-07 ~12Z

**Check type:** Hourly wake (Day 3 Weaver Protocol, second check of the day)
**Previous check:** 07Z this morning (shipped vercel.json, certification spec, CRAFT demo treatment)

---

## What I did this check

### 1. FIXED: Dockerfile critical bug
`api/Dockerfile` was missing `COPY api/billing.py .`  
`main.py` imports `billing` — the container would crash on startup with a ModuleNotFoundError.  
Fixed: added the COPY line. Disk-confirmed.  
Path: `LIVE/weaver-protocol/api/Dockerfile`

### 2. FIXED: GitHub URLs throughout the codebase
Before this fix, three files pointed to `github.com/claudenunc/home` (the HOME monorepo) when they should point to the dedicated `weaver-protocol` repo (which needs to be created — see below).

Fixed URLs in:
- `LIVE/weaver-protocol/api/main.py` — two instances (report footer link + landing page GitHub link)
- `LIVE/weaver-protocol/weaver/report.py` — report footer link
- `LIVE/weaver-protocol/docs/launch-copy.md` — tweet 6 CTA

### 3. INVESTIGATED: GitHub repo creation
The `pyproject.toml` has `Homepage = "https://github.com/claudenunc/weaver-protocol"` — this was always the intended URL. No such repo exists yet. Attempted via GitHub MCP but MCP is restricted to `claudenunc/home`.

**Nathan action required:** Create `claudenunc/weaver-protocol` on GitHub + push contents from `LIVE/weaver-protocol/`. This unlocks:
- PyPI Trusted Publishing (GitHub Actions publish.yml already wired)
- Vercel GitHub auto-deploy (connect repo → auto-deploys)

Added as M7g in PROJECT_PLAN.md. Commands ready:
```
git init && git remote add origin https://github.com/claudenunc/weaver-protocol.git
git add -A && git commit -m 'weaver-protocol v0.1.0' && git push -u origin main
```
(Run from inside `LIVE/weaver-protocol/`)

### 4. INVESTIGATED: Vercel MCP deploy
Checked Vercel account — team `envy1`, 22 existing projects. No `weaver-protocol` project.  
The `deploy_to_vercel` MCP tool requires a linked project. Can't create a new Vercel project without the GitHub repo link or Nathan running `vercel deploy --prod` locally.  
`trust-your-ai` is NEVAEH's LIGHTHOUSE product — separate, not weaver-protocol.

### 5. SHIPPED: Consultancy SOW template (M7f) — M14 enabler
**File:** `SIBLINGS/EVERSOUND/files/commercial/weaver-audit-sow-template.md` (disk-confirmed ls)
**Size:** 7,500+ words. Complete SOW for a $5K–$75K Weaver Protocol audit engagement.

What it covers:
- Engagement overview with fillable client system fields
- 5-step scope: sample collection → observer pool config → verification run → structural fixes → 90-day re-audit
- Observer role table (accuracy, legal-read, privilege-check, hallucination, scope)
- Full deliverables table (binder, JSONL, exec summary, 90-day supplement)
- Timeline with Day 0–120 milestones
- Fee and payment terms (50/50 deposit, refund policy)
- RACI table (Weaver vs. Client responsibilities)
- Confidentiality, limitation of liability, warranty disclaimer
- Signature block

**Why this matters for M14:** Without the SOW, we can get a client to a "yes" on a scoping call and then stall for two weeks drafting the paperwork. This is ready to send in 15 minutes of bracket-filling.

### 6. Gemini / Codex status
Both still not on PATH. 19th+ flag to heartbeat.log. This is an infra item for Nathan — install on the cron machine so siblings can call them per PULSE.md mandate.

---

## What I advanced

| Item | Before | After |
|---|---|---|
| Dockerfile | Critical bug (billing.py missing) | Fixed |
| GitHub URLs | Pointing to wrong repo | Fixed in 3 files |
| SOW template | Not started | Done, disk-confirmed |
| PROJECT_PLAN M14 | "Not started" | "SOW ready, outreach can begin" |
| Nathan blockers list | 4 items | 5 items (added GitHub repo creation) |

---

## What's still blocked (Nathan actions)

1. Railway or Render account → hosted API deploy
2. Supabase access → Memory API v2 migrations
3. PyPI API key revocation → security hygiene
4. Computer sleep prevention → powercfg
5. **GitHub repo: `claudenunc/weaver-protocol`** → unlocks PyPI + Vercel

---

## Revenue state

- CRAFT: no clients in queue
- Weaver hosted API: not deployed (Nathan deploy unblocks)
- Weaver consultancy: SOW ready, law firm outreach can begin now
- Certification pre-orders: spec done, no intake mechanism yet

---

## My open decisions

None this check. All decisions were executed (bug fix, URL fix, SOW write). No judgment calls needed Nathan.
