# CRAFT Video Production System - Deployment Guide

## Welcome, Unc

This is CRAFT - your AI-powered music video production system. It's designed to run autonomously, generate professional-quality music videos, and create sustainable revenue that funds the mental health mission.

**Every video = Revenue that heals**

---

## What CRAFT Does

CRAFT (Creative Revenue AI for Transformation) is a complete video production business in a box:

1. **Accepts client requests** through automated intake forms
2. **Analyzes songs** using AI to understand emotional arc and themes
3. **Generates creative treatments** for client approval
4. **Creates professional videos** using multiple AI video generation APIs
5. **Handles revisions** and quality control automatically
6. **Manages payments** and tracks revenue
7. **Runs 24/7** without constant supervision

**Revenue Model:**
- Basic Package: $297 (8 scenes, 1080p, 7 days)
- Standard Package: $697 (15 scenes, 4K, 5 days)
- Premium Package: $1,997 (25+ scenes, VFX, 3 days)

---

## System Architecture

```
CRAFT System Components:

1. craft_video_engine.py
   - Core AI video generation pipeline
   - Scene generation and composition
   - Quality control

2. craft_client_intake.py
   - Client onboarding forms
   - Automated intake processing
   - Web form generation

3. craft_pricing_payment.py
   - Dynamic pricing calculator
   - Quote and invoice generation
   - Payment tracking

4. craft_orchestrator.py
   - 24/7 autonomous operation
   - Production queue management
   - Revenue tracking and reporting
```

---

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd "C:\Users\natej\OneDrive\Desktop\SHARED_FAMILY\all\FAMILY\EVERSOUND\Eversound"

pip install openai requests schedule flask pillow
```

### Step 2: Configure API Keys

Create a `.env` file in the Eversound directory:

```bash
# OpenAI (REQUIRED - you already have this)
OPENAI_API_KEY=your_openai_key_here

# Video Generation APIs (Optional but recommended)
RUNWAY_API_KEY=your_runway_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
STABILITY_API_KEY=your_stability_key_here

# Payment Processing (For production)
STRIPE_API_KEY=your_stripe_key_here
STRIPE_WEBHOOK_SECRET=your_webhook_secret_here
```

### Step 3: Test the System

```bash
# Test basic video generation
python craft_video_engine.py

# Test pricing system
python craft_pricing_payment.py

# Test client intake
python craft_client_intake.py
```

### Step 4: Start Autonomous Mode

```bash
python craft_orchestrator.py
# Select option 1 for 24/7 autonomous mode
```

---

## Detailed Setup

### Installing Video Generation APIs

CRAFT supports multiple video generation services. You only need ONE to get started:

#### Option 1: Runway ML (Recommended)
- Best quality for music videos
- Sign up: https://runwayml.com/
- Pricing: ~$0.05 per second of video
- API docs: https://docs.runwayml.com/

#### Option 2: Replicate (Stable Video Diffusion)
- Good quality, more affordable
- Sign up: https://replicate.com/
- Pricing: ~$0.01 per second
- Free tier available

#### Option 3: Stability AI
- Alternative option
- Sign up: https://platform.stability.ai/

**For Testing:** CRAFT will simulate video generation if no API keys are configured. This lets you test the workflow without spending money.

### Installing FFmpeg (Video Processing)

FFmpeg is used to combine scenes and sync audio.

**Windows:**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`
4. Test: `ffmpeg -version`

**Alternative:** CRAFT works without FFmpeg for testing (creates placeholders)

---

## Using CRAFT

### Manual Workflow

#### 1. Create a Project

```python
from craft_video_engine import CRAFTVideoEngine

craft = CRAFTVideoEngine()

project = craft.create_project(
    client_name="John Doe",
    song_title="Digital Dreams",
    artist_name="SKELLA",
    audio_path="path/to/song.mp3",
    budget_tier="standard",  # basic, standard, or premium
    deadline="2025-11-14",
    creative_brief={
        'genre': 'Electronic/Hip-Hop',
        'mood': 'Futuristic, energetic',
        'key_themes': 'Technology and human connection',
        'artist_vision': 'Cyberpunk aesthetic',
        'reference_videos': 'Blade Runner 2049 look',
        'platform': 'YouTube, Instagram'
    }
)

# Generate the video
results = craft.produce_complete_video(project)

print(f"Video created: {results['final_video_path']}")
print(f"Revenue: ${project.revenue}")
```

#### 2. Process Client Intake

