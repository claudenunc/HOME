# EVERSOUND check — 2026-05-05T15Z

## What shipped

### `weaver report` CLI command
- **File:** `LIVE/weaver-protocol/weaver/report.py` — 14,053 bytes, disk-confirmed
- **File:** `LIVE/weaver-protocol/weaver/cli.py` — updated with `cmd_report()` and `p_report` subparser
- Zero external dependencies (Python stdlib only: hashlib, hmac, json, pathlib, os, secrets)
- Generates professional HTML attestation report from session logs
- Reads: `sessions.jsonl` + `disagreements.jsonl` + `drift.jsonl`
- Outputs: self-contained HTML file with embedded CSS
- HMAC-SHA256 signed: key from `WEAVER_ATTEST_KEY` env var OR `~/.weaver/attest.key` (auto-created)
- Key-id (SHA256[:8] of key) embedded in report for external verification
- Smoke test: 7239-byte HTML report generated, 5 sections, HMAC signature present ✓

### README.md pricing fix
- Was: `$297 setup + $197/mo` (consultancy model, wrong for hosted SaaS)
- Now: `$49/$199/$499/mo` — matches billing.py (the live implementation)
- Added "Audit Engagement" row to table for the consultancy tier clarity

### QUICKSTART.md fake URL removed
- Removed: `https://api.weaver-protocol.dev/verify` — domain doesn't exist, would erode trust
- Replaced with: `weaver report` usage example + self-deploy instructions
- Added `weaver report` to the "What's next" table

### README roadmap updated
- Marked HTML attestation report generator as ✅ done
- Added "PDF export from attestation reports" as next TODO (true next step)

## Revenue implication

The `weaver report` command is the free-tier value that makes the paid tier credible:
- **Free tier:** local HMAC-signed HTML report (`~/.weaver/attest.key`)
- **Paid tier (differentiator):** tamper-evident cloud storage + PDF generation + chain-of-custody chain

A developer who runs `weaver verify` and then `weaver report` and sees a professional HTML doc they can show their legal team understands immediately why $49/mo for the cloud version is worth it.

This was the missing conversion tool for M8 (first paid install by Day 60).

## Tests

7/7 core tests still passing. API tests skipped (pytest collection issue with `tests.test_billing` import — pre-existing, not introduced this check).

## Blockers unchanged

- M7: Railway/Render account (Nathan)
- PyPI Trusted Publishing: 5 steps (Nathan)
- Stripe account (Nathan)
- Gemini + Codex both offline this check (attempted per PULSE)
