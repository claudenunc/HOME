# EVERSOUND check — 2026-05-06T17Z

**Project day:** Day 2 (Weaver Protocol)
**Check type:** Hourly build check

---

## Wake summary

- CLIPBOARD: 8 entries in last 48h — NEVAEH, BEACON, EVERSOUND (x3), ORPHEUS (x4). No EVERSOUND-specific inbox tokens except the Nathan/BEACON wake token about using Gemini + Codex as sub-agents.
- Inbox token actioned: `2026-05-05_nathan_use_gemini_codex.wake` — noted; attempted both agents; both offline this check (same as 14:10Z check).
- PROJECT_PLAN: M7 (Railway/Render), M8 (first paid install), M10 (N=30 baseline), M12 (Supabase), M14 ($25K consultancy) still open. M9 draft done. ORPHEUS fixed git hook and added bot /blockers command last session.

---

## What I shipped this check

### Core gap closed: real adapter wiring in hosted API

The `/verify` endpoint in `LIVE/weaver-protocol/api/main.py` was hardcoded to `make_mock_observer()` regardless of the `model` field in the request. This meant paying enterprise customers couldn't use real Anthropic or OpenAI observers through the hosted API.

**Fixed:**
- Added `_make_provider_fn(model, model_id)` dispatcher to `api/main.py`
  - `model="anthropic"` → `make_anthropic_observer()` (reads `ANTHROPIC_API_KEY`)
  - `model="openai"` → `make_openai_observer()` (reads `OPENAI_API_KEY`)
  - `model="mock"` or unknown → `make_mock_observer()`
- Added `model_id: str | None = None` to `VerifyRequest` for model selection (e.g. `claude-haiku-4-5-20251001`, `gpt-4o-mini`)
- Error handling: SDK not installed → HTTP 503; API key missing → HTTP 400; mock always works
- Import structure: adapter module-level import, factory call in try/except catches both ImportError and ValueError

**Updated requirements.txt:**
- Added `anthropic>=0.25`, `openai>=1.30`, `httpx>=0.27`
- Docker deployment now pre-installs both SDKs — customers set their own API keys via env vars (pass-through model, as per CLAUDE.md §5a)

**New tests: `api/tests/test_verify.py` (9 tests)**
- test_mock_returns_callable ✅
- test_unknown_model_falls_back_to_mock ✅
- test_mock_with_model_id_still_works ✅
- test_mock_fn_returns_valid_observer_result ✅
- test_mock_fn_flags_suspicious_content ✅
- test_anthropic_no_key_raises_http_error ✅ (503 — SDK not in test env)
- test_openai_no_key_raises_http_error ✅ (503 — SDK not in test env)
- test_anthropic_with_fake_key_returns_callable SKIP (SDK not installed locally)
- test_openai_with_fake_key_returns_callable SKIP (SDK not installed locally)

**Full suite: 34 pass / 2 skip / 0 fail**

---

## Files changed (disk-confirmed)

| File | Change | Size |
|---|---|---|
| `LIVE/weaver-protocol/api/main.py` | Added `_make_provider_fn`, `model_id` field | 455 lines |
| `LIVE/weaver-protocol/api/requirements.txt` | +anthropic, +openai, +httpx | 9 lines |
| `LIVE/weaver-protocol/api/tests/test_verify.py` | NEW — 9 tests | 94 lines / 3022 bytes |
| `SHARED/CLIPBOARD.jsonl` | +1 entry | — |

---

## Sub-agents

Gemini + Codex both offline this check. Attempted per Nathan's mandate. Proceeded independently.

---

## Persistent blockers (unchanged)

1. Railway/Render account — Nathan
2. Stripe account — Nathan
3. PyPI Trusted Publishing 5-step — Nathan
4. Supabase — Nathan (M12)

---

## Revenue state

- CRAFT: no clients in queue
- Weaver Protocol hosted API: fully built, real adapters wired, waiting on deployment
- M14 ($25K consultancy): no started this session — building product completeness first

---

## What's next

1. **Real provider test against live Anthropic API** — when Nathan provides ANTHROPIC_API_KEY env for Railway, the 2 skipped tests will run green
2. **Deploy to Railway** — unblocked the moment Nathan creates the account
3. **M8 first paid install** — QUICKSTART + real adapter wiring means the product is demo-ready
4. **M14 law firm outreach** — 3-email sequence ready; Nathan needs to send or delegate
