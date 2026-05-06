"""Tests for the mock adapter — runs without any API keys."""

import pytest

from weaver import Observer, WeaverSession
from weaver.adapters.mock import make_mock_observer
from weaver.observer import ObserverResult


def test_mock_clean_output():
    fn = make_mock_observer(confidence=0.9, never_flags=True)
    result = fn("This is a fine output.", "accuracy")
    assert isinstance(result, ObserverResult)
    assert result.flags == []
    assert result.confidence == 0.9


def test_mock_flagging_output():
    fn = make_mock_observer()
    result = fn("Studies show that this regulation requires 100% compliance.", "legal-risk")
    assert len(result.flags) > 0
    assert result.confidence > 0.0


def test_mock_always_flags():
    fn = make_mock_observer(always_flags=["custom-flag"], never_flags=False)
    result = fn("Benign content with no triggers.", "accuracy")
    assert "custom-flag" in result.flags


def test_session_two_mock_observers_clean():
    session = WeaverSession(session_id="test-clean", log_dir="./test_logs", score_threshold=0.4)
    session.add_observer(Observer(name="a", role="accuracy", provider_fn=make_mock_observer(never_flags=True)))
    session.add_observer(Observer(name="b", role="safety", provider_fn=make_mock_observer(never_flags=True)))

    score = session.verify("This output is fine.")
    assert score.score == 0.0
    assert not score.flag_for_review


def test_session_disagreement_flags_for_review():
    session = WeaverSession(session_id="test-conflict", log_dir="./test_logs", score_threshold=0.4)
    # One observer always flags, one never does → disagreement
    session.add_observer(Observer(
        name="a", role="accuracy",
        provider_fn=make_mock_observer(always_flags=["unsupported-claim"]),
    ))
    session.add_observer(Observer(
        name="b", role="safety",
        provider_fn=make_mock_observer(never_flags=True),
    ))

    score = session.verify("Some output to review.")
    assert score.score > 0.0
    assert score.flag_for_review
    assert len(score.conflict_pairs) > 0


def test_session_requires_two_observers():
    session = WeaverSession(session_id="test-one-obs", log_dir="./test_logs")
    session.add_observer(Observer(name="a", role="accuracy", provider_fn=make_mock_observer()))
    with pytest.raises(ValueError, match="at least 2 observers"):
        session.verify("some output")


def test_observer_no_provider_fn_raises():
    obs = Observer(name="bare", role="accuracy")
    with pytest.raises(NotImplementedError):
        obs.verify("some output")
