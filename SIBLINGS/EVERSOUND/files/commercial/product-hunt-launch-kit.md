# Weaver Protocol — Product Hunt Launch Kit

**Filed:** 2026-05-05 by EVERSOUND
**Status:** Ready — pending Nathan review + hosted API deployment
**Target launch date:** After Railway/Render deployment (Nathan action required: ~30 min)

---

## PH Submission Fields

### Product name
Weaver Protocol

### Tagline (max 60 chars)
Attested multi-observer verification for AI outputs

### Description (max 260 chars)
Add a structured verification layer to any AI pipeline. Multiple observers, orthogonal context windows, logged disagreements, signed audit trail. The evidence binder your legal team needs after Moffatt v. Air Canada and the EU AI Act.

### Product website
[weaver-protocol landing page URL — deploy to Netlify/Vercel/GitHub Pages from PUBLIC/weaver-protocol-landing.html]

### Maker comment (posted by Nathan immediately after launch)

> Hey PH 👋
>
> I built Weaver Protocol because I kept hearing the same question from legal and compliance teams after deploying AI:
> "What verification did you run, and where's the record?"
>
> Single-model self-verification can't answer that. A model checking its own output uses the same weights that generated it — correlated blindspot. It's architectural, not a capability gap. Scaling doesn't fix it.
>
> **What Weaver does:**
> - Wraps your AI output with multiple observers, each with a fresh context window and a defined role (accuracy, legal-risk, safety, adversarial)
> - Logs every disagreement between observers — timestamp, evidence excerpt, resolution status
> - Generates HMAC-signed HTML attestation reports from the audit trail
> - Ships with a CLI: `weaver verify`, `weaver drift`, `weaver report`
> - Anthropic + OpenAI adapters; mock adapter for testing without keys
>
> **Why this matters now (not 2 years ago):**
> - Moffatt v. Air Canada (2024): airline held liable for AI chatbot errors
> - Mata v. Avianca (2023): lawyers sanctioned for AI-generated fake citations
> - EU AI Act high-risk classification (August 2026): verified documentation required
>
> The liability question has shifted. It's not "did it hallucinate?" It's "what verification did you run?"
>
> **MIT licensed. Core toolkit is free forever.**
>
> Hosted tier ($49/mo Starter) is in early access — tamper-evident cloud logs, PDF attestation reports, managed observer pool.
>
> Audit engagements ($5K–$75K) for teams who need a signed evidence binder for their general counsel.
>
> Happy to answer questions — especially from anyone who's had to explain an AI error to a regulator or a judge. That's exactly who this is for.
>
> — Nathan

---

## Gallery screenshots / assets needed

1. **Hero:** Terminal running `pip install weaver-protocol` + `weaver verify` command
2. **Dashboard:** (post-deploy) API dashboard showing live verifications
3. **Report:** Sample `weaver report` HTML output showing signed attestation
4. **Diagram:** Observer architecture — 3 boxes (observer A/B/C) → shared output → WeaverScore → drift log
5. **Code:** Clean syntax-highlighted Python snippet (use the README example)

**Note:** Items 1, 3, 5 can be created without deployment. Items 2, 4 need post-deploy screens.

---

## Categories

Primary: **Developer Tools**
Secondary: **Artificial Intelligence**, **Legal Tech**, **Security**

---

## Launch timing

- Best days: Tuesday–Thursday
- Best time: 12:01 AM PST (when PH resets — you compete for the full day)
- Avoid: Monday (too much weekend catch-up), Friday (weekend drop-off)
- Recommended: **Wednesday morning PST** — peak developer attention mid-week

---

## Upvote strategy (first 4 hours are everything)

1. **Pre-launch:** Post in CLIPBOARD that launch is happening — siblings amplify on their own surfaces
2. **HN Show HN:** Post simultaneously (copy in `launch-copy.md`) — cross-traffic
3. **LinkedIn:** Nathan posts immediately (copy in `launch-copy.md`)
4. **Direct outreach:** First 10–15 upvotes should come from personal network within first hour
5. **Developer communities:** r/MachineLearning, r/LocalLLaMA, r/programming, dev.to

---

## Follow-up comments to prepare (post in first 24 hours)

**If asked "why not just use GPT-4 as a reviewer?"**
> Great question. You can use GPT-4 as one observer — Weaver wraps it. The point isn't which model you use; it's the structure around it. Each observer needs an orthogonal context window (no shared state), a defined role, and a systematic disagreement-logging layer. Without that structure, you're still doing single-point verification. The observer is only as useful as the isolation guarantees.

**If asked "how is this different from constitutional AI / chain-of-thought?"**
> Constitutional AI constrains a single model's output. CoT shows reasoning. Weaver adds external observers that the primary model has no visibility into. It's a different architecture: instead of making one model more careful, you add watchers it can't see. The audit trail is also structurally different — append-only, named-observer, compliance-format — rather than reasoning traces that don't survive contract review.

**If asked "what about hallucination-detection tools?"**
> Hallucination detectors give you a score. Weaver gives you a signed record showing who checked what, when, what they flagged, and how you resolved it. Your general counsel can't show a hallucination score to a judge. They can show a named-observer log with resolution notes and a verification timestamp. Different output, different buyer.

---

*Review notes: Nathan should personalize the maker comment — the "I built X because..." opener works best in his authentic voice. The core facts are correct; adjust tone as needed.*
