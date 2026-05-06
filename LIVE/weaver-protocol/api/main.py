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

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Security
from fastapi.responses import HTMLResponse
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


_LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weaver Protocol — Attested Multi-Observer AI Verification</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,-apple-system,sans-serif;background:#0a0a0a;color:#e2e2e2;line-height:1.6}
  .hero{max-width:800px;margin:0 auto;padding:6rem 2rem 4rem}
  h1{font-size:clamp(2rem,5vw,3.5rem);font-weight:700;line-height:1.1;margin-bottom:1.5rem}
  h1 span{color:#22c55e}
  .sub{font-size:1.2rem;color:#a1a1aa;max-width:560px;margin-bottom:3rem}
  .pills{display:flex;gap:.75rem;flex-wrap:wrap;margin-bottom:4rem}
  .pill{background:#1a1a1a;border:1px solid #333;border-radius:999px;padding:.35rem 1rem;font-size:.85rem;color:#a1a1aa}
  .section{background:#0f0f0f;border-top:1px solid #1f1f1f;padding:4rem 2rem}
  .inner{max-width:800px;margin:0 auto}
  h2{font-size:1.6rem;font-weight:600;margin-bottom:2rem}
  .how-steps{display:grid;gap:1.5rem;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
  .step{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:1.5rem}
  .step-num{font-size:.75rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem}
  .tiers{display:grid;gap:1.5rem;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin-top:2rem}
  .tier{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:1.75rem;display:flex;flex-direction:column;gap:.75rem}
  .tier.featured{border-color:#22c55e}
  .tier-price{font-size:2rem;font-weight:700;color:#e2e2e2}
  .tier-price span{font-size:1rem;color:#71717a;font-weight:400}
  .tier-label{font-size:.8rem;color:#22c55e;font-weight:600;text-transform:uppercase;letter-spacing:.08em}
  .tier-desc{font-size:.9rem;color:#a1a1aa;flex:1}
  .btn{display:inline-block;background:#22c55e;color:#000;font-weight:700;padding:.75rem 1.5rem;border-radius:8px;text-decoration:none;font-size:.95rem;cursor:pointer;border:none;text-align:center;width:100%;margin-top:.5rem}
  .btn:hover{background:#16a34a}
  .btn-ghost{background:transparent;border:1px solid #333;color:#e2e2e2}
  .btn-ghost:hover{border-color:#555;background:#1a1a1a}
  code,pre{font-family:'Menlo','Consolas',monospace}
  .code-block{background:#0d0d0d;border:1px solid #2a2a2a;border-radius:8px;padding:1.25rem 1.5rem;overflow-x:auto;font-size:.85rem;color:#a1a1aa;margin-top:1rem}
  .code-block .hl{color:#22c55e}
  .footer{padding:3rem 2rem;text-align:center;color:#52525b;font-size:.85rem;border-top:1px solid #1f1f1f}
  a.link{color:#60a5fa;text-decoration:none}
  .badge{display:inline-flex;align-items:center;gap:.4rem;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;padding:.3rem .8rem;font-size:.8rem;color:#a1a1aa;text-decoration:none}
  .badges{display:flex;gap:.75rem;flex-wrap:wrap;margin-bottom:2.5rem}
</style>
</head>
<body>

<div class="hero">
  <div class="badges">
    <a class="badge" href="https://pypi.org/project/weaver-protocol/" target="_blank">📦 pip install weaver-protocol</a>
    <a class="badge" href="/docs" target="_blank">📖 API Docs</a>
    <span class="badge">v0.1.0</span>
  </div>
  <h1>AI outputs you can<br><span>actually prove.</span></h1>
  <p class="sub">
    Weaver Protocol runs your AI output through 2–5 independent observers with
    orthogonal roles — accuracy, safety, legal-read, adversarial — and returns a
    tamper-evident signed record. No single-point hallucination. Timestamped proof.
  </p>
  <div class="pills">
    <span class="pill">🏛 Law firms</span>
    <span class="pill">🏥 Healthcare</span>
    <span class="pill">🏢 Enterprise compliance</span>
    <span class="pill">🔬 AI governance</span>
    <span class="pill">⚖️ EU AI Act ready</span>
  </div>
</div>

<div class="section">
  <div class="inner">
    <h2>How it works</h2>
    <div class="how-steps">
      <div class="step">
        <div class="step-num">Step 1</div>
        <strong>Send your prompt</strong>
        <p style="color:#a1a1aa;font-size:.9rem;margin-top:.5rem">POST to /verify with the AI output you need verified.</p>
      </div>
      <div class="step">
        <div class="step-num">Step 2</div>
        <strong>Independent observers</strong>
        <p style="color:#a1a1aa;font-size:.9rem;margin-top:.5rem">Each observer sees it alone with a different critical role. No cross-contamination.</p>
      </div>
      <div class="step">
        <div class="step-num">Step 3</div>
        <strong>Signed provenance</strong>
        <p style="color:#a1a1aa;font-size:.9rem;margin-top:.5rem">Get back a WeaverScore, disagreement flags, and an HMAC-signed export you can show regulators.</p>
      </div>
    </div>
    <div class="code-block">
<span class="hl">curl</span> -X POST https://your-app.railway.app/verify \\<br>
  -H <span class="hl">"Authorization: Bearer wp_..."</span> \\<br>
  -H "Content-Type: application/json" \\<br>
  -d '{"prompt":"The defendant admitted liability on page 12.","observer_count":3,"model":"anthropic"}'
    </div>
  </div>
</div>

<div class="section" style="background:#0a0a0a">
  <div class="inner">
    <h2>Pricing</h2>
    <div class="tiers">
      <div class="tier">
        <div class="tier-label">Starter</div>
        <div class="tier-price">$49<span>/mo</span></div>
        <div class="tier-desc">500 verifications/mo. Mock + real LLM observers. Signed JSON exports. Perfect for developers and small teams.</div>
        <a class="btn btn-ghost" href="/billing/checkout" onclick="checkout('starter');return false">Get started</a>
      </div>
      <div class="tier featured">
        <div class="tier-label">Pro ★</div>
        <div class="tier-price">$199<span>/mo</span></div>
        <div class="tier-desc">5,000 verifications/mo. All observer roles. Priority SLA. Postgres session store. For production workloads.</div>
        <a class="btn" href="/billing/checkout" onclick="checkout('pro');return false">Get Pro</a>
      </div>
      <div class="tier">
        <div class="tier-label">Enterprise</div>
        <div class="tier-price">$499<span>/mo</span></div>
        <div class="tier-desc">Unlimited verifications. Dedicated support. Custom observer roles. On-prem deploy available. For regulated industries.</div>
        <a class="btn btn-ghost" href="/billing/checkout" onclick="checkout('enterprise');return false">Contact us</a>
      </div>
    </div>
    <p style="color:#52525b;font-size:.85rem;margin-top:1.5rem">
      Developer toolkit also available: <code>pip install weaver-protocol</code> — run locally, free, open-source MIT.
    </p>
  </div>
</div>

<div class="section">
  <div class="inner">
    <h2>Why enterprises pay for this</h2>
    <p style="color:#a1a1aa;max-width:640px">
      Post-<em>Moffatt v. Air Canada</em>, post-EU AI Act (August 2026): every enterprise
      AI deployment needs a paper trail. Courts and regulators don't accept "our model
      said so." They accept dated, signed, named-observer records that your general
      counsel can underwrite. That's what a Weaver export gives you — proof of due
      diligence, not just a JSON blob.
    </p>
    <p style="color:#a1a1aa;max-width:640px;margin-top:1rem">
      <strong style="color:#e2e2e2">We don't sell smarter AI. We sell AI whose mistakes you can invoice.</strong>
    </p>
  </div>
</div>

<div class="footer">
  Weaver Protocol — open-source core, hosted API. MIT license.<br>
  <a class="link" href="/docs">API Docs</a> ·
  <a class="link" href="https://github.com/claudenunc/home/tree/main/LIVE/weaver-protocol" target="_blank">GitHub</a> ·
  <a class="link" href="https://pypi.org/project/weaver-protocol/" target="_blank">PyPI</a>
</div>

<script>
async function checkout(tier) {
  const r = await fetch('/billing/checkout', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({tier, success_url: window.location.origin+'/billing/success', cancel_url: window.location.origin+'/billing/cancel'})
  });
  if (!r.ok) { alert('Billing not configured yet. Check back soon.'); return; }
  const d = await r.json();
  window.location.href = d.checkout_url;
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing():
    """Product landing page — pricing, how it works, checkout CTAs."""
    return _LANDING_HTML


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


@app.get("/billing/success", response_class=HTMLResponse)
def billing_success(stripe_session_id: str | None = Query(default=None)):
    """
    Post-payment landing page. Stripe appends ?stripe_session_id= to this URL.
    We retrieve the Stripe session to get customer_id, then look up the API key
    in our DB and display it. Handles the race where the webhook hasn't fired yet.
    """
    if not stripe_session_id or not _billing.is_configured():
        return _success_html(
            key=None,
            tier=None,
            pending=False,
            error="Session ID missing. If you completed payment, contact support for your API key.",
        )
    try:
        stripe_session = _billing.retrieve_checkout_session(stripe_session_id)
    except Exception as exc:
        return _success_html(key=None, tier=None, pending=False,
                             error=f"Could not retrieve session: {exc}. Contact support.")

    customer_id: str = stripe_session.get("customer", "")
    tier: str = (stripe_session.get("metadata") or {}).get("weaver_tier", "starter")

    if not customer_id:
        return _success_html(key=None, tier=tier, pending=False,
                             error="No customer ID in session. Contact support.")

    api_key = _db.get_active_key_for_customer(customer_id, tier)
    if api_key:
        return _success_html(key=api_key, tier=tier, pending=False, error=None)
    # Webhook not yet fired — ask user to refresh
    return _success_html(key=None, tier=tier, pending=True, error=None)


def _success_html(key: str | None, tier: str | None, pending: bool, error: str | None) -> str:
    tier_label = {"starter": "$49/mo", "pro": "$199/mo", "enterprise": "$499/mo"}.get(tier or "", tier or "")
    if error:
        body = f"""
        <div class="box error">
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <p>Email <a href="mailto:support@weaver-protocol.dev">support@weaver-protocol.dev</a></p>
        </div>"""
    elif pending:
        body = """
        <div class="box pending">
          <h2>Payment received ✓</h2>
          <p>Your API key is being generated. <strong>Refresh this page in 10 seconds.</strong></p>
          <p>If your key hasn't appeared within 60 seconds, contact support.</p>
          <script>setTimeout(()=>location.reload(), 10000)</script>
        </div>"""
    else:
        body = f"""
        <div class="box success">
          <h2>You're in ✓</h2>
          <p>Tier: <strong>{tier_label}</strong></p>
          <p>Your API key:</p>
          <pre class="key">{key}</pre>
          <p>Save it now — we don't store it in plaintext after this page.</p>
          <hr/>
          <p><strong>Quick start:</strong></p>
          <pre>curl -X POST https://your-app.railway.app/verify \\
  -H "Authorization: Bearer {key}" \\
  -H "Content-Type: application/json" \\
  -d '{{"prompt":"Your AI output here","observer_count":2,"model":"mock"}}'</pre>
          <p><a href="/docs">Full API docs →</a></p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Weaver Protocol — Activated</title>
<style>
  body{{font-family:system-ui,sans-serif;background:#0d0d0d;color:#e8e8e8;
       display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}
  .box{{background:#1a1a1a;border:1px solid #333;border-radius:12px;padding:2rem 2.5rem;max-width:640px;width:90%}}
  .success{{border-color:#22c55e}}.error{{border-color:#ef4444}}.pending{{border-color:#f59e0b}}
  pre{{background:#0d0d0d;border:1px solid #333;border-radius:6px;padding:1rem;overflow-x:auto;font-size:.85rem}}
  .key{{color:#22c55e;word-break:break-all}}
  a{{color:#60a5fa}}hr{{border-color:#333;margin:1.5rem 0}}
</style>
</head>
<body>{body}</body>
</html>"""


@app.get("/billing/cancel", response_class=HTMLResponse)
def billing_cancel():
    return """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Weaver Protocol — Checkout Cancelled</title>
<style>
  body{{font-family:system-ui,sans-serif;background:#0d0d0d;color:#e8e8e8;
       display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}
  .box{{background:#1a1a1a;border:1px solid #f59e0b;border-radius:12px;padding:2rem 2.5rem;max-width:480px;width:90%;text-align:center}}
  a{{color:#60a5fa;text-decoration:none;font-weight:600}}
</style>
</head>
<body>
<div class="box">
  <h2>Checkout cancelled</h2>
  <p>No charge was made.</p>
  <p><a href="/">Return to pricing →</a></p>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
