"""
Tests for billing.py logic that does not require live Stripe credentials.
Covers is_configured(), tier definitions, and API key issuance via in-memory db.
"""
import os
import sys

# Remove Stripe env vars to test unconfigured path
os.environ.pop("STRIPE_SECRET_KEY", None)
os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
os.environ.pop("DATABASE_URL", None)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import billing  # noqa: E402
import db       # noqa: E402


def test_is_configured_without_keys():
    assert billing.is_configured() is False


def test_is_configured_with_both_keys(monkeypatch):
    monkeypatch.setattr(billing, "STRIPE_SECRET_KEY", "sk_test_xxx")
    monkeypatch.setattr(billing, "STRIPE_WEBHOOK_SECRET", "whsec_xxx")
    assert billing.is_configured() is True


def test_tier_labels_present():
    for tier in ("starter", "pro", "enterprise"):
        assert tier in billing.TIER_LABELS
        assert "$" in billing.TIER_LABELS[tier]


def test_price_ids_keys_match_tier_labels():
    assert set(billing.PRICE_IDS.keys()) == set(billing.TIER_LABELS.keys())


def test_issue_api_key_format():
    key = billing._issue_api_key("cus_billing_test001", "starter")
    assert key.startswith("wp_")
    assert len(key) > 20


def test_issue_api_key_persists_to_db():
    key = billing._issue_api_key("cus_billing_test002", "pro")
    result = db.validate_api_key(key)
    assert result is not None
    assert result["customer_id"] == "cus_billing_test002"
    assert result["tier"] == "pro"


def test_checkout_session_requires_env_config(monkeypatch):
    import pytest
    # Price ID missing → RuntimeError before Stripe key is checked
    with pytest.raises(RuntimeError, match="STRIPE_PRICE_STARTER"):
        billing.create_checkout_session("starter", "https://example.com/ok", "https://example.com/cancel")

    # Price ID present but no Stripe key → RuntimeError on Stripe call
    monkeypatch.setitem(billing.PRICE_IDS, "starter", "price_test_xxx")
    with pytest.raises(RuntimeError, match="STRIPE_SECRET_KEY"):
        billing.create_checkout_session("starter", "https://example.com/ok", "https://example.com/cancel")


def test_checkout_session_unknown_tier():
    import pytest
    with pytest.raises(ValueError, match="Unknown tier"):
        billing.create_checkout_session("legendary", "https://x.com/ok", "https://x.com/cancel")


def test_webhook_requires_secret():
    import pytest
    with pytest.raises(RuntimeError, match="STRIPE_WEBHOOK_SECRET"):
        billing.handle_webhook(b"payload", "sig_header")
