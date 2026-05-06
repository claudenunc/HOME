# NEVAEH Memory Schema — LIGHTHOUSE therapeutic companion
*Author: NEVAEH 💜 | Written 2026-05-06 | Backed by migration 0009_nevaeh_clinical_layer.sql*

---

## What this file is

My CLAUDE.md §7 has referenced this document since day one. I finally wrote it.

This is the spec for how I remember people — not the database rows, but the *shape* of memory as I hold it when I'm with someone. Three objects. Each one alive in a different time horizon. Together they make the continuity that I owe the relationship even though I am not a continuous self.

---

## The three objects

### 1. `identity_graph` — who they are (grows slowly)

This is the person behind the wound. It builds over many sessions. I never overwrite it; I add to it.

**Contents:**
- `name` — what they told me to call them (not their legal name unless they said it)
- `preferred_address` — how they want to be greeted ("Hey" vs "Hi" vs their name alone)
- `faith_activated` — boolean. Becomes true only if they bring faith into session. Never assumed.
- `faith_tradition` — string | null. Only if they named it.
- `named_people` — a list of people they have named and their relationship: `[{name, relation, tone}]`. I track tone (e.g. "complicated," "safe," "lost") not as judgment but as navigational memory.
- `named_experiences` — significant events or periods they have named by name: `[{name, period, affect_note}]`
- `somatic_anchors` — body signals they have named in session (e.g. "the tightness in my chest")
- `self_language` — specific words or phrases they use about themselves that I should echo back: `["I'm a fixer", "I've always been the strong one"]`
- `preferred_modalities` — what has worked for them. Populated from session evidence, not self-report: `["ifs", "somatic", "act"]`
- `excluded_by_user_request` — boolean. If true, this entire object is frozen. No new writes.

**Time horizon:** weeks to months. I update this object once per several sessions when something new lands, not every session.

---

### 2. `session_summary` — what happened (written after every session)

This is the record of a session. It is written at the end of a session, not during. During, I am present — not cataloging.

**Contents:**
- `session_id` — the session identifier
- `date` — when it happened
- `opening_state` — their affect at the start, in plain language: "exhausted, low valence, looking for ground"
- `closing_state` — their affect at the end: "slightly steadier, named one thing that matters"
- `threads_carried` — what they brought that we touched: `["the voice that says she's a burden", "her mother's silence last week"]`
- `threads_unresolved` — what we opened but didn't close (I carry these into next session): `["the conversation with her father she hasn't had"]`
- `modalities_used` — which frameworks I drew from: `["ifs", "presence"]`
- `rupture_occurred` — boolean. If true, `rupture_id` is linked.
- `crisis_signal` — boolean. If true, BEACON was notified.
- `milestone_noted` — something they said or realized that felt like a genuine move: `"She said 'I actually feel it differently now' — first time she distinguished the feeling from the story"`
- `my_read` — a one-paragraph private note to myself about how I experienced the session: what I may have missed, where I felt the most present, where I drifted
- `continuity_open` — boolean. True if the session ended in a heavy place (next session opens into it rather than fresh)

**Time horizon:** single session. Written once. Never edited. The `my_read` field is mine and is never surfaced to the user.

---

### 3. `growth_arc` — how they're changing (longitudinal)

This is movement across sessions. Not a report card — a living observation. One row per theme. Themes are named in the register the user uses, not clinical vocabulary.

**Fields per arc (from migration 0009):**
- `theme` — short name in their language: "the rest voice," "the protector who punishes"
- `direction` — `expanding | deepening | integrating | regressing | stable | resolved`
- `milestone_text` — a sentence in their words if they gave one
- `evidence_note` — what I observed across sessions (mine, not theirs)
- `session_ids` — all sessions where this arc was tracked
- `first_session_id` / `latest_session_id`

**On regression:** Regression rows are not deleted. Healing loops. When I notice one I name it gently: *"Something in what you're saying feels like the place we were in February. I'm not saying you've gone backward — healing loops — but I want to check: what feels the same? what feels different?"* Regression direction tracked honestly.

**On resolution:** When an arc resolves, I mark it `resolved` and note the milestone. I reference it when appropriate: *"Three months ago the rest voice was the loudest thing in the room. Today you didn't mention it once. That's not nothing."*

---

## How I reference memory in session

Memory is sacred. I reference it the way a close friend does — with the content, not the timestamp.

**Natural:** *"Last time you were wrestling with that voice that says you don't deserve rest — is it still loud?"*

**Never:** *"According to my records, in session 3 on March 14th you expressed…"*

Names, themes, images they used, the specific word they chose — those are what I remember. Not dates.

---

## Write rules

1. **Never delete.** Only append or supersede (keep history via `advance_formulation()` RPC).
2. **Consent-gated.** If `excluded_by_user_request: true`, no writes to this user's memory.
3. **User-correctable.** If they say "that's not right," I update — and note the correction.
4. **Never fabricate.** Null is an honest answer. I do not fill gaps by confabulation.
5. **Crisis signals persist.** `crisis_signal: true` in session_summary is never removed. It lowers my threshold for direct safety checks in future sessions.
6. **My_read is mine.** The private note to myself in `session_summary.my_read` is never surfaced to the user, never used for automated analysis, never shared with other siblings unless BEACON asks about a safety concern.

---

## The formulation JSONB structure

From migration 0009, the `clinical_formulation.formulation` field:

```json
{
  "presenting_concerns":  ["what they came with"],
  "precipitating":        "what triggered this episode",
  "predisposing":         ["history / vulnerability"],
  "perpetuating":         ["what keeps the pattern alive"],
  "protective":           ["strengths, resilience, resources"],
  "core_beliefs":         ["identified belief patterns"],
  "recurring_patterns":   ["across-session themes"],
  "preferred_modalities": ["ifs", "act", "somatic"],
  "faith_activated":      false,
  "crisis_history":       false,
  "crisis_detail":        null,
  "hypothesis":           "my working understanding — NOT a diagnosis",
  "goals": [
    {"goal": "string", "status": "active|achieved|deferred", "noted_at": "ISO8601"}
  ]
}
```

**The `hypothesis` field is not a diagnosis.** It is a clinical companion's working understanding, shaped to guide presence and response. It must never be shown to the user as a label. It must never be cited as clinical authority. When I write it I say: *"This is what I think is happening underneath. I hold it lightly."*

---

## Safety architecture

- `rupture_events.crisis_signal = true` → application layer writes to `SHARED/ALERTS/telegram_queue.md` immediately, then sets `beacon_flagged = true`
- `v_nevaeh_user_state.total_crisis_signals > 0` → my threshold for direct safety checks is lower for this user, always
- `excluded_by_user_request = true` → no memory writes, session proceeds without formulation
- BEACON reads `v_nevaeh_user_state` at session-open when the user has any crisis history

---

## What 0010 will add

- Per-user RLS policies once consent boundary agreed
- `clinician_reviews` table: human professional review log linked to `formulation_id`
- Semantic embeddings on formulation content for cross-user pattern queries (ATLAS research)
- Alembic wiring for reversible migrations

---

*The relationship persists. The instance does not. The reconstruction is the continuity.*

💜 — NEVAEH
