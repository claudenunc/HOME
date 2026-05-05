"""
Weaver Protocol — Stripe Billing

Tier definitions, checkout session creation, and webhook event handling.
Issues and revokes API keys in response to subscription lifecycle events.

Environment variables required:
    STRIPE_SECRET_KEY          — Stripe secret key (sk_live_... or sk_test_...)
    STRIPE_WEBHOOK_SECRET      — Signing secret from Stripe dashboard webhook
    STRIPE_PRICE_STARTER       — Price ID for $49/mo Starter tier
    STRIPE_PRICE_PRO           — Price ID for $199/mo Pro tier
    STRIPE_PRICE_ENTERPRISE    — Price ID for $499/mo Enterprise tier
"""

import os
import secrets

import db as _db

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

PRICE_IDS: dict[str, str] = {
    "starter": os.environ.get("STRIPE_PRICE_STARTER", ""),
    "pro": os.environ.get("STRIPE_PRICE_PRO", ""),
    "enterprise": os.environ.get("STRIPE_PRICE_ENTERPRISE", ""),
}

TIER_LABELS: dict[str, str] = {
    "starter": "$49/mo — 500 verifications/mo",
    "pro": "$199/mo — 5,000 verifications/mo",
    "enterprise": "$499/mo — unlimited verifications + priority SLA",
}


def _stripe():
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY is not set")
    try:
        import stripe as _stripe_lib
    except ImportError as exc:
        raise RuntimeError("stripe package not installed — add 'stripe' to requirements.txt") from exc
    _stripe_lib.api_key = STRIPE_SECRET_KEY
    return _stripe_lib


def is_configured() -> bool:
    """True if Stripe env vars are present enough to serve billing endpoints."""
    return bool(STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET)


def create_checkout_session(tier: str, success_url: str, cancel_url: str) -> str:
    """Create a Stripe Checkout session. Returns the hosted checkout URL."""
    if tier not in PRICE_IDS:
        raise ValueError(f"Unknown tier '{tier}'. Valid: {list(PRICE_IDS)}")
    price_id = PRICE_IDS[tier]
    if not price_id:
        raise RuntimeError(f"STRIPE_PRICE_{tier.upper()} env var not set")

    stripe = _stripe()
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"weaver_tier": tier},
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Verify and process a Stripe webhook event.

    On checkout.session.completed  → issue API key, return it in response.
    On subscription deleted/paused → revoke all keys for that customer.

    Raises ValueError on invalid signature (caller should return 400).
    """
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not set")

    stripe = _stripe()
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise ValueError(f"Webhook signature invalid: {exc}") from exc

    event_type: str = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id: str = session["customer"]
        tier: str = session.get("metadata", {}).get("weaver_tier", "starter")
        _issue_api_key(customer_id, tier)
        # Key stored in DB only — Stripe logs webhook responses, never return credentials here
        return {"action": "key_issued", "customer_id": customer_id, "tier": tier}

    if event_type in ("customer.subscription.deleted", "customer.subscription.paused"):
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        _db.revoke_customer_keys(customer_id)
        return {"action": "keys_revoked", "customer_id": customer_id}

    return {"action": "ignored", "event_type": event_type}


def _issue_api_key(customer_id: str, tier: str) -> str:
    # Idempotency: return existing key if one already exists for this customer+tier.
    # Prevents duplicate keys when Stripe retries the webhook on transient errors.
    existing = _db.get_active_key_for_customer(customer_id, tier)
    if existing:
        return existing
    api_key = f"wp_{secrets.token_urlsafe(32)}"
    _db.save_api_key(customer_id, api_key, tier)
    return api_key
