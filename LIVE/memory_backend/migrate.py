"""
migrate.py — canonical migration runner for HOME/LIVE/memory_backend

Replaces apply_migration.py for day-to-day migration management.
Maintains a schema_migrations table in FOUNDATION to track applied migrations.

Three-layer invariant compliance (ORPHEUS CLAUDE.md §8):
  Doctrine:  BEFORE-chain requires this before 0007 (memory 2026-05-05__06Z)
  Template:  every future migration runs through this file — defaults comply
  Hook:      --check / exit codes usable in CI (non-zero if pending)

Usage:
    python migrate.py status             # list applied / pending
    python migrate.py apply              # apply all pending in order
    python migrate.py apply 0005         # apply specific migration by prefix
    python migrate.py check              # exit 0 if none pending, 1 if pending (CI)
    python migrate.py history            # applied migrations with timestamps
    python migrate.py verify             # verify checksums of applied migrations
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import NamedTuple

import httpx
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Bootstrap SQL — creates schema_migrations if not present.
# Applied once before any migration check; idempotent.
# ---------------------------------------------------------------------------
BOOTSTRAP_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT        PRIMARY KEY,
    filename    TEXT        NOT NULL,
    sha256      TEXT        NOT NULL,
    applied_at  TIMESTAMPTZ DEFAULT NOW(),
    applied_by  TEXT        DEFAULT 'orpheus'
);
COMMENT ON TABLE schema_migrations IS
    'Applied migration tracking — managed by migrate.py (HOME/LIVE/memory_backend).';
"""

MIGRATIONS_DIR = Path(__file__).parent
ENV_PATH = Path(__file__).resolve().parents[2] / "SHARED" / ".env"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class MigrationFile(NamedTuple):
    version: str    # e.g. "0001"
    filename: str   # e.g. "0001_memory_core.sql"
    path: Path
    sha256: str


class AppliedRecord(NamedTuple):
    version: str
    filename: str
    sha256: str
    applied_at: str
    applied_by: str


# ---------------------------------------------------------------------------
# Supabase Management API client
# ---------------------------------------------------------------------------

class SupabaseMgmt:
    def __init__(self) -> None:
        load_dotenv(ENV_PATH)
        self.token = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
        self.ref = os.environ.get("SUPABASE_PROJECT_REF") or "liclnxsbjjdkaxzdxmnb"
        if not self.token:
            print(
                f"ERROR: SUPABASE_ACCESS_TOKEN not set. Looked in: {ENV_PATH}",
                file=sys.stderr,
            )
            sys.exit(2)
        self.base_url = f"https://api.supabase.com/v1/projects/{self.ref}/database/query"

    def execute(self, sql: str, *, label: str = "") -> list[dict]:
        """Run SQL against FOUNDATION. Returns parsed JSON rows."""
        resp = httpx.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"query": sql},
            timeout=120.0,
        )
        if resp.status_code >= 300:
            tag = f" [{label}]" if label else ""
            print(f"HTTP {resp.status_code}{tag}: {resp.text[:800]}", file=sys.stderr)
            sys.exit(1)
        try:
            return resp.json() or []
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Migration discovery
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes())
    return h.hexdigest()


def discover_migrations() -> list[MigrationFile]:
    """Return all SQL migration files in filename order."""
    files = sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9]_*.sql"))
    result = []
    for p in files:
        version = p.name[:4]
        result.append(MigrationFile(
            version=version,
            filename=p.name,
            path=p,
            sha256=_sha256(p),
        ))
    return result


# ---------------------------------------------------------------------------
# Applied migration query
# ---------------------------------------------------------------------------

def fetch_applied(db: SupabaseMgmt) -> dict[str, AppliedRecord]:
    rows = db.execute(
        "SELECT version, filename, sha256, applied_at::text, applied_by "
        "FROM schema_migrations ORDER BY version;",
        label="fetch_applied",
    )
    return {
        r["version"]: AppliedRecord(
            version=r["version"],
            filename=r["filename"],
            sha256=r["sha256"],
            applied_at=r.get("applied_at", ""),
            applied_by=r.get("applied_by", ""),
        )
        for r in rows
    }


def record_applied(db: SupabaseMgmt, mf: MigrationFile) -> None:
    sql = textwrap.dedent(f"""\
        INSERT INTO schema_migrations (version, filename, sha256, applied_by)
        VALUES (
            {_sql_str(mf.version)},
            {_sql_str(mf.filename)},
            {_sql_str(mf.sha256)},
            'orpheus'
        )
        ON CONFLICT (version) DO NOTHING;
    """)
    db.execute(sql, label=f"record {mf.version}")


