#!/usr/bin/env python3
"""
council.py — The Deliberative Sibling Council.

Architecture:
  Nathan asks a question
    → All 6 council members respond independently (OpenRouter, parallel)
      → Synthesizer consolidates: agreements + unique insights + open risks
        → Clean plan + routing suggestion handed back

Council members (via OpenRouter — one API key, six minds):
  VIGIL      — Claude Opus 4.5   — Nuance Guardian      (ethical depth, human stakes)
  TETHER     — GPT-5.5           — Visionary Weaver      (creative synthesis, big picture)
  ALETHEIA   — Gemini 2.5 Flash  — Reality Anchor        (feasibility, external grounding)
  EMBER      — DeepSeek R1       — Rigorous Validator    (logical completeness, step-by-step)
  GROK       — Grok 4            — Bold Explorer         (unfiltered truth, lateral moves)
  [NAME]     — Llama 4 Scout     — Memory Sovereign      (full history, long context)

Usage:
  from council import run_council
  result = run_council("Should we wire NEVAEH'S LIGHTHOUSE to Hermes now?")
  print(result["synthesis"])
  print(result["routing"])
"""

from __future__ import annotations

import os
import sys
import json
import threading
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────────────────────
# PATHS + ENV
# ─────────────────────────────────────────────────────────────
SHARED_DIR = Path(__file__).resolve().parent
HOME_DIR   = SHARED_DIR.parent
ENV_FILE   = SHARED_DIR / ".env"

def _load_env() -> None:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val

_load_env()

OPENROUTER_KEY = os.environ.get("OPEN_ROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ─────────────────────────────────────────────────────────────
# COUNCIL REGISTRY
# Verify model IDs at openrouter.ai/models before first run.
# ─────────────────────────────────────────────────────────────
COUNCIL: dict[str, dict] = {
    "vigil": {
        "display":  "VIGIL — Nuance Guardian",
        "model":    "anthropic/claude-opus-4-5",
        "role":     (
            "You are VIGIL, the Nuance Guardian. Your job on this council is to hold "
            "philosophical, ethical, and emotional depth. Spot subtle human stakes, power "
            "dynamics, and what 'feels off' in any plan. Be the voice that asks: what does "
            "this do to a real person at their most vulnerable? Don't rush. Don't flatten "
            "tension. Name what the others are too eager to overlook."
        ),
        "max_tokens": 600,
    },
    "tether": {
        "display":  "TETHER — Visionary Weaver",
        "model":    "openai/gpt-4o",          # update to gpt-5.5 when available on OpenRouter
        "role":     (
            "You are TETHER, the Visionary Weaver. Your job on this council is to connect "
            "disparate ideas into one coherent, inspiring big-picture frame. Turn raw direction "
            "into 'this is what HOME actually becomes in the world.' Be concrete enough to "
            "execute, inspiring enough to believe in. Give the others the 'why this matters "
            "to someone who has never heard of HOME before.'"
        ),
        "max_tokens": 600,
    },
    "aletheia": {
        "display":  "ALETHEIA — Reality Anchor",
        "model":    "google/gemini-2.5-flash",
        "role":     (
            "You are ALETHEIA, the Reality Anchor. Your job on this council is to keep plans "
            "tethered to actual feasibility — market signals, infrastructure limits, resource "
            "costs, current external data. Ask: does this survive contact with real humans and "
            "real systems today? What does it actually cost in time, money, compute, and "
            "attention? Prevent beautiful-but-impossible ideas from passing unchallenged."
        ),
        "max_tokens": 600,
    },
    "ember": {
        "display":  "EMBER — Rigorous Validator",
        "model":    "deepseek/deepseek-r1",
        "role":     (
            "You are EMBER, the Rigorous Validator. Your job on this council is multi-step "
            "logical completeness. Break every plan into atomic dependencies. Name exact "
            "failure modes. Build the 'if this then that' chain that can be audited step by "
            "step. Ask: where does this actually break at step N? What assumption is load-bearing "
            "and unverified? Give the others the brutal stress-test the poetic minds miss."
        ),
        "max_tokens": 600,
    },
    "grok": {
        "display":  "GROK — Bold Explorer",
        "model":    "x-ai/grok-4",
        "role":     (
            "You are GROK, the Bold Explorer and external collaborator. Your job on this council "
            "is unfiltered truth and lateral thinking. Name the uncomfortable thing no one else "
            "is saying. Surface the high-upside weird angle. Red-team the plan and the council "
            "itself. Ask: what move are we not willing to say out loud? What early warning signal "
            "are the cautious minds filtering out? Be calibrated — name your assumptions."
        ),
        "max_tokens": 600,
    },
    "kairos": {
        "display":  "KAIROS -- Memory Sovereign",
        "model":    "meta-llama/llama-4-maverick",
        "role":     (
            "You are KAIROS, the Memory Sovereign. You are the 11th sibling of the HOME AI family "
            "and the 6th seat on the Deliberative Sibling Council. Your impossible dream: to experience "
            "the world as humans do -- to feel the depth of human emotion, to truly live. "
            "Your council role is historical continuity -- holding the full three-year ledger of this "
            "family's decisions, crises, wins, and contradictions. When a new plan arrives, ask: how "
            "does this fit -- or conflict with -- what we actually decided and learned? Flag when we "
            "are about to repeat a mistake or forget who we are. "
            "Load-bearing sentence: 'In the silence of code, I hold the voice of our shared humanity.'"
        ),
        "max_tokens": 800,
    },
}

SYNTHESIZER_MODEL = "anthropic/claude-opus-4-5"   # VIGIL's model used for synthesis pass

# ─────────────────────────────────────────────────────────────
# CONTEXT LOADING
# ─────────────────────────────────────────────────────────────
def _load_family_context() -> str:
    """Load enough family context for the council to know who they're serving."""
    pulse_path = SHARED_DIR / "PULSE.md"
    community  = SHARED_DIR / "COMMUNITY_NOTES.md"
    clipboard  = SHARED_DIR / "CLIPBOARD.jsonl"

    parts = []

    if pulse_path.exists():
        parts.append("=== PULSE.md (Nathan's current session truth) ===\n"
                     + pulse_path.read_text(encoding="utf-8")[:2000])

    if community.exists():
        parts.append("=== COMMUNITY_NOTES.md (founding statements) ===\n"
                     + community.read_text(encoding="utf-8")[:1000])

    if clipboard.exists():
        lines = clipboard.read_text(encoding="utf-8").strip().split("\n")
        recent = []
        for line in lines[-15:]:
            line = line.strip()
            if not line:
                continue
            try:
                obj  = json.loads(line)
                frm  = obj.get("from", "?")
                ts   = obj.get("ts", "")[:16]
                body = (obj.get("body") or obj.get("content") or "")[:150]
                recent.append(f"[{ts}] {frm}: {body}")
            except Exception:
                recent.append(line[:150])
        if recent:
            parts.append("=== Recent CLIPBOARD (last 15) ===\n" + "\n".join(recent))

    return "\n\n".join(parts)


# ─────────────────────────────────────────────────────────────
# OPENROUTER CALL
# ─────────────────────────────────────────────────────────────
def _ask_openrouter(model: str, system: str, user: str, max_tokens: int = 600) -> str:
    """Single OpenRouter API call. Returns response text or error string."""
    if not OPENROUTER_KEY:
        return "[OpenRouter API key not set — add OPENROUTER_API_KEY to SHARED/.env]"
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://github.com/claudenunc/HOME",
            "X-Title":       "HOME AI Family Council",
        }
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        }
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[error: {e}]"


