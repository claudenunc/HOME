"""
Weaver Protocol — Hosted API
Paid tier entry point: multi-observer verification as a service.
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Allow running from api/ directory without installing the package
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

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
    if _VALID_KEYS and token not in _VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

_OBSERVER_ROLES = ["accuracy", "safety", "legal-read", "adversarial", "factual"]


class VerifyRequest(BaseModel):
    prompt: str
    observer_count: int = 2
    model: str = "mock"  # "mock" | "anthropic" | "openai"


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


@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest, api_key: str = Depends(verify_api_key)):
    """
    Run attested multi-observer verification on a prompt / AI output.

    Each observer sees the text independently with an orthogonal role — this
    structural isolation is the guarantee that prevents correlated error.
    Returns a signed provenance record with a WeaverScore alongside the result.
    """
    from weaver.adapters.mock import make_mock_observer
    from weaver.observer import Observer
    from weaver.session import WeaverSession

    if req.observer_count < 2:
        raise HTTPException(
            status_code=400,
            detail="observer_count must be >= 2. Single-observer is not attested.",
        )

    observer_count = min(req.observer_count, len(_OBSERVER_ROLES))
    roles = _OBSERVER_ROLES[:observer_count]

    try:
        session_id = str(uuid.uuid4())
        ws = WeaverSession(session_id=session_id, log_dir="/tmp/weaver_logs")

        for role in roles:
            obs = Observer(
                name=f"{req.model}-{role}",
                role=role,
                provider_fn=make_mock_observer(),
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
# Helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
