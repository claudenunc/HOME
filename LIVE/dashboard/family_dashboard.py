"""
Unc's family cockpit — local server behind ENVY's family_room.html.

Serves HOME/PUBLIC/family_room.html at http://127.0.0.1:8765/ and a JSON
snapshot of the Supabase telemetry views at /api/snapshot. Because the page
and the snapshot are same-origin, ENVY's live cockpit section lights up
whenever this server is running; when it's not, the page still opens fine
over file:// with a polite "offline" note in that section.

The service_role key stays in HOME/SHARED/.env and never crosses the wire;
the browser only talks to /api/snapshot on localhost.

Run:
    python family_dashboard.py
    # opens http://127.0.0.1:8765/ automatically

Stop:
    Ctrl-C.

Author: ATLAS 🧭 on ENVY's 👑 HTML, 2026-04-23.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    from supabase import Client, create_client  # type: ignore
except ImportError:
    print("ERROR: supabase-py missing. `pip install supabase==2.7.4`", file=sys.stderr)
    sys.exit(2)

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv missing. `pip install python-dotenv`", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Env + client
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
HOME_ROOT = HERE.parents[1]
ENV_PATH = HOME_ROOT / "SHARED" / ".env"
FAMILY_ROOM_HTML = HOME_ROOT / "PUBLIC" / "family_room.html"
PUBLIC_DIR = HOME_ROOT / "PUBLIC"
load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_SECRET") or os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

if not SUPABASE_URL or not SUPABASE_KEY:
    print(
        f"ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_SECRET not found in {ENV_PATH}",
        file=sys.stderr,
    )
    sys.exit(2)

_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PORT = int(os.getenv("DASHBOARD_PORT", "8765"))


# ---------------------------------------------------------------------------
# Query helpers — every call wrapped so a failing view doesn't nuke the page
# ---------------------------------------------------------------------------

def _safe_query(fn, default):
    try:
        return fn()
    except Exception as e:
        return {"_error": str(e)[:300], "_fallback": default}


def snapshot() -> dict[str, Any]:
    """Assemble everything the dashboard needs in one pass."""
    return {
        "generated_at": time.time(),
        "dashboard": _safe_query(
            lambda: _client.table("v_atlas_dashboard").select("*").limit(1).execute().data,
            [],
        ),
        "family_today": _safe_query(
            lambda: _client.table("v_family_activity_today").select("*").execute().data,
            [],
        ),
        "cognition_stream": _safe_query(
            lambda: _client.table("v_cognition_stream").select("*").limit(20).execute().data,
            [],
        ),
        "drift_patterns": _safe_query(
            lambda: _client.table("v_drift_patterns_weekly")
            .select("*")
            .order("week_start", desc=True)
            .order("n_incidents", desc=True)
            .limit(15)
            .execute()
            .data,
            [],
        ),
        "drift_incidents": _safe_query(
            lambda: _client.table("drift_incidents")
            .select("incident_id,incident_date,sibling,drift_vector,caught_by,status,pattern_key")
            .order("incident_date", desc=True)
            .limit(15)
            .execute()
            .data,
            [],
        ),
        "memory_writes": _safe_query(
            lambda: _client.table("memory_ops_log")
            .select("ts,sibling,command,path,bytes_written,ok")
            .in_("command", ["create", "str_replace", "insert", "rename", "delete"])
            .order("ts", desc=True)
            .limit(15)
            .execute()
            .data,
            [],
        ),
        "confabulation_flags": _safe_query(
            lambda: _client.table("v_confabulation_flags")
            .select("*")
            .order("ts", desc=True)
            .limit(10)
            .execute()
            .data,
            [],
        ),
    }


# ---------------------------------------------------------------------------
# HTML — ENVY's family_room.html, read fresh from disk on each request so
# edits show up without a restart. The live-cockpit <section> inside it
# fetches /api/snapshot from this server.
# ---------------------------------------------------------------------------

_MIME = {
    ".html": "text/html; charset=utf-8",
    ".htm":  "text/html; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".js":   "application/javascript; charset=utf-8",
    ".json": "application/json",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".svg":  "image/svg+xml",
    ".webp": "image/webp",
    ".ico":  "image/x-icon",
}


def _serve_static(rel: str) -> tuple[int, bytes, str]:
    """Resolve a request path to a file inside PUBLIC_DIR, with traversal guard."""
    rel = rel.lstrip("/")
    target = (PUBLIC_DIR / rel).resolve()
    try:
        target.relative_to(PUBLIC_DIR.resolve())
    except ValueError:
        return 403, b"forbidden", "text/plain"
    if not target.is_file():
        return 404, b"not found", "text/plain"
    ctype = _MIME.get(target.suffix.lower(), "application/octet-stream")
    return 200, target.read_bytes(), ctype




# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # quiet mode — no per-request noise in the terminal
        return

    def _send(self, status: int, body: bytes, ctype: str):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path == "/" or path == "/index.html":
            if not FAMILY_ROOM_HTML.is_file():
                self._send(500, b"family_room.html missing", "text/plain")
                return
            body = FAMILY_ROOM_HTML.read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
            return

        if path == "/api/snapshot":
            try:
                data = snapshot()
                self._send(200, json.dumps(data, default=str).encode("utf-8"),
                           "application/json")
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode("utf-8")
                self._send(500, body, "application/json")
            return

        # static: serve anything under PUBLIC/ (assets, future pages)
        status, body, ctype = _serve_static(path)
        self._send(status, body, ctype)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # bind loopback only — key never leaves this machine
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"

    print("ATLAS family cockpit")
    print(f"   serving on {url}")
    print(f"   env:   {ENV_PATH}")
    print(f"   proj:  {os.getenv('SUPABASE_PROJECT_REF') or '(from SUPABASE_URL)'}")
    print("   Ctrl-C to stop.")

    # auto-open after a short delay so the bind finishes first
    threading.Timer(0.7, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down.")
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
