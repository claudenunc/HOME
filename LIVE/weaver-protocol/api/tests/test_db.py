"""
Tests for db.py in-memory fallback path.
Runs without DATABASE_URL — no Postgres required.
"""
import os
import sys

# Ensure DATABASE_URL is absent so memory backend is used
os.environ.pop("DATABASE_URL", None)

# db.py lives in api/, not in the weaver package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db  # noqa: E402


def _make_session(session_id: str, disagreement: bool = False) -> dict:
    return {
        "session_id": session_id,
        "created_at": "2026-05-05T00:00:00Z",
        "prompt": "test prompt",
        "consensus": "acceptable",
        "disagreement_detected": disagreement,
        "observers": ["a", "b"],
        "provenance": {"a": "clean", "b": "clean"},
    }


def test_storage_backend_is_memory():
    assert db.storage_backend() == "memory"


def test_save_and_retrieve_session():
    db.save_session(_make_session("db-test-001"))
    result = db.get_session("db-test-001")
    assert result is not None
    assert result["session_id"] == "db-test-001"
    assert result["consensus"] == "acceptable"
    assert result["disagreement_detected"] is False


def test_get_missing_session_returns_none():
    assert db.get_session("does-not-exist-xyz") is None


def test_count_sessions_increments():
    before = db.count_sessions()
    db.save_session(_make_session("db-count-test-001"))
    assert db.count_sessions() == before + 1


def test_count_disagreements_increments():
    before = db.count_disagreements()
    db.save_session(_make_session("db-disagree-test-001", disagreement=True))
    assert db.count_disagreements() == before + 1


def test_disagreement_false_does_not_increment_disagreements():
    before = db.count_disagreements()
    db.save_session(_make_session("db-clean-test-001", disagreement=False))
    assert db.count_disagreements() == before


def test_save_and_validate_api_key():
    db.save_api_key("cus_test001", "wp_testkey001", "starter")
    result = db.validate_api_key("wp_testkey001")
    assert result is not None
    assert result["customer_id"] == "cus_test001"
    assert result["tier"] == "starter"


def test_validate_missing_key_returns_none():
    assert db.validate_api_key("wp_doesnotexist_xyz") is None


def test_revoke_customer_keys():
    db.save_api_key("cus_revoke001", "wp_revokekey001", "pro")
    assert db.validate_api_key("wp_revokekey001") is not None
    db.revoke_customer_keys("cus_revoke001")
    assert db.validate_api_key("wp_revokekey001") is None


def test_revoke_only_affects_target_customer():
    db.save_api_key("cus_a", "wp_key_a", "starter")
    db.save_api_key("cus_b", "wp_key_b", "pro")
    db.revoke_customer_keys("cus_a")
    # cus_a's key gone, cus_b's key still active
    assert db.validate_api_key("wp_key_a") is None
    assert db.validate_api_key("wp_key_b") is not None


def test_save_session_conflict_does_not_raise():
    record = _make_session("db-conflict-001")
    db.save_session(record)
    db.save_session(record)  # second save should not raise
    assert db.get_session("db-conflict-001") is not None