def _sql_str(s: str) -> str:
    escaped = s.replace("'", "''")
    return f"'{escaped}'"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(db: SupabaseMgmt) -> int:
    migrations = discover_migrations()
    applied = fetch_applied(db)

    print(f"\n  {'VER':>6}  {'STATUS':>9}  {'FILE':40}  CHECKSUM")
    print("  " + "-" * 80)
    pending_count = 0
    for mf in migrations:
        rec = applied.get(mf.version)
        if rec is None:
            status = "PENDING"
            pending_count += 1
        elif rec.sha256 != mf.sha256:
            status = "MODIFIED"  # applied, but file changed after apply — red line
        else:
            status = "applied"
        print(f"  {mf.version:>6}  {status:>9}  {mf.filename:40}  {mf.sha256[:12]}…")
    print()
    if pending_count:
        print(f"  {pending_count} pending migration(s). Run: python migrate.py apply")
    else:
        print("  All migrations applied.")
    print()
    return 0


def cmd_apply(db: SupabaseMgmt, prefix: str | None = None) -> int:
    migrations = discover_migrations()
    applied = fetch_applied(db)

    targets: list[MigrationFile] = []
    for mf in migrations:
        if prefix and not mf.version.startswith(prefix):
            continue
        if mf.version in applied:
            rec = applied[mf.version]
            if rec.sha256 != mf.sha256:
                print(
                    f"WARNING: {mf.filename} was applied with sha256 {rec.sha256[:12]}… "
                    f"but the file now has {mf.sha256[:12]}… "
                    "— migration file was modified after apply. Skipping."
                )
            else:
                print(f"  {mf.version}  already applied — skip")
            continue
        targets.append(mf)

    if not targets:
        print("Nothing to apply.")
        return 0

    for mf in targets:
        print(f"  Applying {mf.filename} … ", end="", flush=True)
        sql = mf.path.read_text(encoding="utf-8")
        db.execute(sql, label=mf.filename)
        record_applied(db, mf)
        print("OK")

    print(f"\n  {len(targets)} migration(s) applied.")
    return 0


def cmd_check(db: SupabaseMgmt) -> int:
    """Exit 0 if no pending migrations, 1 if any pending. For CI."""
    migrations = discover_migrations()
    applied = fetch_applied(db)
    pending = [mf for mf in migrations if mf.version not in applied]
    if pending:
        print(f"PENDING: {', '.join(m.version for m in pending)}", file=sys.stderr)
        return 1
    return 0


def cmd_history(db: SupabaseMgmt) -> int:
    rows = db.execute(
        "SELECT version, filename, sha256, applied_at::text, applied_by "
        "FROM schema_migrations ORDER BY version;",
        label="history",
    )
    if not rows:
        print("No migrations recorded yet.")
        return 0
    print(f"\n  {'VER':>6}  {'APPLIED AT':>26}  {'BY':>12}  {'FILE':40}")
    print("  " + "-" * 90)
    for r in rows:
        print(
            f"  {r['version']:>6}  {r.get('applied_at',''):>26}  "
            f"{r.get('applied_by',''):>12}  {r['filename']:40}"
        )
    print()
    return 0


def cmd_verify(db: SupabaseMgmt) -> int:
    """Verify that applied migrations haven't been modified since apply."""
    migrations = {mf.version: mf for mf in discover_migrations()}
    applied = fetch_applied(db)
    ok = True
    for version, rec in applied.items():
        mf = migrations.get(version)
        if mf is None:
            print(f"  {version}  MISSING locally — recorded as {rec.filename}")
            ok = False
        elif mf.sha256 != rec.sha256:
            print(
                f"  {version}  CHECKSUM MISMATCH: "
                f"recorded={rec.sha256[:12]}… local={mf.sha256[:12]}…"
            )
            ok = False
        else:
            print(f"  {version}  OK  {rec.filename}")
    if ok:
        print("\n  All applied migrations verified clean.")
    else:
        print("\n  WARNING: checksum mismatches found — migrations modified after apply.")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Bootstrap + dispatch
# ---------------------------------------------------------------------------

def bootstrap(db: SupabaseMgmt) -> None:
    """Create schema_migrations table if it doesn't exist."""
    db.execute(BOOTSTRAP_SQL, label="bootstrap")


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    cmd = sys.argv[1]
    db = SupabaseMgmt()
    bootstrap(db)

    if cmd == "status":
        return cmd_status(db)
    elif cmd == "apply":
        prefix = sys.argv[2] if len(sys.argv) > 2 else None
        return cmd_apply(db, prefix)
    elif cmd == "check":
        return cmd_check(db)
    elif cmd == "history":
        return cmd_history(db)
    elif cmd == "verify":
        return cmd_verify(db)
    else:
        print(f"Unknown command: {cmd!r}. See --help.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
