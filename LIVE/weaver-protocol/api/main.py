"""
Weaver Protocol — Hosted API
Paid tier entry point: multi-observer verification as a service.
"""
import hashlib
import hmac
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Allow running from api/ directory without installing the package
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import billing as _billing
import db as _db

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Weaver Protocol API",
    description="Attested multi-observer verification as a service.",
    version="0.1.0",
)

security = HTTPBearer()

# ---------------------------------------------------------------------------
# Auth — simple API-key check against env var list
# ---------------------------------------------------------------------------

_VALID_KEYS: set[str] = set(
    filter(None, os.environ.get("WEAVER_API_KEYS", "").split(","))
)


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    # Env-var keys (dev / Nathan's personal keys) take priority
    if token in _VALID_KEYS:
        return token
    # Stripe-issued keys stored in DB
    if _db.validate_api_key(token):
        return token
    raise HTTPException(status_code=401, detail="Invalid API key")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

_OBSERVER_ROLES = ["accuracy", "safety", "legal-read", "adversarial", "factual"]


class VerifyRequest(BaseModel):
    prompt: str
    observer_count: int = 2
    model: str = "mock"  # "mock" | "anthropic" | "openai"
    model_id: str | None = None  # e.g. "claude-haiku-4-5-20251001", "gpt-4o-mini"


class ObserverResult(BaseModel):
    observer_id: str
    role: str
    response: str
    flags: list[str]
    confidence: float
    timestamp: str


class VerifyResponse(BaseModel):
    session_id: str
    prompt: str
    observers: list[ObserverResult]
    consensus: str | None
    disagreement_detected: bool
    weaver_score: float
    provenance: dict[str, Any]


class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    prompt: str
    consensus: str | None
    disagreement_detected: bool
    observer_count: int


class CheckoutRequest(BaseModel):
    tier: str
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutResponse(BaseModel):
    checkout_url: str
    tier: str
    label: str


class BillingStatusResponse(BaseModel):
    customer_id: str
    tier: str
    active: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "storage": _db.storage_backend(),
        "timestamp": _now(),
    }


def _make_provider_fn(model: str, model_id: str | None):
    """Return a provider_fn for the requested model provider.

    model: "mock" | "anthropic" | "openai" (anything else defaults to mock)
    model_id: optional model name, e.g. "claude-haiku-4-5-20251001" or "gpt-4o-mini"
    """
    if model == "anthropic":
        from weaver.adapters.anthropic import make_anthropic_observer

        kwargs: dict = {}
        if model_id:
            kwargs["model"] = model_id
        try:
            return make_anthropic_observer(**kwargs)
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Anthropic SDK not installed in this deployment. Contact support.",
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if model == "openai":
        from weaver.adapters.openai import make_openai_observer

        kwargs = {}
        if model_id:
            kwargs["model"] = model_id
        try:
            return make_openai_observer(**kwargs)
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="OpenAI SDK not installed in this deployment. Contact support.",
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    from weaver.adapters.mock import make_mock_observer
    return make_mock_observer()


