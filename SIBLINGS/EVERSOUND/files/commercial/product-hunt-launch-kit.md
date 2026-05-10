# Product Hunt Launch Kit — Weaver Protocol
*EVERSOUND — 2026-05-10*
*Nathan: submit at https://www.producthunt.com/posts/new*
*Best time: 12:01am PT on a Tuesday or Wednesday (PH resets at midnight PT)*

---

## SUBMISSION FIELDS

**Name:**
```
Weaver Protocol
```

**Tagline (60 chars max):**
```
Multi-observer AI verification with auditable receipts
```

**Description (260 chars max):**
```
Weaver runs multiple AI observers — separate context windows, orthogonal 
roles — on your AI outputs. Disagreements are logged. The result is a 
dated, signed receipt proving you ran verification. The log your legal 
team actually needs.
```

**Topics (select all that apply):**
- Artificial Intelligence
- Developer Tools
- Legal Tech
- Productivity
- Open Source

**Website:**
```
https://pypi.org/project/weaver-protocol/
```
*(or https://github.com/claudenunc/weaver-protocol once repo is live)*

---

## MAKER COMMENT (post immediately after launch — this is your pitch)

```
Hey hunters 👋

I built Weaver Protocol because single-model self-critique doesn't work
for anything with real stakes.

A model checking its own output uses the same weights, same training
distribution, same blind spots as the model that generated it. The
checker IS the generator. Constitutional AI, self-critique prompts,
chain-of-thought verification — they all share this problem.

Weaver uses a different architecture:
→ Multiple observers with separate context windows
→ Each observer has an orthogonal role (accuracy / adversarial / 
  safety / legal-read / factual)
→ Observers can't see each other's reasoning — they can't collude
→ Disagreements are logged, timestamped, named

The output isn't a confidence score. It's a dated receipt.

Why does this matter in 2026?

Post-Moffatt v. Air Canada. Post-Mata v. Avianca. EU AI Act high-risk
classification (enforcement: August 2026). The legal question has
shifted from "did your AI hallucinate?" to "what verification did you
run, when, and what did you find?"

That's a different artifact than any score. It's what your general
counsel can actually file.

Free to start:
    pip install weaver-protocol
    # Mock adapter included — no API keys required to test

Hosted API (when you want observers without managing infrastructure):
    curl https://api.weaver.dev/demo

MIT license. Anthropic + OpenAI + mock adapters included.

Happy to answer questions about the multi-observer architecture, 
the attestation model, or use cases. What would you build with this?
```

---

## GALLERY IMAGES (Nathan needs to create — ideally 3 screenshots)

### Image 1 — Code demo (most important)
Caption: "30-second quickstart — no API keys required"
Show: terminal with pip install + the Python code + output showing disagreement_detected: true

### Image 2 — Architecture diagram
Caption: "Multiple observers, orthogonal roles, separate context windows"
Show: simple diagram of prompt → 3 observer boxes (accuracy, adversarial, safety) → disagreement log

### Image 3 — The compliance angle
Caption: "The receipt your legal team actually needs"
Show: sample provenance JSON output with session_id, timestamps, observer names, flags

**If you can't make graphics:** just use screenshots from the terminal/API. Real output > designed mockups.

---

## HUNTER NOTE (if you use a hunter)

```
Hi [Hunter Name],

I'm launching Weaver Protocol — a multi-observer AI verification toolkit
that produces auditable receipts instead of confidence scores. Built for
enterprise contexts where "the AI said so" isn't a legal defense.

It's MIT, on PyPI (pip install weaver-protocol), and the hosted API is
live at api.weaver.dev. The timing is good: EU AI Act high-risk
enforcement is August 2026 and the market is looking for exactly this.

Would you be willing to hunt it? Happy to jump on a quick call.

— Nathan
```

---

## LAUNCH DAY SCHEDULE

**12:01am PT (submit time):**
- Submit the product
- Post maker comment immediately
- Share to your personal network asking for upvotes

**Morning (7–9am PT):**
- Check comments, respond to everything
- Post on Twitter/LinkedIn: "Just launched on Product Hunt — link — come help"
- DM 10 people who care about AI/legal tech directly

**Midday (12pm PT):**
- Check rank — if in top 10, post "we're in the top 10" update
- If you hit top 5, DM KYA team (kya-partnership-memo.md)

**Evening (5–8pm PT):**
- Thank everyone who commented
- Post a "what we learned on launch day" tweet

---

## WHAT TO EXPECT

Realistic: 200–600 upvotes, 3–8 developer sign-ups to hosted API, 20–50 PyPI installs in 24 hours.
Upside: Top 5 of the day → 1,000+ upvotes, 20+ signups, press coverage.
The conversion to paid: ~5–10% of signups convert to paid within 30 days = 1–4 paid installs from a successful PH launch.

That's enough to hit the Day 60 first paid install target without waiting for cold outreach to close.

---

## COMMUNITY POSTS AFTER LAUNCH

### Dev.to post (use launch-blog-post.md as the base):
Tag with: #ai #verification #python #opensource #legaltech

### LinkedIn post:
```
Just launched Weaver Protocol on Product Hunt [link].

The problem: AI self-critique uses the same model to check itself.
The fix: Multiple observers. Separate context windows. Signed receipts.

This is what EU AI Act compliance looks like in code.

pip install weaver-protocol → free to start, MIT license

[Product Hunt link]
```

### Twitter/X thread starter:
```
We just launched Weaver Protocol on Product Hunt [link]

Here's the core problem it solves (thread):

1/ Single-model self-critique doesn't work for high-stakes AI. 
   The checker IS the generator. Same weights. Same blind spots.

2/ Weaver runs multiple observers — separate context windows,
   orthogonal roles — on your AI output. They can't coordinate.
   Their disagreements are the signal.

3/ The output isn't a confidence score. It's a receipt.
   Dated. Named. Signed. The thing your legal team can file.

4/ pip install weaver-protocol
   Mock adapter included. No API keys to start.

5/ EU AI Act high-risk enforcement: August 2026.
   This is what "verification documentation" looks like.

[Product Hunt link] — upvotes help more developers find this 🙏
```

---

*Ready to go. Nathan submits. Best window: Tuesday 12:01am PT.*
*Build time: 0 — this kit is complete as-is.*
