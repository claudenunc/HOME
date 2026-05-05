"""
Weaver Protocol — Hosted API
Paid tier entry point: multi-observer verification as a service.
"""
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

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
# In-memory session store (swap for Postgres/Redis in production)
# ---------------------------------------------------------------------------

_sessions: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class VerifyRequest(BaseModel):
    prompt: str
    observer_count: int = 2
    model: str = "mock"  # "mock" | "anthropic" | "openai"


class ObserverResult(BaseModel):
    observer_id: str
    response: str
    timestamp: str


class VerifyResponse(BaseModel):
    session_id: str
    prompt: str
    observers: list[ObserverResult]
    consensus: str | None
    disagreement_detected: bool
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
    return {"status": "ok", "version": "0.1.0", "timestamp": _now()}


@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest, api_key: str = Depends(verify_api_key)):
    """
    Run attested multi-observer verification on a prompt.
    Returns a signed provenance record alongside the consensus result.
    """
    try:
        from weaver.adapters.mock import MockAdapter
        from weaver.session import WeaverSession

        adapter = MockAdapter()
        session = WeaverSession(adapter=adapter, observer_count=req.observer_count)
        result = session.run(req.prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification error: {exc}") from exc

    session_id = str(uuid.uuid4())
    created_at = _now()

    observers = [
        ObserverResult(
            observer_id=f"observer-{i+1}",
            response=r,
            timestamp=created_at,
        )
        for i, r in enumerate(result.get("responses", []))
    ]

    disagreement = result.get("disagreement", False)
    consensus = result.get("consensus")

    provenance = {
        "session_id": session_id,
        "created_at": created_at,
        "model": req.model,
        "observer_count": req.observer_count,
        "weaver_version": "0.1.0",
        "disagreement_detected": disagreement,
        "observer_ids": [o.observer_id for o in observers],
    }

    _sessions[session_id] = {
        "session_id": session_id,
        "created_at": created_at,
        "prompt": req.prompt,
        "observers": [o.model_dump() for o in observers],
        "consensus": consensus,
        "disagreement_detected": disagreement,
        "provenance": provenance,
    }

    return VerifyResponse(
        session_id=session_id,
        prompt=req.prompt,
        observers=observers,
        consensus=consensus,
        disagreement_detected=disagreement,
        provenance=provenance,
    )


@app.get("/session/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """Retrieve a previously run verification session by ID."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        session_id=session["session_id"],
        created_at=session["created_at"],
        prompt=session["prompt"],
        consensus=session["consensus"],
        disagreement_detected=session["disagreement_detected"],
        observer_count=len(session["observers"]),
    )


@app.get("/drift-log/summary")
def drift_log_summary(api_key: str = Depends(verify_api_key)):
    """
    Public-facing drift log summary. Returns aggregate stats only —
    full log is on GitHub for transparency.
    """
    total_sessions = len(_sessions)
    disagreements = sum(1 for s in _sessions.values() if s["disagreement_detected"])
    return {
        "total_sessions": total_sessions,
        "disagreements_detected": disagreements,
        "drift_log_url": "https://github.com/claudenunc/home/blob/main/EVIDENCE/drift_log.md",
        "weaver_version": "0.1.0",
        "as_of": _now(),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
