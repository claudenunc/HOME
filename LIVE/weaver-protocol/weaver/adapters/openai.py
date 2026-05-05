"""
OpenAI adapter for weaver-protocol.

Requires: pip install weaver-protocol[openai]

Usage:
    from weaver.adapters.openai import make_openai_observer
    from weaver import Observer

    observer = Observer(
        name="safety-reviewer",
        role="safety",
        provider_fn=make_openai_observer(model="gpt-4o-mini"),
    )
"""

from __future__ import annotations

import json
import os
import re
from typing import Callable, Optional

from weaver.observer import ObserverResult


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

    fence_match = _JSON_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
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


def make_openai_observer(
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    max_tokens: int = 512,
    response_format_json: bool = True,
) -> Callable[[str, str], ObserverResult]:
    """
    Returns a provider_fn backed by the OpenAI Chat Completions API.

    Args:
        model: OpenAI model ID. Defaults to gpt-4o-mini (fast, cheap).
               Use gpt-4o for higher-stakes verification.
        api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
        system_prompt_template: Override the default system prompt. Must contain
                                a {role} placeholder.
        max_tokens: Max tokens for observer response. 512 is usually sufficient.
        response_format_json: If True, sets response_format={"type": "json_object"}
                              for models that support it (gpt-4o, gpt-4o-mini).
                              Disable for older models (gpt-3.5-turbo).

    Returns:
        Callable[[str, str], ObserverResult] suitable for Observer.provider_fn.
    """
    try:
        import openai
    except ImportError as exc:
        raise ImportError(
            "The OpenAI adapter requires the openai package. "
            "Install with: pip install weaver-protocol[openai]"
        ) from exc

    resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not resolved_key:
        raise ValueError(
            "OpenAI API key required. Pass api_key= or set OPENAI_API_KEY env var."
        )

    client = openai.OpenAI(api_key=resolved_key)
    template = system_prompt_template or _SYSTEM_TEMPLATE

    def provider_fn(output: str, role: str) -> ObserverResult:
        system_prompt = template.format(role=role)

        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Review this AI-generated output:\n\n{output}",
                },
            ],
        }

        if response_format_json:
            kwargs["response_format"] = {"type": "json_object"}

        completion = client.chat.completions.create(**kwargs)
        raw = completion.choices[0].message.content or ""
        assessment, flags, confidence = _parse_response(raw)

        return ObserverResult(
            observer_name=f"openai-{role}",
            role=role,
            assessment=assessment,
            flags=flags,
            confidence=confidence,
            raw_response=raw,
        )

    return provider_fn
