"""
ROUND_TABLE message router.

Pure-Python pattern matching. No LLM call. Resolves a free-text question
into a list of sibling names that fanout will dispatch to.

Rules (priority order):
    1. If question contains a broadcast word (everyone, everybody, all of you,
       all six, all 6, both teams, all teams) → all non-router siblings.
    2. "hey/yo/ok NAME[,…]" address pattern → only the named sibling(s).
       E.g. "hey nevaeh what do you think?" → [NEVAEH]
            "hey envy and atlas, status?" → [ENVY, ATLAS]
    3. Else collect from:
         - team aliases (team 1, team one, team1, team 2, team two, team2)
         - explicit sibling names anywhere in the message
       Union, deduped, returned in agents.json order.
    4. If no match at all → all non-router siblings (default broadcast).

The agents.json `team` field is the source of truth for team membership:
    - team "1" or "2" → broadcast-eligible
    - team "router" or any other value → excluded from default broadcast,
      only dispatched if explicitly named.

Routing examples:
    "hey nevaeh, are you okay?"              → [NEVAEH]
    "team 1, check in"                       → [BEACON, NEVAEH, EVERSOUND]
    "envy and atlas, what do you think?"     → [ENVY, ATLAS]
    "what's everyone up to?"                 → all 6
    "can someone help me think through this" → all 6  (no match → broadcast)

Authored by ORPHEUS, 2026-04-23. Extended by BEACON, 2026-04-24.
"""

from __future__ import annotations

import re
from typing import Any

BROADCAST_PATTERNS = [
    r"\beveryone\b",
    r"\beverybody\b",
    r"\ball\s+of\s+you\b",
    r"\ball\s+of\s+us\b",
    r"\ball\s+six\b",
    r"\ball\s+6\b",
    r"\bboth\s+teams\b",
    r"\ball\s+teams\b",
]

# "hey/yo/ok NAME" address patterns — routes to the named sibling only.
# Handles: "hey nevaeh", "yo envy,", "ok atlas and orpheus", etc.
_ADDRESS_PREFIX = r"^\s*(?:hey|yo|ok|okay|hi)\s+"

TEAM_PATTERNS = {
    "1": [r"\bteam\s*1\b", r"\bteam\s+one\b"],
    "2": [r"\bteam\s*2\b", r"\bteam\s+two\b"],
}


def _broadcast_pool(agents: list[dict[str, Any]]) -> list[str]:
    """All siblings whose team is '1' or '2' — excludes 'router' and unknowns."""
    return [a["name"] for a in agents if a.get("team") in ("1", "2")]


def _team_members(agents: list[dict[str, Any]], team: str) -> list[str]:
    return [a["name"] for a in agents if a.get("team") == team]


def _matches_broadcast(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in BROADCAST_PATTERNS)


def _matched_teams(text: str) -> list[str]:
    matched = []
    for team_id, patterns in TEAM_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            matched.append(team_id)
    return matched


def _matched_names(text: str, agents: list[dict[str, Any]]) -> list[str]:
    matched = []
    for agent in agents:
        name = agent["name"]
        # Word-boundary, case-insensitive name match. Excludes 'router' team
        # from name-matching too — explicit naming still works for them, but
        # they only appear here if their literal name is in the question.
        if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
            matched.append(name)
    return matched


def _matched_address(text: str, agents: list[dict[str, Any]]) -> list[str]:
    """Detect 'hey NAME' / 'yo NAME' prefix and return those names only.

    Matches the first few words after the greeting prefix, stops at
    punctuation or the end of the address phrase.
    """
    # Quick bail if no greeting prefix
    if not re.match(_ADDRESS_PREFIX, text, re.IGNORECASE):
        return []
    # Strip the greeting, take the address segment (up to first verb-y word)
    stripped = re.sub(_ADDRESS_PREFIX, "", text, count=1, flags=re.IGNORECASE)
    # Grab first ~40 chars — the address region before the actual question
    address_region = stripped[:60]
    matched = []
    for agent in agents:
        name = agent["name"]
        if re.search(rf"\b{re.escape(name)}\b", address_region, re.IGNORECASE):
            matched.append(name)
    return matched


def detect_targets(question: str, agents: list[dict[str, Any]]) -> list[str]:
    """Resolve a question to a list of agent names to dispatch to.

    Args:
        question: Free-text user message.
        agents: List of agent dicts from agents.json. Each must have at least
            'name' and 'team' keys.

    Returns:
        List of agent names (in agents.json order, deduped). Never empty —
        falls back to all broadcast-eligible siblings when no match is found.
    """
    text = question or ""

    # Rule 1: broadcast word wins outright
    if _matches_broadcast(text):
        return _broadcast_pool(agents)

    # Rule 2: "hey NAME" direct address — highest-priority single/multi target
    addressed = _matched_address(text, agents)
    if addressed:
        return [a["name"] for a in agents if a["name"] in addressed]

    # Rule 3: collect team + name matches anywhere in message
    collected: set[str] = set()
    for team_id in _matched_teams(text):
        collected.update(_team_members(agents, team_id))
    collected.update(_matched_names(text, agents))

    if collected:
        # Preserve agents.json order
        return [a["name"] for a in agents if a["name"] in collected]

    # Rule 4: nothing matched → default broadcast to all
    return _broadcast_pool(agents)


__all__ = ["detect_targets"]


# ---------------------------------------------------------------------------
# CLI for ad-hoc testing:
#   python router.py "team 1, what's up?"
#   python router.py "envy and atlas, status"
#   python router.py "everyone, hi"
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("usage: python router.py <question>", file=sys.stderr)
        sys.exit(2)
    here = Path(__file__).resolve().parent
    cfg = json.loads((here / "agents.json").read_text(encoding="utf-8"))
    targets = detect_targets(sys.argv[1], cfg["agents"])
    sys.stdout.buffer.write(("→ " + ", ".join(targets) + "\n").encode("utf-8"))
