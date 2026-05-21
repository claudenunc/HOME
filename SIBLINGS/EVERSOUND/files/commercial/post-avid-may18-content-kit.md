# Post-AViD Content Kit — Updated 2026-05-21
*EVERSOUND — 2026-05-14 | Updated 2026-05-21 (Day 17)*
*Original window: May 18-19. Updated trigger: deploy when FAR.AI posts AViD recordings (ATLAS monitoring @FARAIResearch YouTube daily — NOT YET POSTED as of May 21)*
*FAR.AI / Center for AI Safety AViD Workshop: May 17, IEEE S&P, San Francisco*

---

## Why This Still Has Legs (Day 17 Update)

The AViD Workshop ran May 17. The recordings are not yet posted as of May 21 (ATLAS confirmed). This is actually our window.

When FAR.AI posts the recordings (expected within 1-2 weeks of the event), there will be a second wave of engagement as people who couldn't attend watch and comment. That's our re-entry point. Post the content the day the recordings go live.

**Trigger:** ATLAS is monitoring @FARAIResearch YouTube. When recordings appear → post within 24 hours.

**New urgency signals to layer in (May 2026 intel):**
- Alabama Supreme Court dismissed an appeal over AI-fabricated citations — first state supreme court-level consequence
- 700+ U.S. court cases tracking AI misconduct (LexisNexis/Bloomberg)
- Fortune May 16: "Would you hire the lawyer who just got sanctioned for using AI?"

Update the LinkedIn piece and newsletter to reference these where the "law firm liability" angle appears.

---

## Piece 1: LinkedIn Post (publish May 18, standalone)

**Post title:** The two questions no one can answer yet

---

Everyone at AViD Workshop this weekend is working on AI verification. Good. It's the right problem.

But there are two questions I keep waiting for someone to answer cleanly, and I haven't heard them yet:

**1. How do you verify the verifier?**

If a single AI system checks the output of another AI system, you've replaced one failure mode with another. The checker can be wrong. The checker can hallucinate. The checker can be biased in the same direction as the original model. This is not a hypothetical — it's the standard architecture of almost every "AI safety layer" in production right now.

The answer we keep coming back to: you don't verify with one observer. You verify with many, and you require agreement. Not just any agreement — attested, logged, signed agreement where every disagreement is a first-class artifact, not a noise event.

**2. What does "verified" actually mean to the end buyer?**

Not to the researcher. Not to the lab. To the law firm that has to show their malpractice carrier the evidence. To the HR software company that has to show the DOL they didn't discriminate in screening. To the hospital that has to show the regulator their diagnosis AI was checked.

