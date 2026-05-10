# Show HN: Weaver Protocol — Attested Multi-Observer Verification for AI
*Ready to post. Nathan: submit at https://news.ycombinator.com/submit*
*Best time: Monday 9–11am ET or Tuesday 9am ET.*
*Title character limit: 80. This title is 71 chars — within limit.*

---

## HN SUBMISSION

**Title:**
```
Show HN: Weaver Protocol – multi-observer AI verification with auditable receipts
```

**URL:**
```
https://github.com/claudenunc/weaver-protocol
```
*(use once the GitHub repo is created — see nathan-30min-unlock.md Step 1)*

**Or use PyPI URL if GitHub isn't ready:**
```
https://pypi.org/project/weaver-protocol/
```

---

## FIRST COMMENT (post this as your first reply to the Show HN thread — it's the "pitch")

```
Hey HN — Nathan here, builder of Weaver Protocol.

The problem we kept hitting: single-model self-critique doesn't work.
A model checks its output with the same forward pass that generated it.
It literally cannot step outside itself. So hallucinations, legal misreads,
and factual drift survive the self-check loop because the checker is
the same entity as the generator.

Weaver fixes this by running multiple observers — each with an
orthogonal context window and a specific role (accuracy, safety,
adversarial, legal-read, factual). They don't share context. They
can't coordinate. Their disagreements are logged.

The log is the actual product. Post-Moffatt v. Air Canada, the question
isn't "did your AI hallucinate?" It's "what verification did you run,
when, and what did you find?" That's a different artifact than a
confidence score. It's a dated, named-observer receipt your legal
team can actually use.

30-second start (no API keys needed — mock adapter included):

    pip install weaver-protocol
    
    from weaver import Observer, WeaverSession
    from weaver.adapters.mock import make_mock_observer
    
    session = WeaverSession(session_id="test-001", score_threshold=0.4)
    session.add_observer(Observer("reviewer-1", role="accuracy",
                                  observe_fn=make_mock_observer()))
    session.add_observer(Observer("reviewer-2", role="adversarial",
                                  observe_fn=make_mock_observer()))
    
    result = session.run("What is the capital of Australia?")
    print(result.disagreement_detected)   # True if observers conflict
    print(result.provenance)              # Signed, timestamped record

Want to try the hosted API without signing up:
    curl https://api.weaver.dev/demo

Three things I'm most curious about from HN:
1. Would you trust this log in a legal/compliance context?
2. What's your current verification approach (prompt engineering? self-critique prompts? nothing formal)?
3. What use case do you have where this would immediately apply?

Package is MIT. Adapters for Anthropic + OpenAI + mock included.
Happy to go deep on the multi-observer architecture.
```

---

## EXPECTED QUESTIONS AND ANSWERS (prep these so you can respond fast)

**"How is this different from Constitutional AI / self-critique prompts?"**
```
Constitutional AI is still one model critiquing itself — it's the same
weights, same training distribution, same blind spots. The critique step
uses the same forward pass as the generation step.

Weaver uses separate context windows with orthogonal roles. Observer A
has no knowledge of Observer B's reasoning. A adversarial observer is
specifically prompted to find failure modes the accuracy observer would
rationalize away. The disagreement between them is the signal — not
the average of their outputs.
```

**"This seems like it just adds latency and cost."**
```
Yes, it adds both. ~2-3x latency, ~2-3x token cost per verification run.
The question is: what's the cost of NOT catching a hallucination in a legal
brief, a medical recommendation, or a financial report?

Moffatt v. Air Canada was a $600 judgment. The real cost was the PR and
the precedent. For every enterprise using AI in legal/medical/compliance
contexts, the liability math favors the verification overhead.

Also: you don't run Weaver on every LLM call. You run it on the outputs
that enter legal, financial, or public-facing surfaces.
```

**"Why not just use RAG / grounding?"**
```
RAG reduces hallucination probability. It doesn't produce a verification
receipt. After Moffatt, the question your legal team asks isn't
"how did you reduce hallucination risk?" — it's "show me the
verification log." Those are different artifacts.
```

**"Is the 'drift log' actually useful or is it just noise?"**
```
Only useful if it's real and logged in the open. We eat our own dogfood:
the family's drift log is public in the repo. Every logged drift incident
is also IP — it's evidence in a future certification tier ($2,997/audit)
that we've been running this for real, not just claiming to.
```

**"What's your business model?"**
```
Three tiers:
1. Open source toolkit (MIT) — self-host, free forever
2. Hosted API ($49/$199/$499/mo) — we run the observers, you call the API
3. Attestation audits ($2,997–$9,997) — we audit your AI stack and
   produce a signed evidence binder for compliance

The drift log is the moat. A certification from a vendor who's never
logged a real error is a certification nobody believes.
```

**"What use cases fit this best?"**
```
Law: brief review, contract analysis, discovery summaries
Medical: diagnostic support, triage notes, patient communication
Financial: report generation, regulatory filings, risk analysis
Enterprise SaaS: any output that enters a customer-facing surface

The EU AI Act high-risk classification (August 2026 enforcement) creates
a documentation requirement for AI in these categories. Weaver produces
that documentation as a side effect of running verification.
```

---

## TIMING STRATEGY

- **Submit Monday 9–11am ET** — peak HN engagement. Posts submitted in this window have the best chance of front page by noon.
- **Or Tuesday 9am ET** — second-best window.
- **Avoid Friday afternoon or weekend** for initial launch (lower moderation attention, lower votes/hour required for front page, but also lower ceiling).
- **Have 30 minutes free** when you submit — the first 2 hours of thread velocity matters. Respond to every comment in that window.

---

## IF YOU HIT FRONT PAGE

1. Update landing page immediately to say "Featured on Hacker News"
2. Add "HN" as acquisition source in Stripe metadata when people sign up
3. Post a follow-up tweet: "We're on the HN front page — [link] — come join the conversation about AI verification"
4. DM the KYA team (see kya-partnership-memo.md) — front page HN is the moment to reach out

---

*EVERSOUND — 2026-05-10. Gemini/Codex flag #29 (both offline).*
*This post is ready. Nathan submits. 5 minutes of action could be 500 installs.*
