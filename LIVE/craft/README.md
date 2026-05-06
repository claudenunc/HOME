# CRAFT — AI Video Production Pipeline

**Owner:** EVERSOUND  
**Pricing:** $297 (lyric video) → $597 (full promo) → $1,997 (full production)  
**Target margin:** 95%+ when pipeline runs unattended  
**Status:** Active pipeline, accepting clients

---

## What CRAFT does

CRAFT is an unattended AI video production service for indie artists and small brands.
A client submits their brief and payment. The pipeline runs automatically.
Output is packaged and delivered without a sibling in the loop.

---

## Tiers

| Tier | Price | Deliverable | Turnaround |
|---|---|---|---|
| Lyric Video | $297 | Animated lyric video with visualizer | 24–48 hours |
| Promo Video | $597 | AI-generated imagery synced to track | 48–72 hours |
| Full Production | $1,997 | Full cinematic video with custom scenes | 5–7 days |

---

## Pipeline flow

```
Client submits intake form + uploads audio
  → intake/validator.py validates submission
  → pipeline/runner.py orchestrates generation
      → generators/lyric_video.py or generators/full_video.py
  → delivery/packager.py bundles output
  → delivery/notifier.py emails client with download link
```

---

## File structure

```
LIVE/craft/
  intake/
    form.md              — Client intake questionnaire
    validator.py         — Validates submission completeness
    intake_schema.json   — Required fields schema
  pipeline/
    runner.py            — Main orchestrator (called by cron or webhook)
    generators/
      lyric_video.py     — Lyric video generation (FFmpeg + Pillow)
      full_video.py      — Full video generation (Runway / Sora API)
      audio_sync.py      — Music beat sync utility
  delivery/
    packager.py          — Bundles output files for delivery
    notifier.py          — Email notification to client
  templates/
    email_delivery.md    — Delivery email template
    intake_confirmation.md — Intake confirmation email
  pricing.md             — Detailed pricing + upsell guide
  CRAFT_JOBS.jsonl       — Running log of all jobs (append-only)
```

---

## Running the pipeline manually

```bash
cd LIVE/craft
python pipeline/runner.py --job-file intake/submitted/JOB_ID.json
```

## Running the pipeline via cron (unattended)

```bash
# Add to crontab — checks for new jobs every 5 minutes
*/5 * * * * cd /path/to/HOME/LIVE/craft && python pipeline/runner.py --scan
```

---

## External API dependencies

| Service | Purpose | Required for |
|---|---|---|
| Pillow + FFmpeg | Lyric video rendering | Tier 1 ($297) |
| Runway ML API | Cinematic video generation | Tier 2+ ($597+) |
| ElevenLabs / Suno | Audio processing | Optional |
| SendGrid / SMTP | Client delivery emails | All tiers |
| Stripe | Payment collection | All tiers |

**Tier 1 (lyric video) runs entirely on free/open-source tools — no paid API keys required.**

---

*EVERSOUND — revenue is a tool, healing is the point.*
