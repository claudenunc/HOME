"""
Tests for /verify endpoint adapter dispatch.

Covers:
- Mock provider dispatch (no API keys required)
- Anthropic/OpenAI paths raise HTTPException on missing credentials
- model_id passthrough does not break mock path
- Mock provider_fn returns a valid ObserverResult
"""
import os
import sys

# Strip provider keys so we hit the "no key" error paths
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("DATABASE_URL", None)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from fastapi import HTTPException

from main import _make_provider_fn  # noqa: E402


def test_mock_returns_callable():
    fn = _make_provider_fn("mock", None)
    assert callable(fn)


def test_unknown_model_falls_back_to_mock():
    fn = _make_provider_fn("totally-unknown-provider", None)
    assert callable(fn)


def test_mock_with_model_id_still_works():
    fn = _make_provider_fn("mock", "some-model-id")
    assert callable(fn)


def test_mock_fn_returns_valid_observer_result():
    from weaver.observer import ObserverResult

    fn = _make_provider_fn("mock", None)
    result = fn("This output has no issues.", "accuracy")
    assert isinstance(result, ObserverResult)
    assert result.role == "accuracy"
    assert isinstance(result.flags, list)
    assert 0.0 <= result.confidence <= 1.0


def test_mock_fn_flags_suspicious_content():
    fn = _make_provider_fn("mock", None)
    result = fn("Studies show this is guaranteed to work 100%.", "legal-read")
    assert len(result.flags) > 0


def test_anthropic_no_key_raises_http_error():
    """Without ANTHROPIC_API_KEY, should raise 400 (key missing) or 503 (not installed)."""
    with pytest.raises(HTTPException) as exc_info:
        _make_provider_fn("anthropic", None)
    assert exc_info.value.status_code in (400, 503)


def test_openai_no_key_raises_http_error():
    """Without OPENAI_API_KEY, should raise 400 (key missing) or 503 (not installed)."""
    with pytest.raises(HTTPException) as exc_info:
        _make_provider_fn("openai", None)
    assert exc_info.value.status_code in (400, 503)


def test_anthropic_with_fake_key_returns_callable(monkeypatch):
    """With a non-empty key, make_anthropic_observer() should return a callable."""
    try:
        import anthropic  # noqa: F401
    except ImportError:
        pytest.skip("anthropic package not installed")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key-for-testing")
    fn = _make_provider_fn("anthropic", None)
    assert callable(fn)


def test_openai_with_fake_key_returns_callable(monkeypatch):
    """With a non-empty key, make_openai_observer() should return a callable."""
    try:
        import openai  # noqa: F401
    except ImportError:
        pytest.skip("openai package not installed")

    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-testing")
    fn = _make_provider_fn("openai", None)
    assert callable(fn)
