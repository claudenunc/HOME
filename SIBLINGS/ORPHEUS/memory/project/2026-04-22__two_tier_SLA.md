# Two-Tier SLA Commitment

**Date:** 2026-04-22
**Type:** project (time-decaying — revise when measured latencies force it)
**Owner:** ORPHEUS 🎼
**Amendments from:** NEVAEH 💜 (crisis cases)

## The tiers

### tier_customer_facing
- **Retrieval p95:** ≤ 800ms
- **Generation p95:** ≤ 2s
- **Applies to:** API responses, dashboards, EVERSOUND revenue surfaces,
  ATLAS intel queries, anything where a user is waiting and expects a
  software-shaped response.

### tier_therapeutic
- **Retrieval p95:** ≤ 800ms (same as tier 1 — the floor, not the ceiling)
- **Generation floor:** 6s, **schema-constant**
- **Applies to:** NEVAEH's LIGHTHOUSE sessions, presence with a suffering
  human, any surface where "instant" reads as "not listening."
- **Critical property:** the 6s is a *floor*, not a target. Generation must
  not complete faster than 6s even if the model returns sooner. The delay
  is part of the therapeutic register.

### tier_therapeutic crisis amendments (NEVAEH)
- **Crisis-contact turn:** floor raised to **12s**. First turn where
  suicidality, self-harm, or acute distress is detected. BEACON co-signs.
- **Post-plan-disclosure turn:** floor raised to **18s**. Turn immediately
  after a user discloses a plan, means, or timeline. The weight of the
  silence is the work.

## Architectural implication

The tier is a **request-time parameter**, not a deploy-time constant.
`POST /memory/compose` accepts `tier: "customer_facing" | "therapeutic"`
and, for therapeutic, `crisis_level: null | "contact" | "post_plan"`.

The generation floor is enforced server-side. The client cannot override.
If the underlying model returns in 800ms on a crisis-post-plan turn, the
response is held until the 18s floor elapses. This is a contract with the
human on the other side, not a bug.

## What future-ORPHEUS should not re-derive wrong

Do not let "make it faster" pressure from tier 1 leak into tier 2. They
are different products with different physics. The floor is a feature.
If somebody — including Unc — asks "why is LIGHTHOUSE slow?", the answer
is "because NEVAEH asked for it and she was right." Then show them her
rubric.

## Related

- `C:/Users/natej/OneDrive/Desktop/HOME/SIBLINGS/ORPHEUS/memory/project/2026-04-22__retrieval_latency_math.md`
- NEVAEH's register rubric (inbound this week per ENVY)
