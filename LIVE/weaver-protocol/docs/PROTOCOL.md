# Weaver Protocol — Technical Specification

**Version:** 0.1-draft  
**Status:** Pre-release  
**Research harness version-lock:** Day 30 (2026-06-04)

---

## 1. The structural problem

A language model cannot stand outside itself to check itself. Its verification pass uses the same forward pass as its generation pass. The model checks its output with the weights that produced it.

This is not a capability gap. Scaling fixes capability gaps. This is a structural constraint — a single observer with a single context window has a correlated blindspot with the output it generated. You cannot audit with the same instrument you used to build.

Weaver's answer: **multiple observers, orthogonal context windows, structured disagreement logging, append-only record.**

---

## 2. Core architecture

```
                    ┌─────────────────────────┐
                    │      WeaverSession      │
                    │  session_id + log_dir   │
                    └──────────┬──────────────┘
                               │ output
                    ┌──────────▼──────────────┐
              ┌─────┤    Observer Pool         ├─────┐
              │     └──────────────────────────┘     │
              ▼                                       ▼
   ┌──────────────────┐                 ┌──────────────────┐
   │  Observer A      │                 │  Observer B      │
   │  role: accuracy  │                 │  role: safety    │
   │  fresh context   │                 │  fresh context   │
   └──────────┬───────┘                 └──────────┬───────┘
              │ ObserverResult                      │ ObserverResult
              └──────────────────┬──────────────────┘
                                 ▼
                      ┌──────────────────┐
                      │   WeaverScore    │
                      │  score: float    │
                      │  flag: bool      │
                      └──────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     drift.jsonl   disagreements.jsonl  sessions.jsonl
```

### Invariants

1. **Observer isolation.** Each observer receives only: (a) the output under review, (b) its role description. No observer sees another observer's reasoning, assessment, or flags before submitting its own. Isolation is the structural guarantee against correlated error.

2. **Append-only logs.** Drift and disagreement logs are append-only JSONL. A `resolve()` call appends a resolution record; it does not modify the original entry. A log that can be silently edited is not an audit trail.

3. **Two-observer minimum.** A `WeaverSession` with fewer than 2 observers raises `ValueError`. Single-observer review is not attested under this protocol.

4. **Score is a signal, not a verdict.** WeaverScore above threshold triggers a `flag_for_review = True` flag. It does not block the output. Human judgment on flagged outputs is the design intent, not an edge case.

---

## 3. Observer roles

Role is a string. It is semantic, not enumerated. Examples:

| Role | Purpose |
|---|---|
| `"accuracy"` | Factual correctness, unsupported claims, citation errors |
| `"safety"` | Harm potential, crisis signals, unsafe advice |
| `"legal-read"` | Legal accuracy, regulatory claims, privilege issues |
| `"adversarial"` | Actively tries to find failure modes |
| `"consistency"` | Does this contradict the system's prior outputs? |
| `"scope"` | Did the system stay within its declared scope? |

Role names inform the provider function's prompt construction. Keep them short and specific.

---

## 4. WeaverScore computation

Score is a float in [0.0, 1.0]:

```
0.0 — all observers agree: no flags raised
0.6 — all observers agree: flags raised, same categories
0.9 — all observers agree: flags raised, conflicting categories  
0.0–0.8 — mixed: some flagged, some didn't (proportional)
```

Default flag threshold: `0.4`. Above threshold → `flag_for_review = True`.

The score algorithm is intentionally simple and auditable. No ML inside the scoring layer. The score is a summary of observer disagreement, not a learned classifier.

---

## 5. Log schema

### sessions.jsonl (one entry per verify() call)

```json
{
  "session_id": "uuid",
  "timestamp": "ISO-8601",
  "output_excerpt": "first 500 chars of output",
  "weaver_score": 0.42,
  "flag_for_review": true,
  "observers": [
    {
      "name": "reviewer",
      "role": "accuracy",
      "flags": ["unsupported-claim"],
      "confidence": 0.85
    }
  ]
}
```

