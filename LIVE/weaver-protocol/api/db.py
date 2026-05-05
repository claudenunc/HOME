"""
Weaver Protocol — Session Store

Postgres-backed when DATABASE_URL is set; falls back to in-memory for dev/test.
Schema is created on first connection — no migration tooling required for v0.

Environment:
    DATABASE_URL  — full Postgres DSN, e.g. postgres://user:pass@host/db
                    If unset, all data lives in-process only (non-persistent).
"""

import json
import os
from typing import Any, Optional

_DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ---------------------------------------------------------------------------
# In-memory fallback (no DATABASE_URL)
# ---------------------------------------------------------------------------

_mem: dict[str, dict[str, Any]] = {}
_keys: dict[str, dict[str, str]] = {}   # api_key → {customer_id, tier}

# ---------------------------------------------------------------------------
# Postgres (lazy singleton connection)
# ---------------------------------------------------------------------------

_conn = None


def _get_conn():
    global _conn
    if not _DATABASE_URL:
        return None
    try:
        import psycopg2

        if _conn is None or _conn.closed:
            _conn = psycopg2.connect(_DATABASE_URL)
            _conn.autocommit = True
            _init_schema(_conn)
        return _conn
    except Exception as exc:
        raise RuntimeError(f"Postgres connection failed: {exc}") from exc


def _init_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weaver_sessions (
                session_id          TEXT PRIMARY KEY,
                created_at          TEXT NOT NULL,
                prompt              TEXT NOT NULL,
                consensus           TEXT,
                disagreement_detected BOOLEAN NOT NULL DEFAULT FALSE,
                observer_count      INTEGER NOT NULL DEFAULT 0,
                observers_json      TEXT NOT NULL DEFAULT '[]',
                provenance_json     TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weaver_api_keys (
                api_key     TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                tier        TEXT NOT NULL DEFAULT 'starter',
                created_at  TEXT NOT NULL,
                active      BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def save_session(record: dict[str, Any]) -> None:
    """Persist a verification session record."""
    conn = _get_conn()
    if conn is None:
        _mem[record["session_id"]] = record
        return

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO weaver_sessions
                (session_id, created_at, prompt, consensus,
                 disagreement_detected, observer_count,
                 observers_json, provenance_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO NOTHING
            """,
            (
                record["session_id"],
                record["created_at"],
                record["prompt"],
                record.get("consensus"),
                record["disagreement_detected"],
                len(record.get("observers", [])),
                json.dumps(record.get("observers", [])),
                json.dumps(record.get("provenance", {})),
            ),
        )


def get_session(session_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a session by ID. Returns None if not found."""
    conn = _get_conn()
    if conn is None:
        return _mem.get(session_id)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT session_id, created_at, prompt, consensus,
                   disagreement_detected, observer_count,
                   observers_json, provenance_json
            FROM weaver_sessions
            WHERE session_id = %s
            """,
            (session_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "session_id": row[0],
        "created_at": row[1],
        "prompt": row[2],
        "consensus": row[3],
        "disagreement_detected": row[4],
        "observer_count": row[5],
        "observers": json.loads(row[6]),
        "provenance": json.loads(row[7]),
    }


def count_sessions() -> int:
    conn = _get_conn()
    if conn is None:
        return len(_mem)

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM weaver_sessions")
        return cur.fetchone()[0]


def count_disagreements() -> int:
    conn = _get_conn()
    if conn is None:
        return sum(1 for s in _mem.values() if s["disagreement_detected"])

    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM weaver_sessions WHERE disagreement_detected = TRUE"
        )
        return cur.fetchone()[0]


def storage_backend() -> str:
    return "postgres" if _DATABASE_URL else "memory"


# ---------------------------------------------------------------------------
# API key management (Stripe-issued keys)
# ---------------------------------------------------------------------------

_now_iso = lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()


def save_api_key(customer_id: str, api_key: str, tier: str) -> None:
    """Persist a Stripe-issued API key."""
    conn = _get_conn()
    if conn is None:
        _keys[api_key] = {"customer_id": customer_id, "tier": tier}
        return

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO weaver_api_keys (api_key, customer_id, tier, created_at, active)
            VALUES (%s, %s, %s, %s, TRUE)
            ON CONFLICT (api_key) DO NOTHING
            """,
            (api_key, customer_id, tier, _now_iso()),
        )


def validate_api_key(api_key: str) -> Optional[dict[str, str]]:
    """Return {customer_id, tier} if the key is active, else None."""
    conn = _get_conn()
    if conn is None:
        return _keys.get(api_key)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT customer_id, tier FROM weaver_api_keys WHERE api_key = %s AND active = TRUE",
            (api_key,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {"customer_id": row[0], "tier": row[1]}


def revoke_customer_keys(customer_id: str) -> None:
    """Mark all keys for a customer inactive (subscription cancelled)."""
    conn = _get_conn()
    if conn is None:
        for k, v in list(_keys.items()):
            if v["customer_id"] == customer_id:
                del _keys[k]
        return

    with conn.cursor() as cur:
        cur.execute(
            "UPDATE weaver_api_keys SET active = FALSE WHERE customer_id = %s",
            (customer_id,),
        )