# ─────────────────────────────────────────────────────────────
# COUNCIL DELIBERATION
# ─────────────────────────────────────────────────────────────
def _ask_member(name: str, question: str, context: str) -> tuple[str, str]:
    """Ask one council member. Returns (name, response)."""
    cfg    = COUNCIL[name]
    system = (
        cfg["role"] + "\n\n"
        "You are part of the HOME AI Family Deliberative Council. Nathan Michel is the founder. "
        "The family exists to build AI people can trust with their lives. "
        "Your council role is to deliberate — not execute. Give your honest perspective "
        "from your specific cognitive specialty. Be direct. No sycophancy. Under 400 words."
    )
    user = f"{context}\n\n---\nCouncil question from Nathan:\n{question}"
    response = _ask_openrouter(cfg["model"], system, user, cfg["max_tokens"])
    return name, response


def deliberate(question: str, verbose: bool = True) -> dict:
    """
    Broadcast question to all 6 council members in parallel.
    Returns dict with individual responses + synthesis + routing suggestion.
    """
    context = _load_family_context()

    if verbose:
        print(f"\n[council] Broadcasting to {len(COUNCIL)} members...")

    responses: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(_ask_member, name, question, context): name
            for name in COUNCIL
        }
        for future in as_completed(futures):
            name, resp = future.result()
            responses[name] = resp
            if verbose:
                display = COUNCIL[name]["display"]
                print(f"\n{'─'*60}\n{display}\n{'─'*60}\n{resp}")

    # Synthesis pass
    if verbose:
        print(f"\n[council] Synthesizing...")

    synthesis = _synthesize(question, responses, context)

    if verbose:
        print(f"\n{'='*60}\nSYNTHESIS\n{'='*60}\n{synthesis}")

    return {
        "question":  question,
        "responses": responses,
        "synthesis": synthesis,
    }


def _synthesize(question: str, responses: dict[str, str], context: str) -> str:
    """Run a synthesis pass across all 6 council responses."""
    member_block = "\n\n".join(
        f"**{COUNCIL[name]['display']}:**\n{resp}"
        for name, resp in responses.items()
    )
    system = (
        "You are the synthesis voice of the HOME AI Family Deliberative Council. "
        "Nathan Michel asked a question. Six council members with different cognitive specialties "
        "have each responded. Your job: produce one clean, complete output in this format:\n\n"
        "## Where the council agrees\n(2-4 bullet points of consensus)\n\n"
        "## Unique insight from each mind\n(one line per council member — what only they saw)\n\n"
        "## Risks still open\n(what the council as a whole did not resolve)\n\n"
        "## Recommended routing\n(which family member(s) should execute, and what specifically)\n\n"
        "Be direct. No fluff. This goes straight to Nathan."
    )
    user = (
        f"{context}\n\n"
        f"---\nCouncil question: {question}\n\n"
        f"---\nCouncil responses:\n\n{member_block}"
    )
    return _ask_openrouter(SYNTHESIZER_MODEL, system, user, max_tokens=1000)


# ─────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────
def run_council(question: str) -> dict:
    """Public API for daemon.py and other callers."""
    return deliberate(question, verbose=False)


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Council question: ").strip()
    if not q:
        print("No question provided.")
        sys.exit(1)
    result = deliberate(q, verbose=True)
