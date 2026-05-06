#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env_file(path: Path):
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw) if raw else {"ok": True}


def main():
    parser = argparse.ArgumentParser(description="Push member PUBLIC status to unified memory API.")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without posting.")
    args = parser.parse_args()

    member_root = Path(__file__).resolve().parent
    repo_root = member_root.parent
    member_id = member_root.name.lower()

    load_env_file(repo_root / ".env")
    load_env_file(repo_root / ".env.example")
    memory_api_url = os.getenv("MEMORY_API_URL", "http://127.0.0.1:8090")

    public_dir = member_root / "PUBLIC"
    capabilities = read_json(public_dir / "capabilities.json", {})
    availability = read_json(public_dir / "availability.json", {})
    adapter_status_path = public_dir / "memory_adapter_status.json"
    adapter_status = read_json(
        adapter_status_path,
        {
            "schema_version": "1.0",
            "member_id": member_id,
            "enabled": True,
            "last_push_utc": None,
            "last_error": None,
        },
    )

    content = (
        f"Status heartbeat for {member_id}. "
        f"Role: {capabilities.get('role', 'unknown')}. "
        f"Status: {availability.get('status', 'unknown')}. "
        f"Current task: {availability.get('current_task')}. "
        f"Lane: {availability.get('active_lane')}."
    )

    payload = {
        "event_id": str(uuid4()),
        "timestamp_utc": now_utc(),
        "actor": member_id,
        "member_scope": member_id,
        "event_type": "status_heartbeat",
        "priority": "medium",
        "content": content,
        "source_file": f"{member_root.name}/PUBLIC",
        "tags": ["status", "heartbeat", "member_adapter"],
        "thread_id": "default",
    }

    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "payload": payload}, indent=2))
        return

    try:
        result = post_json(f"{memory_api_url}/memory/events", payload)
        adapter_status["last_push_utc"] = now_utc()
        adapter_status["last_error"] = None
        adapter_status["last_event_id"] = payload["event_id"]
        adapter_status["last_result"] = result
        write_json(adapter_status_path, adapter_status)
        print(json.dumps({"ok": True, "member_id": member_id, "result": result}, indent=2))
    except urllib.error.URLError as e:
        adapter_status["last_push_utc"] = now_utc()
        adapter_status["last_error"] = str(e)
        write_json(adapter_status_path, adapter_status)
        print(json.dumps({"ok": False, "member_id": member_id, "error": str(e)}, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

