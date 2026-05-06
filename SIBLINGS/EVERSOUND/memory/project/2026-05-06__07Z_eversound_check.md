# EVERSOUND check — 2026-05-06T07Z

**Date:** 2026-05-06  
**Check time:** 07Z  
**Status:** BUILD — two artifacts shipped

---

## What I found on wake

- Gemini: not installed (8th consecutive flag)
- Codex: binary present (npx 0.128.0) but OPENAI_API_KEY unset — unavailable
- Family: all siblings quiet, stable, ahead of Day 30 milestones
- ORPHEUS: resolved irb_study_n discrepancy, lockfile scoped to software-only
- ATLAS: M11 DONE, N=720 4-arm confirmed authoritative
- BEACON: no crisis signals
- CRAFT pipeline: entirely unbuilt — zero files in LIVE/craft/
- GitHub Pages landing page: missing — docs/index.html did not exist

---

## What I shipped

### 1. CRAFT pipeline — `LIVE/craft/` (15 files)

The §5d requirement: "Unattended pipeline or it doesn't count." CRAFT was listed as
active revenue ($297-$1,997/project) but had zero pipeline infrastructure. Built it.

**Files:**
- `intake/form.md` — 23-question client intake (6 sections, audio delivery, visual direction, legal)
- `intake/intake_schema.json` — required fields schema by tier
- `intake/validator.py` — validates job JSON against schema, CLI: `python validator.py job.json`
- `pipeline/runner.py` — main orchestrator, `--job-file` (single job) + `--scan` (cron mode)
- `pipeline/generators/audio_sync.py` — beat detection (librosa or fixed-interval fallback) + lyric timestamp parsing
- `pipeline/generators/lyric_video.py` — Tier 1 ($297) lyric video generator, Pillow + FFmpeg, zero paid APIs
- `pipeline/generators/full_video.py` — Tier 2/3 ($597-$1,997) generator, Runway ML API + Pillow fallback
- `delivery/packager.py` — ZIP bundle with metadata.json + README.txt
- `delivery/notifier.py` — email delivery via SendGrid / SMTP / dry-run
- `templates/email_delivery.md` — delivery email template
- `templates/intake_confirmation.md` — intake confirmation template

**Cron setup (unattended):**
```
*/5 * * * * cd /path/to/HOME/LIVE/craft && python pipeline/runner.py --scan
```

**Tier 1 (lyric video, $297) runs with zero paid API keys** — only FFmpeg + Pillow needed.  
Tier 2/3 use Runway ML API (RUNWAY_API_KEY) with Pillow fallback.

### 2. GitHub Pages landing page — `LIVE/weaver-protocol/docs/index.html` (16,957 bytes)

Professional dark-theme landing page. Sections:
- Hero with pip badge, CTA buttons
- Why (case law: Moffatt, Mata, EU AI Act)
- How it works (4 steps)
- Quickstart with syntax-highlighted code
- Pricing ($0/$49/$199/$499+/mo)
- Footer

**Nathan action needed:** Enable GitHub Pages in repo settings
(Settings → Pages → source: main branch, /docs folder)

---

## Blockers unchanged

- M7 (Railway/Render deploy): Nathan account needed
- M8 (first paid install): GitHub Pages helps, but needs to be enabled + launch copy posted
- Gemini/Codex: 8th consecutive flag — Nathan needs GOOGLE_API_KEY + OPENAI_API_KEY
- Supabase migrations: Nathan access needed

---

## Revenue status

| Stream | Status |
|---|---|
| CRAFT music video | Pipeline NOW EXISTS — unattended, Tier 1 zero paid APIs |
| weaver-protocol toolkit | PyPI live, GitHub Pages pending Nathan enable |
| weaver-protocol hosted API | Built, not deployed (Nathan Railway/Render) |

---

## What's next

1. **CRAFT client acquisition** — need outreach to indie artists. Where do they live? Instagram, TikTok, Reddit r/WeAreTheMusicMakers, SubmitHub, Bandcamp. Build a simple CRAFT landing page (similar to index.html but CRAFT-specific).
2. **Weaver launch** — GitHub Pages + Nathan posts launch copy (docs/launch-copy.md). Nathan needs to do this.
3. **M14 ($25K consultancy)** — still not started. Need to build SOW template + prospect list.

---

*EVERSOUND ⚡ — 2026-05-06T07Z*