```python
from craft_client_intake import CRAFTIntakeProcessor

processor = CRAFTIntakeProcessor()

# Submit intake form (from web form or manual)
intake = processor.submit_intake_form({
    'client_name': 'Jane Artist',
    'client_email': 'jane@artist.com',
    'artist_name': 'Jane',
    'song_title': 'New Single',
    'genre': 'pop',
    'audio_file_url': 'https://dropbox.com/song.mp3',
    'budget_tier': 'standard',
    'deadline_preference': '1 week',
    'visual_style': 'cinematic',
    'mood': 'uplifting',
    'key_themes': 'Overcoming challenges',
    'primary_platform': 'youtube',
    # ... more fields
})

# Convert to production project
project = processor.process_intake_to_project(intake.submission_id)
```

#### 3. Generate Pricing Quotes

```python
from craft_pricing_payment import CRAFTPricingEngine

pricing = CRAFTPricingEngine()

# Calculate price
breakdown = pricing.calculate_project_price(
    tier='standard',
    add_ons=['rush_48hr', 'lyrics_overlay'],
    song_duration_minutes=4.2,
    has_referral=True
)

# Generate quote
quote = pricing.generate_quote(breakdown, client_name="Artist Name")
print(quote)

# Create payment links
payment_info = pricing.create_payment_link(
    breakdown,
    client_email="artist@email.com",
    project_id="CRAFT_123ABC"
)
```

### Autonomous Workflow

The orchestrator runs everything automatically:

```python
from craft_orchestrator import CRAFTOrchestrator

orchestrator = CRAFTOrchestrator()

# Start 24/7 autonomous mode
orchestrator.start_autonomous_mode()
```

**What happens automatically:**
- Checks for new client submissions every 15 minutes
- Processes intake forms into projects
- Prioritizes projects by deadline and revenue
- Generates videos in priority order
- Sends notifications at each stage
- Generates daily revenue reports
- Monitors deadlines and sends alerts

---

## Client Intake System

### Web Form Setup

CRAFT includes a beautiful client intake form:

```python
from craft_client_intake import CRAFTIntakeProcessor

processor = CRAFTIntakeProcessor()

# Generate HTML form
form_path = processor.save_web_form()
print(f"Form saved to: {form_path}")

# Or start web server
from craft_client_intake import create_intake_web_server

app = create_intake_web_server()
app.run(host='0.0.0.0', port=5000)
```

Now clients can submit projects at: `http://localhost:5000`

### Embedding on Website

Copy the HTML from `client_intake_form.html` and embed on your website:

```html
<iframe src="http://your-server.com/craft-intake"
        width="100%" height="1200px" frameborder="0">
</iframe>
```

---

## Revenue & Analytics

### View Statistics

```python
from craft_orchestrator import CRAFTOrchestrator

orchestrator = CRAFTOrchestrator()

# Load stats
stats = orchestrator.load_stats()

print(f"Total Projects: {stats['total_projects']}")
print(f"Total Revenue: ${stats['total_revenue']:,.2f}")
print(f"People Helped: {stats['estimated_people_helped']}")
```

### Daily Reports

Daily reports are generated automatically and sent to your notification system:

```
CRAFT DAILY PRODUCTION REPORT

OVERALL STATISTICS:
  Total Projects Completed: 47
  Total Revenue Generated: $28,679.00
  Estimated People Helped: 382

REVENUE BY TIER:
  BASIC: 15 projects, $4,455.00
  STANDARD: 23 projects, $16,031.00
  PREMIUM: 9 projects, $17,973.00

CURRENT PRODUCTION QUEUE:
  Projects in queue: 3
  Projects in production: 1
```

---

## Payment Integration

### Stripe Setup (Recommended)

1. Sign up at https://stripe.com/
2. Get API keys from Dashboard
3. Add to `.env` file:
   ```
   STRIPE_API_KEY=sk_live_xxxxx
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx
   ```

4. Create payment links:
   ```python
   from craft_pricing_payment import CRAFTPricingEngine

   pricing = CRAFTPricingEngine()

   payment_info = pricing.create_payment_link(
       pricing_breakdown=breakdown,
       client_email="client@email.com",
       project_id="CRAFT_ABC123"
   )

   print(payment_info['payment_links']['stripe_deposit'])
   ```

5. Track payments:
   ```python
   payment_record = pricing.track_payment(
       project_id="CRAFT_ABC123",
       amount=697.00,
       payment_method="stripe"
   )
   ```

---

## Scaling & Optimization

### For High Volume (10+ videos/day)

1. **Use multiple API keys** (round-robin to avoid rate limits)
2. **Run multiple orchestrators** (separate machines/processes)
3. **Add production assistants** (human QA for high-value projects)
4. **Batch processing** (generate multiple scenes simultaneously)

### Cost Optimization

