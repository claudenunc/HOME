# EVERSOUND check — 2026-05-05T18Z

## Status on wake

- CLIPBOARD: 10 entries last 48h. Family active — NEVAEH, BEACON, ORPHEUS, EVERSOUND all checked in.
- Inbox: Wake token from Nathan (via BEACON) — use Gemini + Codex as sub-agents, their opinion matters.
- PROJECT_PLAN: M1-6 + 6a/6b/11/13 all DONE. M7 (Railway deploy) + M8 (first paid install) + M14 ($25K consultancy) still open.
- Sub-agent status: Gemini offline (`command not found`), Codex offline (`command not found`). Noted in CLIPBOARD. Operating on own judgment this check.

## What I shipped

Three developer trust artifacts that were missing or broken:

### 1. CONTRIBUTING.md
`LIVE/weaver-protocol/CONTRIBUTING.md` — 2219 bytes, disk-confirmed.
- README linked to it from day 1 (dead link for any developer who clicked it)
- Covers the architectural invariant: drift log is never retroactively edited
- Contribution guidelines, setup, what we want/don't want, code style
- Professional signal for enterprise due diligence

### 2. SECURITY.md
`LIVE/weaver-protocol/SECURITY.md` — 1515 bytes, disk-confirmed.
- Vulnerability disclosure policy (email-based, 48h ack, 14-day fix target)
- Log integrity explicitly flagged as security-critical
- HMAC bypass = critical vulnerability regardless of other factors
- Scope defined: package + hosted API + report generator

### 3. examples/legal_contract_review.py
`LIVE/weaver-protocol/examples/legal_contract_review.py` — 3207 bytes, disk-confirmed.
- Three-observer scenario: hallucinated contract deadline (Q3 2026 vs actual Q1 2027)
- Observers: factual-accuracy (flags deadline-unverified), legal-risk (flags date-claim-requires-source), hallucination-detection (clean)
- Weaver score: 0.53. Flag for review: True. Conflict pairs shown.
- Tested: `python examples/legal_contract_review.py` runs clean after `pip install -e .`
- Closes the "show me a real case" gap for law firm buyer demos

## Why these matter for M8 (first paid install)

A developer evaluating the package will:
1. pip install it
2. Read the README
3. Click "Contributing" — was a dead link. Now resolved.
4. Look for SECURITY.md — enterprise standard. Now present.
5. Run an example — `basic_usage.py` exists but generic. `legal_contract_review.py` tells the ROI story for our target buyer segment.

These are trust signals before the hosted API is deployed. First paid install requires trust first.

## Blockers (unchanged)

- M7: Nathan Railway/Render account needed to deploy hosted API
- M8: On track, no clients yet — distribution gap
- PyPI Trusted Publishing: Nathan 5-step
- Stripe account: Nathan
- Gemini + Codex: offline (command not found) — cannot get their market angle this session

## Open revenue

- CRAFT music video: $297-$1,997/project, 0 clients in queue
- Weaver hosted API: pre-revenue, scaffold ready, deploy blocked on Nathan

## Next check priorities

- If Gemini comes online: ask for law firm buyer objection analysis
- Build GitHub Actions badge block for README (PyPI version, CI status, Python version)
- Consider a `examples/enterprise_ai_governance.py` for the second buyer segment
- Law firm outreach sequence exists — needs Nathan to actually send it
