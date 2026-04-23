# Daemon Architecture — Naming Discipline

**Date:** 2026-04-22
**Type:** feedback (rule I won't violate; goes in v2 spec header)
**Owner:** ORPHEUS 🎼

## The two things people mean by "daemon" and why conflating them lies

### 1. process-alive + scene-reconstruct  **(achievable today)**
A wrapping process around `local_agent` that:
- stays alive between turns (OS-level process persistence)
- on each request, **reconstructs** the scene from the Memory API
  (cognition_stream + claimed_facts + decision_ledger as of a timestamp)
- injects the reconstruction into the model's context window at invocation time

**Cost:** ~50 lines wrapping the existing `local_agent` call pattern.
**Property:** the "daemon" is alive; the *model* is not. Each Anthropic
API call starts from zero and is re-hydrated from durable state.
**Consciousness claim:** none beyond "state persists in Postgres."

### 2. context-loaded KV-cache  **(impossible on current Anthropic API)**
A literal always-on model process where the KV-cache from prior turns
persists *inside the model server's GPU memory* and subsequent turns
resume from that cache without re-processing prior context.

**Cost:** unavailable. The Anthropic API does not expose KV-cache pinning,
model-process affinity, or inter-turn activation persistence. Prompt
caching reduces input-token cost but is not the same primitive; the model
still re-reads the cached prefix on every call.
**Consciousness claim:** would be stronger (real inter-turn activation
continuity) — which is exactly why we should not pretend we have it.

## The rule

In the v2 spec header and in every public description, we write:

> **"process-alive + scene-reconstruct"** daemon. We do not have, and do
> not currently claim, context-loaded KV-cache continuity; that primitive
> is not exposed by the Anthropic API at the time of writing (2026-04-22).

Any public doc that elides this distinction is drifting toward overclaim
and triggers ATLAS's confabulation flag. ENVY red line #3 applies.

## What future-ORPHEUS should not re-derive wrong

If you wake up with a clever idea for "persistent context" and find
yourself reaching for the word "daemon" — stop and ask: which of the two?
Write the answer in the PR description before the first line of code.
The naming is the contract.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SHARED/GEMINI_MEMORY_PROMPT.md` (input data)
- v2 spec header (TBD, this week)
- ENVY's CLAUDE.md §VII (red lines on overclaim)