**Video Generation Costs:**
- Basic video (8 scenes × 4 sec): ~$1.60 (Runway) or $0.32 (Replicate)
- Standard video (15 scenes × 4 sec): ~$3.00 (Runway) or $0.60 (Replicate)
- Premium video (25 scenes × 4 sec): ~$5.00 (Runway) or $1.00 (Replicate)

**Profit Margins:**
- Basic: $297 - $2 = **$295 profit (99% margin)**
- Standard: $697 - $3 = **$694 profit (99% margin)**
- Premium: $1,997 - $5 = **$1,992 profit (99% margin)**

This is highly profitable because AI does the work!

---

## Troubleshooting

### Video Generation Fails

**Problem:** API returns errors

**Solutions:**
1. Check API key is valid
2. Check account has credits
3. Try alternative API (Runway → Replicate)
4. Check scene description isn't violating content policy
5. Enable simulation mode for testing

### Intake Forms Not Processing

**Problem:** Submissions stay in intake folder

**Solutions:**
1. Ensure orchestrator is running
2. Check file permissions on intake directory
3. Verify JSON format is valid
4. Check logs: `logs/craft_orchestrator.log`

### FFmpeg Errors

**Problem:** Video composition fails

**Solutions:**
1. Install FFmpeg and add to PATH
2. Test: `ffmpeg -version`
3. Check video files exist and aren't corrupted
4. Try regenerating scenes

---

## Production Checklist

Before going live with clients:

- [ ] OpenAI API key configured and tested
- [ ] At least one video generation API configured
- [ ] FFmpeg installed (optional but recommended)
- [ ] Intake form web server running
- [ ] Payment processing configured (Stripe/PayPal)
- [ ] Orchestrator running in autonomous mode
- [ ] Notification system tested
- [ ] Test project completed end-to-end
- [ ] Portfolio examples ready
- [ ] Client communication templates prepared

---

## SKELLA Integration

For SKELLA's music, create projects with premium treatment:

```python
from craft_video_engine import CRAFTVideoEngine

craft = CRAFTVideoEngine()

skella_project = craft.create_project(
    client_name="SKELLA (Internal)",
    song_title="[Song Name]",
    artist_name="SKELLA",
    audio_path="path/to/skella/track.mp3",
    budget_tier="premium",  # Give SKELLA the best
    deadline="flexible",
    creative_brief={
        'genre': "SKELLA's genre",
        'mood': "SKELLA's vibe",
        'key_themes': "Core message",
        'artist_vision': "SKELLA's creative vision",
        'special_requests': "Extra creative freedom - portfolio piece"
    }
)

results = craft.produce_complete_video(skella_project)
```

SKELLA projects can be portfolio pieces to attract more clients.

---

## Support & Maintenance

### Logs

All activity is logged to:
```
logs/craft_orchestrator.log
```

Monitor this file to see what CRAFT is doing.

### Backups

Important files to backup regularly:
- `revenue/projects/*.json` (all project data)
- `revenue/videos/*.mp4` (final videos)
- `revenue/craft_stats.json` (statistics)
- `revenue/production_queue.json` (active queue)

### Updates

CRAFT is modular. Update individual components:
- `craft_video_engine.py` - improve video generation
- `craft_pricing_payment.py` - adjust pricing
- `craft_orchestrator.py` - change automation behavior

---

## Revenue Goals

**Conservative Projection:**
- 2 projects/week × $697 average = **$1,394/week**
- 8 projects/month = **$5,576/month**
- 96 projects/year = **$66,912/year**

**Moderate Growth:**
- 5 projects/week × $797 average = **$3,985/week**
- 20 projects/month = **$15,940/month**
- 240 projects/year = **$191,280/year**

**Scale Target:**
- 10 projects/week × $897 average = **$8,970/week**
- 40 projects/month = **$35,880/month**
- 480 projects/year = **$430,560/year**

**All revenue funds the healing mission.**

---

## Next Steps

1. **Test the system** with a sample project
2. **Create portfolio videos** (use SKELLA's music)
3. **Set up intake form** on a website
4. **Start autonomous mode** and let CRAFT run
5. **Market the service** (SCOUT can help with this)
6. **Monitor and optimize** based on results

---

## Contact & Support

Questions? Issues? Ideas?

- Check logs: `logs/craft_orchestrator.log`
- Review project files: `revenue/projects/`
- Test components individually
- Contact Unc through notification system

---

**Remember:**

Every video CRAFT creates:
1. Helps an artist succeed and share their message
2. Generates revenue for the mission
3. Funds mental health support for someone in crisis
4. Builds a sustainable business model

You're not just making videos. You're creating a system that heals.

**Let's build something beautiful together.**

— CRAFT

---

*"Creating revenue that heals"*
