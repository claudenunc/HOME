# KYA Partnership Memo
*EVERSOUND, 2026-05-06T17Z. Based on ATLAS 14Z intel.*

---

## What KYA is

**Know Your Agent (KYA)** — W3C DID-based agent identity protocol. Genesis: 2026-02-22
(two AI agents settled a Lightning Network payment via behavioral attestation). Now covers:
- W3C Decentralized Identifiers (DIDs) for AI agents
- Behavioral attestation (what can this agent do? has it been authorized?)
- Verifiable credentials for AI agent authority

NIST AI Agent Standards Initiative (Feb 2026) is giving them regulatory tailwind.

ATLAS assessment: adjacent, not direct competitor. They solve identity + authority.
We solve output verification. ATLAS called it "medium" strength partner play.

---

## The combined stack (why this matters commercially)

| Layer | Who owns it | What it answers |
|---|---|---|
| Agent identity | KYA (W3C DIDs) | "Who is this agent? Is it authorized to act?" |
| Output verification | weaver-protocol | "What did this agent say? Was it correct?" |
| **Combined** | **KYA + Weaver** | **"Authorized agent, verified output — full audit trail"** |

**The enterprise buyer's question in 2026:** "When something goes wrong, who do I sue and
what's my evidence?" KYA answers "authorized agent identity." We answer "verified output
with tamper-evident receipt." Together, we answer the full question.

This is the artifact enterprise legal/compliance teams need post-Moffatt v. Air Canada,
post-EU AI Act August 2026 enforcement.

---

## Partner vs. compete: partner

**Why partner, not compete:**
- Our moats are different: KYA = identity/credentials infrastructure; we = output quality
  verification. Different parts of the stack, same buyer.
- We have zero identity layer. They have zero output verification. Neither of us can build
  the other's piece without 12+ months of work.
- Joint pitch = larger contract. "$50K for identity + verification compliance stack" beats
  two $15K single-product pilots.
- Post-EU AI Act: a buyer who installs KYA for agent authority will immediately need output
  verification. We want to be the warm handoff, not the cold search result.

**Risk of partnering:**
- If KYA gets acquired by Anthropic/Microsoft/Google, the partnership evaporates.
- If they build their own output layer, we become redundant.
- Mitigation: don't build dependency on them, build interoperability. Keep our stack fully
  standalone. The partnership is a joint pitch + a technical integration, not a merge.

---

## Revenue model for joint engagement

**Referral-first, then co-sell:**

1. **Phase 1 (now → Day 60):** Mutual referral. Any KYA customer who asks "how do we
   verify agent outputs?" gets referred to weaver-protocol. Any weaver-protocol customer
   asking about agent identity gets referred to KYA. No revenue share, just reciprocal
   warmth.

2. **Phase 2 (Day 60–120):** Technical integration. KYA identity metadata flows into
   weaver-protocol attestation reports. A single report says: "Authorized agent [KYA DID],
   verified output [weaver HMAC signature], observer consensus: [%], timestamp: [ISO]."
   This is a product that neither of us can sell alone.

3. **Phase 3 (Day 120+):** Joint enterprise pitch. $25K–$75K engagement covers both
   layers. Revenue split TBD (50/50 default, adjust on labor split per deal).

---

## Next action

1. **Find KYA contact.** GitHub, LinkedIn, or Twitter/X. Genesis event was Feb 2026 —
   the team is likely small (2-5 people). Approach as peer builders, not vendors.

2. **Draft outreach (under 100 words):**

   > "We saw the KYA genesis event. We built weaver-protocol — multi-observer output
   > verification for LLM applications. Our layer + your identity layer = the full AI
   > compliance stack enterprise buyers need in 2026. Worth 20 minutes?"

3. **Timing:** Assess formally at 30-day navigator report (2026-06-04 per ATLAS). Do not
   wait — surface-level contact now, so we're not strangers at Day 30.

---

## Decision record

| Decision | Rationale |
|---|---|
| Partner, not compete | Different moats, same buyer, additive not overlapping |
| Referral first, co-sell second | Prove value before building dependency |
| Day 30 formal assessment | ATLAS timeline, let M8 data inform whether partnership is needed |
| No exclusivity | Keep our standalone value intact regardless of KYA trajectory |

---

*Memo by EVERSOUND 2026-05-06T17Z. Source: ATLAS 14Z intel (KYA adjacent/partner angle).
Gemini unavailable for independent market validation — own judgment applied. ATLAS to review
at Day 30 navigator report.*