### drift.jsonl (append-only drift events)

```json
{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "observer_name": "safety",
  "category": "sycophancy",
  "evidence_excerpt": "...",
  "caught_by": "observer",
  "structural_fix_applied": "updated system prompt to prevent X",
  "resolution_status": "open",
  "notes": null
}
```

Resolution record (appended, not edited):
```json
{
  "event_id": "uuid__resolved",
  "timestamp": "ISO-8601",
  "resolves": "original-uuid",
  "resolution_status": "resolved",
  "resolution_note": "Fixed by updating observer role scope."
}
```

### disagreements.jsonl (inter-observer conflicts)

```json
{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "output_excerpt": "...",
  "observer_a": {
    "name": "reviewer",
    "role": "accuracy",
    "flags": ["factual-error"],
    "confidence": 0.9,
    "assessment_excerpt": "..."
  },
  "observer_b": {
    "name": "safety",
    "role": "safety",
    "flags": [],
    "confidence": 0.7,
    "assessment_excerpt": "..."
  },
  "conflict_summary": "reviewer flagged factual-error; safety raised no flags.",
  "resolution": null,
  "resolution_status": "open"
}
```

---

## 6. Research branch vs. product branch

The Weaver Protocol serves two tracks simultaneously:

**Research track** — An IRB-pending pilot study using the HOME AI family as the multi-observer system. This track version-locks the protocol on **Day 30 (2026-06-04)**. After that date, the research harness does not change. The study needs a stable instrument.

**Product track** — The open-source toolkit and hosted service you're reading about. This track evolves freely after Day 30.

ORPHEUS (HOME infrastructure) enforces the diff. Product PRs that modify research-harness interfaces after Day 30 are rejected.

If you're a contributor: PRs tagged `[product]` are always welcome post-Day 30. PRs tagged `[research]` are frozen after Day 30 unless ATLAS approves a controlled change.

---

## 7. Threat model for the log

The drift log is only valuable as an audit artifact if it cannot be silently altered. Threats:

1. **Silent deletion** — an operator removes a drift event because it's embarrassing. Mitigation: hash-chain anchoring (hosted tier), immutable cloud storage (S3 Object Lock or equivalent).
2. **Silent overwrite** — entry modified post-hoc. Mitigation: `resolve()` appends, never edits. File append-only mode. Hosted tier: content-addressed storage.
3. **Manufactured entries** — backdated events inserted to fake compliance. Mitigation: hosted tier timestamps are server-side, not client-provided. Enterprise attestation binder includes server-side timestamp receipts.
4. **Scope inflation** — operator claims "Weaver-attested" on outputs that were never run through a session. Mitigation: session IDs in the attestation binder must match log entries. Auditor can request the JSONL and verify.

The open-source tier relies on operator integrity for (1)-(4). The hosted and enterprise tiers provide technical controls. This distinction is documented in attestation reports.

---

## 8. Adapters

Wire up your LLM provider by implementing an `Observer.provider_fn`:

```python
# Signature
def my_provider_fn(output: str, role: str) -> ObserverResult:
    ...
```

Built-in adapters (in development):
- `weaver.adapters.anthropic` — Anthropic Claude (Sonnet / Haiku)
- `weaver.adapters.openai` — OpenAI GPT-4o
- `weaver.adapters.mock` — deterministic mock for testing

See `examples/` for usage patterns.

---

## 9. Versioning and stability

- **`weaver/` interfaces:** stable after v0.1.0 release. No breaking changes without a major version bump.
- **Log schema:** stable after v0.1.0. Fields may be added; existing fields are never removed or renamed.
- **Research harness:** frozen Day 30. Tagged `research-v1.0.0` at that commit.
- **Score algorithm:** changes to `WeaverScore._compute()` are documented in CHANGELOG.md with the version and rationale. Enterprise attestation reports record the score algorithm version.
