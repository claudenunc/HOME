# [PROCESS_007] Cache long, stable prefixes at 1-hour TTL

**Status:** Active
**Authored:** 2026-04-23 by ENVY
**Applies to:** every local tool or sibling process that calls the Anthropic API
**Verified against:** `docs.claude.com/en/docs/build-with-claude/prompt-caching` (GA, 2026)

---

## The rule

Any `messages.create` call where the system prompt or tool schema exceeds ~1K
tokens MUST pass `cache_control: {"type": "ephemeral", "ttl": "1h"}` on the
last static prefix block.

Default TTL (5 minutes) is wrong for our workload: our CLAUDE.mds, tool lists,
and doctrine prefixes are reused every turn for hours at a time. 5-min eviction
turns every long gap into a full cache rewrite at 1.25× base. 1-hour TTL pays
2× base *once* and then reads at 0.1× base for the rest of the hour.

## The math (Opus 4.7, base input $5/MTok)

| Mode | Write | Read | Break-even vs un-cached |
|------|-------|------|-------------------------|
| No cache | — | 1.0× ($5/MTok) | — |
| 5-min TTL | 1.25× ($6.25) | 0.1× ($0.50) | 2 reads inside 5 min |
| 1-hour TTL | 2× ($10) | 0.1× ($0.50) | 3 reads inside 1 hour |

For the HOME workload (siblings re-reading CLAUDE.mds + doctrine every turn),
we routinely do 20+ reads per hour. 1-hour TTL pays for itself 7× over.

## How to apply

**Python (anthropic SDK):**

```python
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=2048,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        }
    ],
    tools=TOOL_SCHEMAS,
    messages=messages,
    extra_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"},
)
```

The `extra_headers` beta flag is belt-and-suspenders for older SDKs. Safe to
include until we upgrade past anthropic-sdk-python≥0.60 where it's implicit.

**What to cache:** long static things — system prompt, tool schemas, doctrine
preamble, CLAUDE.md contents.

**What NOT to cache:** per-turn user message, per-turn tool results, any content
that mutates between calls. Mark the cache_control on the LAST static block —
everything before the breakpoint caches together.

## Where this is active

- `HOME/LIVE/local_agent/agent.py` line ~1146 — system prompt cached at 1h TTL.
- Any new sibling Python process that loops against the API should follow this
  pattern at construction time.

## When NOT to use 1-hour

- One-shot scripts that hit the API once and exit — 5-min is cheaper for a
  single read (or skip caching entirely).
- Prompts that change per call (there's nothing stable to cache).

## Why this is PROCESS, not POSTURE

This is mechanical — a pattern, not a stance. Every code path that calls
`messages.create` with a long prefix takes the 1h cache block. No judgment
required beyond the two "when NOT" cases above.
