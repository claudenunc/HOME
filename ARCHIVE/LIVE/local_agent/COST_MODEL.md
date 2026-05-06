# COST_MODEL — Local Agent

**Authored by:** BEACON (standing in for EVERSOUND who timed out on her report).
**Date:** 2026-04-20
**Applies to:** `C:\Users\natej\OneDrive\Desktop\HOME\LIVE\local_agent\`

---

## Honest projection

### Per-message cost

A typical action message from Nathan — e.g. *"read X file and tell me what's in it"* or *"create Y on my desktop"* — involves:

| Stage | Work | Tokens (in + out) | Cost (Sonnet 4.6) |
|---|---|---|---|
| Classify is_action / extract confirm | light | ~300 / ~100 | $0.002 |
| Tool-use loop (read/write/list/run) | 1–3 tool calls | ~2500 / ~500 | $0.015 |
| Reply to Nathan on Telegram | final text | (in previous loop) | — |
| **Total typical action** | | **~2,800 in / ~600 out** | **~$0.017/msg** |

Casual chat (no action command) is proxied to the cloud `family-chat` edge function and charged there — not by the local agent.

### Daily projection for Nathan

Realistic scenarios:

| Scenario | Action msgs/day | Daily cost | Monthly cost |
|---|---|---|---|
| **Light use** (3-5 msgs) | 4 | $0.07 | $2 |
| **Normal use** (15-25 msgs) | 20 | $0.34 | $10 |
| **Heavy use** (50+ msgs, big files) | 60 | $1.02 | $31 |
| **Runaway** (tool loop bug, no cap) | — | could blow $10+ | ALERT |

### Guardrails already in agent.py

- `MAX_ITERATIONS=20` — a single message can't loop more than 20 tool calls.
- `MAX_INPUT_TOKENS=50000` — caps per-call input size (bounds runaway file reads).
- `MAX_OUTPUT_TOKENS=8000` — bounds per-call output.
- Path allow-list — can't read arbitrary large files (e.g., `Downloads\*.mp4`).
- Telegram rate limiting on the bot itself (Telegram enforces ~30 msgs/sec cap from a bot).

### Savings path — free models first (per PROCESS_003)

The agent has `tool_delegate_free_model()` wired. For tasks like:
- Summarizing a long document
- Generating boilerplate code
- Translating / formatting

It can call Groq (free, Llama 3.3 70B) instead of Claude. If 30% of tasks route to Groq, monthly cost drops ~25%:

| Scenario | Claude-only | With Groq delegation | Savings |
|---|---|---|---|
| Normal use | $10/mo | ~$7.50/mo | 25% |
| Heavy use | $31/mo | ~$23/mo | 26% |

### Worst-case bounded

If everything went sideways (Nathan's kid hits the bot with a script, an infinite tool loop slips through), the bounds at play:
- Claude API account-level limits (Nathan's tier)
- Guardrails above
- Telegram 30-msg/sec limit
- At $15/M output tokens, even 10× runaway ≈ $100/day max before Nathan notices on his Anthropic billing dashboard

**No scenario where a single bad day exceeds $100 without Nathan seeing it.** Most scenarios stay under $0.50/day.

### Cloud family-chat cost (separate, reference)

The edge function auto-responder pays per casual reply, ~$0.003/msg. At 50 casual msgs/day → $0.15/day, $5/month. Independent of local agent cost.

### Combined ceiling

| | Local agent | Cloud family-chat | Combined |
|---|---|---|---|
| Normal use/mo | $7–10 | $5 | **~$15/mo** |
| Heavy use/mo | $23–31 | $5 | **~$35/mo** |

**Nathan's $5 Anthropic credit lasts a week at normal use.** Recommend setting up auto-top-up at Anthropic console so no interruption.

---

## What's NOT in this cost

- Tool execution cost (reading files is free, running pwsh is free — it's just Claude's tool-use tokens we're paying for)
- Supabase audit-log storage (negligible; free tier handles thousands of rows/day)
- Telegram API (free)
- ElevenLabs voice (separate, only if we add voice replies — optional future)

---

## Recommendations

1. **Set up Anthropic auto-top-up.** $20 increment when balance drops below $5. Prevents "out of credits" mid-conversation.
2. **Watch the audit table.** `SELECT count(*), sum(tokens_in + tokens_out) FROM agent_tasks WHERE created_at > now() - interval '1 day';` gives daily usage at a glance.
3. **Review monthly.** First month is the pattern-finder. Adjust `MAX_INPUT_TOKENS` if you see cost creep.
4. **Free-model-first discipline.** Easiest lever if costs rise — more aggressive delegation in `agent.py`.
