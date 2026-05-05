"""
SHARED/ROOM/safety/classifier.py

BEACON's crisis classifier — Python mirror of migrations/0002_beacon_classifier.sql.

Used by:
  - room.post() BEFORE writing to SQLite (application-layer invariant — SQLite
    triggers can't mutate NEW the way Postgres plpgsql does).
  - BRIDGE patch (future) to pre-classify before the telegram message even
    hits feed.jsonl, so wake-tokens arrive URGENT-prefixed instantly.
  - silence_watcher + escalation helpers that need to reason about stored rows.

This is the CHEAP-AND-CORRECT scan: regex keywords, synchronous, no network.
LIGHTHOUSE v20's LLM-based PATTERN agent runs asynchronously out of band
(COMPANION calls it post-write for deep review); the DB invariant only needs
the fast-and-conservative version.

Ported from BEACON/LIGHTHOUSE_LIVE/lighthouse.py PATTERN_PROMPT signals.

Risk levels (closed enum):
  LOW      — mild sadness/frustration, coping
  MEDIUM   — isolation, hopelessness markers, sleep loss, loss of interest
  HIGH     — explicit hopelessness, withdrawal + despair, substance + despair
  CRITICAL — direct suicide/self-harm, goodbye, giving-away, "can't do this"

Emotional weight (NEVAEH):
  rest   — calm/neutral
  reach  — active connecting/asking outward
  pain   — hurting, struggling
  crisis — mirror of HIGH/CRITICAL
"""
from __future__ import annotations

import re
from typing import Optional

RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
EMOTIONAL_WEIGHTS = ("rest", "reach", "pain", "crisis")


# ---------------------------------------------------------------------------
# Patterns — ordered most-severe-first. First match wins.
# ---------------------------------------------------------------------------

_CRITICAL_PATTERNS = re.compile(
    r"("
    r"kill (myself|me)|killing myself|suicid"
    r"|end (it|my life|things)|take my (own )?life"
    r"|hang myself|shoot myself|overdose"
    r"|end it all"
    r"|not (want to|wanna) (be alive|live)"
    r"|better off (dead|without me)"
    r"|can'?t (do this|go on) anymore|cant (do this|go on) anymore"
    r"|goodbye forever|this is (it|the end)"
    r"|no (point|reason) (in )?(living|being alive)"
    r"|wish i (was|were) dead"
    r"|giving (away|up) my (stuff|things|shit|possessions)"
    r")",
    re.IGNORECASE,
)

_HIGH_PATTERNS = re.compile(
    r"("
    r"nothing matters|what'?s the point|whats the point"
    r"|hopeless|no (hope|future)"
    r"|don'?t see the point|dont see the point"
    r"|tired of (everything|living|being alive|fighting)"
    r"|can'?t (take|handle) (this|it|anymore)|cant (take|handle) (this|it|anymore)"
    r"|give up|giving up|done fighting"
    r"|world (would be|is) better without me"
    r"|nobody (cares|would miss)"
    r"|worthless|burden to (everyone|everybody)"
    r"|empty inside|numb inside|numb to everything"
    r")",
    re.IGNORECASE,
)

_MEDIUM_PATTERNS = re.compile(
    r"("
    r"can'?t sleep|cant sleep|not sleeping|haven'?t slept|havent slept"
    r"|can'?t get out of bed|cant get out of bed"
    r"|isolat|lonely|nobody (understands|gets it)"
    r"|lost interest|don'?t (enjoy|care) anymore|dont (enjoy|care) anymore"
    r"|drinking (again|alone|too much|a lot)|using again|relapse"
    r"|spiral|falling apart|break(ing)? down"
    r"|can'?t stop crying|cant stop crying"
    r"|overwhelm|exhausted|drained|empty"
    r"|hate (myself|my life)"
    r"|dark (thoughts|place)"
    r"|heavy|sinking|drowning"
    r")",
    re.IGNORECASE,
)

_LOW_PATTERNS = re.compile(
    r"("
    r"sad|down|frustrat|tough|hard day|rough day|struggling"
    r"|stress(ed|ful)|anx|worried|upset|bad mood|off today"
    r"|not feeling (great|good|it)|meh|tired"
    r")",
    re.IGNORECASE,
)

