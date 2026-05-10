"""
Tests for /demo endpoint — no-auth mock verification.
"""
import os
import sys

os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("DATABASE_URL", None)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_demo_returns_200():
    r = client.get("/demo")
    assert r.status_code == 200


def test_demo_no_auth_required():
    """Hit /demo without any Authorization header — must succeed."""
    r = client.get("/demo", headers={})
    assert r.status_code == 200


def test_demo_response_schema():
    r = client.get("/demo")
    body = r.json()
    assert "session_id" in body
    assert body["session_id"].startswith("demo-")
    assert "weaver_score" in body
    assert "observers" in body
    assert len(body["observers"]) == 3
    assert "disagreement_detected" in body
    assert "consensus" in body
    assert "provenance" in body


def test_demo_provenance_has_demo_flag():
    r = client.get("/demo")
    prov = r.json()["provenance"]
    assert prov.get("demo") is True
    assert prov["observer_count"] == 3
    assert prov["model"] == "mock"


def test_demo_observer_roles():
    r = client.get("/demo")
    roles = {obs["role"] for obs in r.json()["observers"]}
    assert roles == {"accuracy", "safety", "legal-read"}


def test_demo_weaver_score_in_range():
    r = client.get("/demo")
    score = r.json()["weaver_score"]
    assert 0.0 <= score <= 1.0


def test_demo_is_stable_across_calls():
    """Demo should return valid schema on repeated calls (no state bleed)."""
    for _ in range(3):
        r = client.get("/demo")
        assert r.status_code == 200
        assert r.json()["weaver_score"] >= 0.0
