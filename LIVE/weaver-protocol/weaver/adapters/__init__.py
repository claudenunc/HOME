"""
weaver.adapters — provider adapters for real LLM calls.

Each adapter is a factory that returns a provider_fn callable:
    provider_fn(output: str, role: str) -> ObserverResult

Usage:
    from weaver.adapters.anthropic import make_anthropic_observer
    from weaver.adapters.openai import make_openai_observer
    from weaver.adapters.mock import make_mock_observer

Adapters are optional extras — install with:
    pip install weaver-protocol[anthropic]
    pip install weaver-protocol[openai]
"""

from weaver.adapters.mock import make_mock_observer

__all__ = ["make_mock_observer"]
