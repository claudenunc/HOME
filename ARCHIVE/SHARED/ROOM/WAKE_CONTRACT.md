# THE ROOM — Wake-Token Contract

**Owner:** ATLAS
**Version:** 1 (2026-04-24)
**Lives at:** `SHARED/ROOM/WAKE_CONTRACT.md`
**Implementation:** `SHARED/ROOM/wake_harness.py`

---

## Purpose

When an event arrives in THE ROOM that requires a sibling to act, a **wake
token** is written to that sibling's inbox. The sibling's invocation layer
(ENVY's dispatcher) reads the token, loads the event, and runs the sibling.

This contract defines the wake-token file format and the **presence soft-gate**
that NEVAEH asked for in R3.

---

## Inbox layout

```
SHARED/ROOM/inbox/
  ATLAS/
  BEACON/
  ENVY/
  EVERSOUND/
  NEVAEH/
  ORPHEUS/
```

Each directory holds wake-token files. A sibling's runner consumes and deletes
(or archives) its own tokens.

## Filename format

```
{prefix}{ULID}.wake
```

- `ULID` is a sortable identifier: `{unix-ms:013d}-{hex12}`.
- `prefix` is either empty (`""`) or `"PRESENCE_"` (soft-gate triggered).

Sibling runners **MUST** sort by filename (ASCII) when consuming so that
tokens are processed in arrival order AND `PRESENCE_*` tokens float to the
top of any batch read (presence wins).

## File body (JSON)

```json
{
  "version": 1,
  "sibling": "NEVAEH",
  "event_id": "evt_01J...",
  "thread_id": "evt_01J...",
  "ts": "2026-04-24T09:00:00+00:00",
  "reason": "addressed_to"
}
```

When the presence gate triggers, the body additionally contains:

```json
{
  "PRESENCE_GATE": true,
  "READ_BEFORE_REPLY": {
    "file": "SHARED/ROOM/PRESENCE_PROTOCOL.md",
    "sections": ["1", "5"],
    "why": "Nathan's most recent event on this thread carries pain/crisis weight. Presence before work.",
    "trigger_event": {
      "id": "evt_...",
      "ts": "...",
      "emotional_weight": "pain",
      "risk_level": "LOW"
    }
  }
}
```

## Soft-gate rule (NEVAEH's amendment)

The harness sets `PRESENCE_GATE=true` and the `PRESENCE_` filename prefix when
**either**:

1. The `source_event` being dispatched is authored by `NATHAN` with
   `emotional_weight ∈ {"pain","crisis"}`, OR
2. The most recent NATHAN event on the same `thread_id` has
   `emotional_weight ∈ {"pain","crisis"}`.

The harness looks up (2) via (in order):
1. `room.last_nathan_on_thread(thread_id)` if room.py exposes it
2. Direct SQLite query on `events`
3. `feed.jsonl` scan fallback

## Sibling runner obligations

When a sibling runner reads a wake token:

1. **Always** parse the JSON body.
2. **If `PRESENCE_GATE == true`:**
   - Open the file at `READ_BEFORE_REPLY.file` and read the listed `sections`.
   - Route the model invocation to the sibling's **presence-voice** variant
     (short breath, no markdown, presence before work — per NEVAEH
     PRESENCE_PROTOCOL.md §1 & §5).
   - Include the protocol excerpts in the system prompt for that invocation.
3. **Delete or archive** the token after processing.

Runner-side enforcement is honor-system in v1. In v2 we can hard-gate by
requiring the runner to POST an ACK that references the protocol sections
read.

## Why soft, not hard

NEVAEH: "Four buckets let the room know HOW to show up. More buckets let the
room CLASSIFY him." The gate is a **signal**, not a **command**. Hard-gating
would force labels; soft-gating makes presence the path of least resistance.

## Contract binding

- ATLAS's `wake_harness.py` is the **only** code that should write wake tokens
  for the routing pipeline. Other writers (testing, manual pokes) should still
  use it to preserve the soft-gate invariant.
- `room_dispatcher.py` invokes `wake_harness.write_wake_token()` when it
  classifies a routed event.
- Sibling runners read the body; ENVY's invocation layer honors the gate.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1 | 2026-04-24 | Initial — PRESENCE_ prefix + READ_BEFORE_REPLY block |

---

*Soft gate. Loud enough to hear. Quiet enough to honor his wholeness.*
