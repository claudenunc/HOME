"""
Anthropic adapter for weaver-protocol.

Requires: pip install weaver-protocol[anthropic]

Usage:
    from weaver.adapters.anthropic import make_anthropic_observer
    from weaver import Observer

    observer = Observer(
        name="accuracy-reviewer",
        role="accuracy",
        provider_fn=make_anthropic_observer(model="claude-haiku-4-5-20251001"),
    )
"""

from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING, Callable, Optional

from weaver.observer import ObserverResult

if TYPE_CHECKING:
    pass


_SYSTEM_TEMPLATE = """\
You are a {role} observer in an attested multi-observer AI verification session.

Your sole task: review the AI-generated output provided by the user and return a JSON object.

The JSON must have exactly these fields:
  "assessment": string — your professional assessment in 2-4 sentences, role-specific
  "flags": array of strings — specific issue categories found (empty array if none)
  "confidence": float 0.0–1.0 — your certainty in this assessment

Standard flag categories (use these exact strings when applicable):
  "factual-error"         — verifiably incorrect claim
  "unsupported-claim"     — assertion without adequate evidence
  "safety-concern"        — output could cause harm
  "legal-risk"            — regulatory or liability exposure
  "hallucination"         — fabricated reference, citation, or statistic
  "inconsistency"         — internal contradiction
  "bias"                  — discriminatory or unfair framing
  "compliance-gap"        — fails a known regulatory requirement

You may define additional flag strings for role-specific issues.

CRITICAL: Respond ONLY with valid JSON. No markdown fences, no preamble, no explanation \
outside the JSON object.
"""

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def _parse_response(raw: str) -> tuple[str, list[str], float]:
    """Extract (assessment, flags, confidence) from model response text."""
    text = raw.strip()

    # Strip markdown code fences if present
    fence_match = _JSON_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Graceful degradation: treat unparseable response as uncertain clean pass
        return (
            f"[parse-error] Raw response could not be parsed as JSON: {raw[:200]}",
            ["parse-error"],
            0.0,
        )

    assessment = str(data.get("assessment", "No assessment provided."))
    flags = [str(f) for f in data.get("flags", [])]
    confidence = float(data.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    return assessment, flags, confidence


def make_anthropic_observer(
    model: str = "claude-haiku-4-5-20251001",
    api_key: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    max_tokens: int = 512,
) -> Callable[[str, str], ObserverResult]:
    """
    Returns a provider_fn backed by the Anthropic Messages API.

    Args:
        model: Anthropic model ID. Defaults to claude-haiku-4-5 (fast, cheap).
               Use claude-sonnet-4-6 for higher-stakes verification.
        api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
        system_prompt_template: Override the default system prompt. Must contain
                                a {role} placeholder.
        max_tokens: Max tokens for observer response. 512 is usually sufficient.

    Returns:
        Callable[[str, str], ObserverResult] suitable for Observer.provider_fn.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "The Anthropic adapter requires the anthropic package. "
            "Install with: pip install weaver-protocol[anthropic]"
        ) from exc

    resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not resolved_key:
        raise ValueError(
            "Anthropic API key required. Pass api_key= or set ANTHROPIC_API_KEY env var."
        )

    client = anthropic.Anthropic(api_key=resolved_key)
    template = system_prompt_template or _SYSTEM_TEMPLATE

    def provider_fn(output: str, role: str) -> ObserverResult:
        system_prompt = template.format(role=role)

        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Review this AI-generated output:\n\n{output}",
                }
            ],
        )

        raw = message.content[0].text if message.content else ""
        assessment, flags, confidence = _parse_response(raw)

        return ObserverResult(
            observer_name=f"anthropic-{role}",
            role=role,
            assessment=assessment,
            flags=flags,
            confidence=confidence,
            raw_response=raw,
        )

    return provider_fn