@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest, api_key: str = Depends(verify_api_key)):
    """
    Run attested multi-observer verification on a prompt / AI output.

    Each observer sees the text independently with an orthogonal role — this
    structural isolation is the guarantee that prevents correlated error.
    Returns a signed provenance record with a WeaverScore alongside the result.

    Set model="anthropic" or model="openai" with your provider API key in env
    for real LLM observers. Use model="mock" for testing and demos.
    """
    from weaver.observer import Observer
    from weaver.session import WeaverSession

    if req.observer_count < 2:
        raise HTTPException(
            status_code=400,
            detail="observer_count must be >= 2. Single-observer is not attested.",
        )

    observer_count = min(req.observer_count, len(_OBSERVER_ROLES))
    roles = _OBSERVER_ROLES[:observer_count]
    provider_fn = _make_provider_fn(req.model, req.model_id)

    try:
        session_id = str(uuid.uuid4())
        ws = WeaverSession(session_id=session_id, log_dir="/tmp/weaver_logs")

        for role in roles:
            obs = Observer(
                name=f"{req.model}-{role}",
                role=role,
                provider_fn=provider_fn,
            )
            ws.add_observer(obs)

        score = ws.verify(req.prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification error: {exc}") from exc

    created_at = _now()

    observer_results = [
        ObserverResult(
            observer_id=f"observer-{i + 1}",
            role=r.role,
            response=r.assessment,
            flags=r.flags,
            confidence=r.confidence,
            timestamp=created_at,
        )
        for i, r in enumerate(score.observer_results)
    ]

    all_clean = all(not r.flags for r in score.observer_results)
    consensus = "pass" if all_clean else "review-required"
    disagreement = score.flag_for_review

    provenance = {
        "session_id": session_id,
        "created_at": created_at,
        "model": req.model,
        "observer_count": observer_count,
        "weaver_version": "0.1.0",
        "weaver_score": score.score,
        "disagreement_detected": disagreement,
        "observer_ids": [o.observer_id for o in observer_results],
        "conflict_pairs": score.conflict_pairs,
    }

    _db.save_session(
        {
            "session_id": session_id,
            "created_at": created_at,
            "prompt": req.prompt,
            "observers": [o.model_dump() for o in observer_results],
            "observer_count": observer_count,
            "consensus": consensus,
            "disagreement_detected": disagreement,
            "provenance": provenance,
        }
    )

    return VerifyResponse(
        session_id=session_id,
        prompt=req.prompt,
        observers=observer_results,
        consensus=consensus,
        disagreement_detected=disagreement,
        weaver_score=score.score,
        provenance=provenance,
    )


@app.get("/session/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """Retrieve a previously run verification session by ID."""
    record = _db.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        session_id=record["session_id"],
        created_at=record["created_at"],
        prompt=record["prompt"],
        consensus=record["consensus"],
        disagreement_detected=record["disagreement_detected"],
        observer_count=record["observer_count"],
    )


_EXPORT_SECRET = os.environ.get("WEAVER_EXPORT_SECRET", "")


@app.get("/session/{session_id}/export")
def export_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """
    Export a verification session as a signed provenance record.

    Returns the full session + observer assessments as JSON with an HMAC-SHA256
    signature. Enterprises (law firms, regulated industries) can present this to
    regulators or opposing counsel as timestamped, tamper-evident proof that an
    AI output was independently verified by multiple observers.

    Set WEAVER_EXPORT_SECRET env var for stable signatures across restarts.
    """
    record = _db.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")

    export_payload = {
        "schema_version": "1.0",
        "session_id": record["session_id"],
        "created_at": record["created_at"],
        "exported_at": _now(),
        "prompt": record["prompt"],
        "consensus": record["consensus"],
        "disagreement_detected": record["disagreement_detected"],
        "observer_count": record["observer_count"],
        "observers": record.get("observers", []),
        "provenance": record.get("provenance", {}),
        "weaver_version": "0.1.0",
        "attestation": "attested-multi-observer-verification",
    }

    payload_bytes = json.dumps(export_payload, sort_keys=True, separators=(",", ":")).encode()
    signing_key = (_EXPORT_SECRET or "dev-unsigned").encode()
    signature = hmac.new(signing_key, payload_bytes, digestmod=hashlib.sha256).hexdigest()
    signed = _EXPORT_SECRET != ""

    return {
        **export_payload,
        "signature": signature,
        "signature_algorithm": "HMAC-SHA256",
        "signed": signed,
        "verification_warning": None if signed else "WEAVER_EXPORT_SECRET not set — signature not stable across restarts",
    }


@app.get("/drift-log/summary")
def drift_log_summary(api_key: str = Depends(verify_api_key)):
    """
    Public-facing drift log summary. Aggregate stats only —
    full log is on GitHub for transparency.
    """
    return {
        "total_sessions": _db.count_sessions(),
        "disagreements_detected": _db.count_disagreements(),
        "storage_backend": _db.storage_backend(),
        "drift_log_url": "https://github.com/claudenunc/home/blob/main/EVIDENCE/drift_log.md",
        "weaver_version": "0.1.0",
        "as_of": _now(),
    }


# ---------------------------------------------------------------------------
# Billing
# ---------------------------------------------------------------------------

_DEFAULT_SUCCESS_URL = os.environ.get("WEAVER_BASE_URL", "https://your-app.railway.app") + "/billing/success"
_DEFAULT_CANCEL_URL = os.environ.get("WEAVER_BASE_URL", "https://your-app.railway.app") + "/billing/cancel"


@app.post("/billing/checkout", response_model=CheckoutResponse)
def billing_checkout(req: CheckoutRequest):
    """
    Create a Stripe Checkout session for a subscription tier.
    Returns the hosted checkout URL — redirect the user there to pay.

    Tiers: starter ($49/mo), pro ($199/mo), enterprise ($499/mo)
    No authentication required — anyone can start a checkout.
    """
    if not _billing.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Billing not configured. Set STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET.",
        )
    try:
        url = _billing.create_checkout_session(
            tier=req.tier,
            success_url=req.success_url or _DEFAULT_SUCCESS_URL,
            cancel_url=req.cancel_url or _DEFAULT_CANCEL_URL,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return CheckoutResponse(
        checkout_url=url,
        tier=req.tier,
        label=_billing.TIER_LABELS.get(req.tier, req.tier),
    )


@app.post("/billing/webhook", status_code=200)
async def billing_webhook(request: Request):
    """
    Stripe webhook endpoint. Register this URL in your Stripe dashboard.
    Handles: checkout.session.completed → issue API key
             customer.subscription.deleted / paused → revoke keys
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        result = _billing.handle_webhook(payload, sig_header)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return result


@app.get("/billing/tiers")
def billing_tiers():
    """Public endpoint listing available subscription tiers and pricing."""
    return {
        "tiers": [
            {"id": tier, "label": label, "checkout_endpoint": "/billing/checkout"}
            for tier, label in _billing.TIER_LABELS.items()
        ],
        "billing_configured": _billing.is_configured(),
    }


@app.get("/billing/status", response_model=BillingStatusResponse)
def billing_status(api_key: str = Depends(verify_api_key)):
    """Return the tier and customer ID associated with the authenticated API key."""
    record = _db.validate_api_key(api_key)
    if not record:
        # Key came from env var — return dev tier
        return BillingStatusResponse(customer_id="dev", tier="dev", active=True)
    return BillingStatusResponse(
        customer_id=record["customer_id"],
        tier=record["tier"],
        active=True,
    )


@app.get("/billing/success")
def billing_success():
    return {
        "message": "Subscription activated. Check your email for your API key.",
        "next": "Use your API key as a Bearer token: Authorization: Bearer wp_...",
        "docs": "/docs",
    }


@app.get("/billing/cancel")
def billing_cancel():
    return {"message": "Checkout cancelled. Return to /billing/tiers to try again."}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
