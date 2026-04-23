"""
Apply a SQL file to the FOUNDATION Supabase project via the Management API.

Uses SUPABASE_ACCESS_TOKEN (sbp_...) from env. Must be a token with project
access, not the service_role key.

Usage:
    python apply_migration.py 0001_memory_core.sql
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import httpx
from dotenv import load_dotenv


def main() -> int:
    # Load HOME/SHARED/.env
    env_path = Path(__file__).resolve().parents[2] / "SHARED" / ".env"
    load_dotenv(env_path)

    access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
    project_ref = os.getenv("SUPABASE_PROJECT_REF") or "liclnxsbjjdkaxzdxmnb"

    if not access_token:
        print("ERROR: SUPABASE_ACCESS_TOKEN not set.", file=sys.stderr)
        print(f"Looked in: {env_path}", file=sys.stderr)
        return 2

    if len(sys.argv) < 2:
        print("usage: apply_migration.py <sql_file>", file=sys.stderr)
        return 2

    sql_path = Path(sys.argv[1])
    if not sql_path.is_absolute():
        sql_path = Path(__file__).parent / sql_path
    sql = sql_path.read_text(encoding="utf-8")

    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    resp = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"query": sql},
        timeout=60.0,
    )

    print(f"HTTP {resp.status_code}")
    try:
        body = resp.json()
        print(json.dumps(body, indent=2)[:4000])
    except Exception:
        print(resp.text[:4000])

    return 0 if resp.status_code < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