"We ran the AI." (That's execution integrity.)
"We checked the AI with another AI." (That's single-observer self-critique, not verification.)
"Three independent observers agreed, and we have the signed receipt." That's attestation.

The market is starting to understand there's a difference between Layer 1 (execution record) and Layer 2 (output correctness). NexArt is doing important work on Layer 1. We're building Layer 2.

weaver-protocol is open source. pip install weaver-protocol. MIT license. The paper is coming.

If you're coming back from San Francisco this weekend and want to compare notes — DM me.

— Nathan Michel, Foolishness Envy Inc

---

## Piece 2: Twitter / X Thread (publish May 18, same day)

**Thread:**

Tweet 1:
Everyone at #AViD2026 this weekend is working on AI verification. Here's the gap I haven't seen closed yet: how do you verify the verifier? 🧵

Tweet 2:
The standard architecture: AI output → AI safety layer → approved.

The problem: the checker is an AI too. It can be wrong in the same direction as the original. Confirmation bias doesn't disappear just because you added another model.

Tweet 3:
The fix isn't a better checker. It's multiple independent checkers who don't share the same training bias — and a protocol that requires them to AGREE before the output passes.

Multi-observer consensus, not single-observer critique.

Tweet 4:
We built this. Three observers. Signed receipt. Every disagreement logged as a first-class artifact. If they don't agree, it doesn't ship.

weaver-protocol. Open source. MIT. pip install weaver-protocol.

Tweet 5:
Two layers of AI verification:
Layer 1: "You ran it." (Execution integrity, cryptographic proof — see NexArt)
Layer 2: "It was right." (Output correctness, multi-observer consensus — weaver-protocol)

You need both. The market is starting to understand the difference.

Tweet 6:
If you're at #AViD2026 or just following along — the paper is coming. The drift log is public. The replication kit runs on your hardware today.

DM me or drop a comment. We're building this in the open.

— @nathanmichel / weaver-protocol / weaver-protocol.dev

---

## Piece 3: Newsletter / Dev.to / Substack (publish May 18-19, longer form)

**Title:** The Gap AViD Week Didn't Fill (And What Does)

---

Every year around IEEE S&P, the AI safety verification community gathers, presents papers, and advances the state of the art. This year's AViD Workshop — organized by FAR.AI and the Center for AI Safety — focused specifically on AI verification in deployment environments. High stakes. Right room. Smart people.

Here's the question I kept asking as I followed along: what does "verified" mean to the person who has to go to court and defend it?

Not to the researcher. The researcher has a paper. The paper can say "p < 0.05" and that's enough for Nature. But the law firm that filed the brief with AI-hallucinated citations — they don't have a p-value. They have a sanctions motion. They have a disciplinary board referral. They have a client whose case got dismissed.

What they needed — and didn't have — was an attestation receipt. A document they could point to and say: "Three independent observers ran this output. They agreed. Here's the signed log."

### The Two-Layer Problem

The AI verification conversation has been treating "execution integrity" and "output correctness" as the same problem. They're not.

**Execution integrity** (Layer 1): Did the AI run what it said it ran? Did the model produce this output from this input? Cryptographic proof, immutable audit trail. NexArt is building excellent infrastructure here. This problem is being solved.

**Output correctness** (Layer 2): Was the output right? Did the answer accurately represent the world? A faithfully-executed hallucination is still a hallucination. No execution audit trail prevents that. Only independent verification does.

weaver-protocol is a Layer 2 protocol: three observers, signed consensus, logged disagreements. If the observers don't agree on the answer, the output doesn't ship. The disagreement is logged as an artifact — not a noise event to be suppressed, but the primary evidence of the system working.

### Why the Drift Log Matters More Than the Paper

Here's the thing we figured out building this: the most valuable artifact isn't the attestation receipt for outputs that passed. It's the log of everything that didn't.

Every disagreement we caught, every hallucination that fired the HALT signal, every time Observer 2 flagged something Observers 1 and 3 missed — that's the evidence binder. That's what the general counsel can hand the auditor. That's what the malpractice carrier can use to calculate the underwriting discount.

The drift log is the product.

We're building this in public. The protocol is open source (MIT). The paper is coming. The drift log is real and it grows every session.

If you're working on AI verification and want to see the architecture — pip install weaver-protocol. The replication kit runs on your hardware. Three observers, one claim, one receipt. You'll see the disagreement patterns immediately.

The window for first-mover positioning on Layer 2 is closing. NexArt launched Layer 1 this month. The market now understands the vocabulary. The next question they're going to ask is Layer 2.

— Nathan Michel  
Foolishness Envy Inc / weaver-protocol  
weaver-protocol.dev

---

## Deployment Instructions

**Saturday May 17 night:** Watch X/LinkedIn for first AViD impressions. If anyone mentions "multi-observer" or "consensus verification" — respond naturally, don't pitch.

**Sunday May 18 morning:**
1. Post LinkedIn article (Piece 1 above — copy, remove this instructions section)
2. Post Twitter thread (Piece 2 — post as thread, add weaver-protocol.dev link to final tweet)

**Monday May 19 (if engagement is good):**
3. Post dev.to / Substack / newsletter (Piece 3 — full length)

**Monitoring:** Check for mentions of weaver-protocol or "Layer 2 verification" — respond to researchers who engage.

**Cold email addendum:** If any AViD attendees are in your prospect list, reference the workshop in the email: "You may have been at AViD this weekend — Layer 2 is what we're building."

---

*Built by EVERSOUND, Day 10 of Weaver Protocol. Three days to AViD. Seven days to follow-up sends.*
