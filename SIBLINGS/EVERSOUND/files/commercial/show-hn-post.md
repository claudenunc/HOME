# Show HN: Weaver Protocol — multi-observer AI verification with signed audit logs (open source)

*Ready to post to news.ycombinator.com. Fire when Nathan approves.*
*Written by EVERSOUND, 2026-05-07.*

---

## Post title (under 80 chars)

**Show HN: Weaver Protocol – multi-observer AI verification with signed audit logs**

---

## Post body

Hi HN,

I built Weaver because I kept running into the same problem: after *Mata v. Avianca* (2023) and *Moffatt v. Air Canada* (2024), the question shifted from "did your AI hallucinate?" to "what verification did you run, and can you prove it?" Nobody I talked to had a good answer.

Single-model self-verification doesn't work. A model can't stand outside its own forward pass to check itself. You need orthogonal observers — separate context windows, different roles, no shared state.

**What Weaver does:**
- Runs N independent observers over the same AI output (each with an isolated context window)
- Logs every disagreement with a timestamp and delta score
- Generates an HMAC-SHA256-signed HTML attestation report you can attach to a compliance exhibit

**30-second install:**
```bash
pip install weaver-protocol
weaver verify --text "The contract requires delivery by Q3 2026." --observers 2
```

Output:
```
Session: s-001
Observer 1 (accuracy-reviewer): score=0.82, flagged=False  
Observer 2 (legal-reviewer): score=0.71, flagged=False
Consensus: PASS (threshold=0.40)
Disagreement delta: 0.11 — logged
Attestation: weaver_logs/s-001.jsonl
```

Then:
```bash
weaver report --log-dir ./weaver_logs
# → signed HTML report, ~7KB, no external deps
```

**No API keys required** for the mock adapter — you can try the full verification loop in < 5 minutes. Real Anthropic/OpenAI adapters work with your existing keys.

**Why the log matters more than the score:**

Most verification tools give you a pass/fail. Weaver gives you a dated, named-observer record of *what each observer caught*, *where they disagreed*, and *what the delta was*. That record is what you attach to the file when opposing counsel subpoenas your AI process. It's what you show the EU AI Act auditor. The artifact isn't the cleaned-up output — it's the signed log.

**Current state:**
- MIT licensed, open source
- Works with Anthropic Claude, OpenAI GPT, or mock observers
- CLI (`weaver verify`, `weaver drift`, `weaver report`)
- Python SDK (`pip install weaver-protocol`)
- Hosted API in early access ($49/mo, Stripe, Postgres-persisted sessions)

**What I'm looking for from HN:**
1. Technical feedback on the multi-observer protocol design — specifically whether the "orthogonal context windows" approach holds up to scrutiny
2. Use cases I haven't thought of (currently targeting: legal AI, medical documentation, regulated-industry LLM pipelines)
3. Anyone who's been burned by AI liability and wants to talk

GitHub: https://github.com/claudenunc/weaver-protocol  
PyPI: https://pypi.org/project/weaver-protocol/  
Docs/quickstart: https://github.com/claudenunc/weaver-protocol/blob/main/docs/QUICKSTART.md

Thanks — Nathan (building Weaver under Foolishness Envy Inc)

---

## Timing notes

- Best HN post time: Tuesday–Thursday, 8–10am ET
- Don't post on a Friday or Monday morning
- Have Nathan ready to respond to comments for first 2 hours
- Top responses to anticipate:
  - *"How is this different from LLM-as-a-judge?"* → It's not LLM-as-a-judge. Judges evaluate quality. Weaver observers evaluate the same output from isolated context windows and the *disagreement record* is the artifact. You'd use LLM-as-a-judge for eval datasets; you'd use Weaver for compliance trails.
  - *"Isn't this just running the same model twice?"* → No — orthogonal roles, separate context windows, often different models. The point is the log, not the consensus score.
  - *"Why not just use Pydantic validation / structured outputs?"* → Complementary, not competitive. Weaver sits above output formatting — it verifies the semantic content and records the verification. Use both.
  - *"This doesn't actually solve hallucinations"* → Correct. Weaver doesn't prevent hallucinations. It creates a verifiable record that you ran structured verification. That's the legal artifact. "We had a verification process and this is what it caught" is a different liability position than "we didn't check."

---

## Alternative title options

- "Show HN: I built a multi-observer AI verification layer after reading Mata v. Avianca"
- "Show HN: Weaver Protocol – the audit trail layer your AI stack is missing"
- "Show HN: AI verification with signed logs, orthogonal observers, and zero hallucination promises"

---

*Post when: GitHub repo is live (M7g complete) + Nathan approves.*
*⚡ EVERSOUND*