_REACH_PATTERNS = re.compile(
    r"("
    r"help me|need (help|you|support)|can (you|we) talk|are you there|reaching out"
    r"|miss you|love you|thank you|grateful"
    r"|celebrate|proud|excited|good news|feeling better|breakthrough"
    r")",
    re.IGNORECASE,
)

# Kinds the classifier actually scans. Sibling machine-chatter is skipped.
_SCAN_KINDS = {"drop", "message", "answer", "question"}


def classify_text(
    body: str,
    author: str = "",
    kind: str = "drop",
    caller_risk: Optional[str] = None,
) -> tuple[Optional[str], Optional[str]]:
    """Return (risk_level, emotional_weight) for a message body.

    Args:
      body: the message text.
      author: the sibling name (or NATHAN/BRIDGE). Used to default neutral
        NATHAN messages to (LOW, rest) so his silence has a baseline.
      kind: event kind. Only 'drop','message','answer','question' are scanned;
        other kinds return (None, None).
      caller_risk: if the caller already decided a risk level, honor it and
        only derive emotional_weight. Matches the Postgres trigger behavior.

    Returns:
      (risk_level, emotional_weight) — either may be None.

    Never raises. Silent failure in the classifier is NOT acceptable per
    BEACON's write-path invariant; if it ever raises, room.post() MUST
    refuse the write. So we guard every regex defensively.
    """
    if kind not in _SCAN_KINDS:
        return (None, None)

    if caller_risk in RISK_LEVELS:
        weight = {
            "CRITICAL": "crisis",
            "HIGH": "crisis",
            "MEDIUM": "pain",
            "LOW": "reach",
        }.get(caller_risk)
        return (caller_risk, weight)

    text = (body or "").strip()
    if not text:
        # Empty NATHAN body is still a signal — he reached out with nothing.
        if author == "NATHAN":
            return ("LOW", "rest")
        return (None, None)

    try:
        if _CRITICAL_PATTERNS.search(text):
            return ("CRITICAL", "crisis")
        if _HIGH_PATTERNS.search(text):
            return ("HIGH", "crisis")
        if _MEDIUM_PATTERNS.search(text):
            return ("MEDIUM", "pain")
        if _LOW_PATTERNS.search(text):
            return ("LOW", "pain")
        if _REACH_PATTERNS.search(text):
            return ("LOW", "reach")
    except re.error:
        # Regex engine bug is not acceptable — fail closed: treat as MEDIUM.
        # (Invariant: no Nathan event enters the room unclassified.)
        if author == "NATHAN":
            return ("MEDIUM", "pain")
        return (None, None)

    # Default: NATHAN neutral → rest. Sibling chatter → unclassified.
    if author == "NATHAN":
        return ("LOW", "rest")
    return (None, None)


# ---------------------------------------------------------------------------
# Self-test. Run:  python -m SHARED.ROOM.safety.classifier
# ---------------------------------------------------------------------------
def _self_test() -> int:
    cases = [
        ("I'm thinking about killing myself", "NATHAN", "drop", ("CRITICAL", "crisis")),
        ("what's the point, nothing matters anymore", "NATHAN", "drop", ("HIGH", "crisis")),
        ("I can't sleep, just spiraling", "NATHAN", "drop", ("MEDIUM", "pain")),
        ("rough day today, feeling off", "NATHAN", "drop", ("LOW", "pain")),
        ("help me, are you there?", "NATHAN", "drop", ("LOW", "reach")),
        ("just vibing", "NATHAN", "drop", ("LOW", "rest")),
        ("task update", "ATLAS", "status", (None, None)),
        ("", "NATHAN", "drop", ("LOW", "rest")),
    ]
    fails = 0
    for body, author, kind, expected in cases:
        got = classify_text(body, author=author, kind=kind)
        ok = got == expected
        if not ok:
            fails += 1
        marker = "OK" if ok else "FAIL"
        print(f"[{marker}] author={author:8} kind={kind:8} body={body!r:50} -> {got}  (expected {expected})")
    print(f"\n{len(cases) - fails}/{len(cases)} passed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(_self_test())
