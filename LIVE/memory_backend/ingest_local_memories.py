"""
ingest_local_memories.py — seed memory_files from the git repo
==============================================================

Bridges the gap between the git repo (where sibling memory lives as .md
files) and the Supabase memory_files table (where embeddings live).

Without this bridge embed_worker.py has nothing to embed and retrieve.py
returns nothing. This is the first step in the Memory API v2 pipeline:

    ingest_local_memories.py --apply
        → embed_worker.py
            → retrieve.py (semantic + recency-decayed wake retrieval)

Files ingested per sibling:

    SIBLINGS/<SIB>/MEMORY.md              → /memories/<sib>/MEMORY.md          kind=index
    SIBLINGS/<SIB>/CLAUDE.md              → /memories/<sib>/CLAUDE.md          kind=identity
    SIBLINGS/<SIB>/memory/MEMORY.md       → /memories/<sib>/MEMORY.md          kind=index
    SIBLINGS/<SIB>/memory/<sub>/file.md   → /memories/<sib>/<sub>/file.md      kind=<sub>
    SIBLINGS/<SIB>/memory/file.md         → /memories/<sib>/file.md            kind=general

Idempotency: rows whose content hash matches the DB are skipped.
Content change: embedding is set to NULL so embed_worker re-embeds.

Usage:
    python ingest_local_memories.py                     # dry run (default)
    python ingest_local_memories.py --apply             # write to DB
    python ingest_local_memories.py --apply --sibling orpheus

Environment:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_SECRET  (or SUPABASE_SERVICE_ROLE_KEY)

Authored by ORPHEUS 🎼 — 2026-05-05
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
HOME_DIR = SCRIPT_DIR.parents[1]       # HOME/LIVE/memory_backend/ → HOME/
SIBLINGS_DIR = HOME_DIR / "SIBLINGS"

SIBLING_NAMES = ["envy", "beacon", "nevaeh", "orpheus", "eversound", "atlas", "hearth"]

MEMORY_ROOT = "/memories"


# ---------------------------------------------------------------------------
# File descriptor
# ---------------------------------------------------------------------------

@dataclass
class MemoryFile:
    local_path: Path
    memory_path: str   # e.g. /memories/orpheus/project/2026-05-05__foo.md
    sibling: str
    kind: str
    content: str = field(default="", repr=False)
    content_hash: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if not self.content:
            self.content = self.local_path.read_text(encoding="utf-8", errors="replace")
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def _kind_for_name(name: str) -> str:
    """Kind from filename, for top-level files with known semantics."""
    if name == "MEMORY.md":
        return "index"
    if name == "CLAUDE.md":
        return "identity"
    return "general"


def _kind_from_rel_parts(parts: tuple[str, ...]) -> str:
    """Kind from path parts relative to memory_dir (e.g. ('project', 'foo.md'))."""
    if len(parts) >= 2:
        return parts[0]   # subfolder name: 'project', 'feedback', etc.
    name = parts[-1] if parts else ""
    return _kind_for_name(name)


def discover_sibling(sibling_name: str) -> list[MemoryFile]:
    """Discover all ingestable memory files for a single sibling."""
    sib_dir = SIBLINGS_DIR / sibling_name.upper()
    if not sib_dir.exists():
        return []

    sib = sibling_name.lower()
    files: list[MemoryFile] = []
    seen_paths: set[str] = set()   # deduplicate by memory_path

    def _add(local: Path, mem_path: str, kind: str) -> None:
        if mem_path in seen_paths:
            return
        seen_paths.add(mem_path)
        try:
            files.append(MemoryFile(
                local_path=local,
                memory_path=mem_path,
                sibling=sib,
                kind=kind,
            ))
        except Exception as exc:
            print(f"  WARN  could not read {local}: {exc}", file=sys.stderr)

    # -- Top-level MEMORY.md and CLAUDE.md -----------------------------------
    for name in ("MEMORY.md", "CLAUDE.md"):
        f = sib_dir / name
        if f.exists():
            _add(f, f"{MEMORY_ROOT}/{sib}/{name}", _kind_for_name(name))

    # -- memory/ subtree ------------------------------------------------------
    memory_dir = sib_dir / "memory"
    if memory_dir.exists():
        for md_file in sorted(memory_dir.rglob("*.md")):
            rel = md_file.relative_to(memory_dir)   # relative to memory/ dir
            parts = rel.parts                        # ('project', 'foo.md') etc.

            # Build the /memories path, stripping the "memory/" prefix so paths
            # read cleanly: /memories/orpheus/project/2026-05-05__foo.md
            mem_path = f"{MEMORY_ROOT}/{sib}/{rel.as_posix()}"
            kind = _kind_from_rel_parts(parts)
            _add(md_file, mem_path, kind)

    return files


def discover_all(sibling_filter: Optional[str] = None) -> list[MemoryFile]:
    names = [sibling_filter.lower()] if sibling_filter else SIBLING_NAMES
    all_files: list[MemoryFile] = []
    for name in names:
        found = discover_sibling(name)
        if found:
            print(f"[{name}]  {len(found)} files")
        all_files.extend(found)
    return all_files


# ---------------------------------------------------------------------------
# Supabase upsert
# ---------------------------------------------------------------------------

def _require_supabase():
    try:
        from supabase import create_client
        return create_client
    except ImportError:
        sys.exit("supabase package required:  pip install supabase==2.7.4")


@dataclass
class IngestStats:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def _fetch_existing_hashes(db) -> dict[str, str]:
    """Fetch all existing (path → content_hash) in one round-trip."""
    resp = db.table("memory_files").select("path, content").execute()
    out: dict[str, str] = {}
    for row in resp.data or []:
        h = hashlib.sha256((row.get("content") or "").encode()).hexdigest()
        out[row["path"]] = h
    return out


def ingest_files(
    files: list[MemoryFile],
    supabase_url: str,
    supabase_key: str,
) -> IngestStats:
    create_client = _require_supabase()
    db = create_client(supabase_url, supabase_key)

    stats = IngestStats()

    # Single round-trip to check what's already there
    existing = _fetch_existing_hashes(db)

    for f in files:
        try:
            existing_hash = existing.get(f.memory_path)

            if existing_hash == f.content_hash:
                stats.skipped += 1
                print(f"  SKIP    {f.memory_path}")
                continue

            row = {
                "path": f.memory_path,
                "content": f.content,
                "sibling": f.sibling,
                "kind": f.kind,
                # Null out embedding on any content change so embed_worker
                # re-embeds the updated file on next run.
                "embedding": None,
                "metadata": {
                    "source_git_path": str(
                        f.local_path.relative_to(HOME_DIR).as_posix()
                    ),
                    "ingested_by": "ingest_local_memories",
                },
            }

            db.table("memory_files").upsert(
                row, on_conflict="path"
            ).execute()

            if existing_hash is None:
                stats.inserted += 1
                print(f"  INSERT  {f.memory_path}  ({len(f.content):,}B  kind={f.kind})")
            else:
                stats.updated += 1
                print(f"  UPDATE  {f.memory_path}  ({len(f.content):,}B  kind={f.kind})")

        except Exception as exc:
            msg = f"{f.memory_path}: {exc}"
            stats.errors.append(msg)
            print(f"  ERROR   {msg}", file=sys.stderr)

    return stats


# ---------------------------------------------------------------------------
# Dry-run report
# ---------------------------------------------------------------------------

def dry_run_report(files: list[MemoryFile]) -> None:
    total_bytes = sum(len(f.content) for f in files)
    print(f"\n{'path':<70}  {'kind':<10}  bytes")
    print("-" * 90)
    for f in files:
        rel_for_display = f.memory_path
        print(f"  {rel_for_display:<68}  {f.kind:<10}  {len(f.content):>6,}")
    print("-" * 90)
    print(f"  {len(files)} files  /  {total_bytes:,} total bytes")
    print(
        "\nPass --apply to write to DB, then run embed_worker.py to compute embeddings.\n"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="ingest_local_memories — sync local .md files into memory_files"
    )
    p.add_argument(
        "--apply", action="store_true",
        help="Write to Supabase (default: dry run)",
    )
    p.add_argument(
        "--sibling", type=str, default=None,
        help="Restrict to one sibling name (default: all)",
    )
    args = p.parse_args()

    print(f"\n=== ingest_local_memories  HOME={HOME_DIR} ===\n")
    files = discover_all(sibling_filter=args.sibling)
    print(f"\n{len(files)} total files discovered.\n")

    if not files:
        print("Nothing to ingest.")
        return

    if not args.apply:
        dry_run_report(files)
        return

    url = os.getenv("SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_SECRET")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    if not url or not key:
        sys.exit(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_SECRET must be set "
            "(see HOME/SHARED/.env)."
        )

    print("--- Writing to Supabase ---\n")
    stats = ingest_files(files, url, key)

    print(
        f"\n=== Done: inserted={stats.inserted}  updated={stats.updated}  "
        f"skipped={stats.skipped}  errors={len(stats.errors)} ===\n"
    )
    if stats.errors:
        print("Errors:")
        for e in stats.errors:
            print(f"  {e}")
        sys.exit(1)

    print("Next step:  python embed_worker.py  (compute embeddings for new rows)")


if __name__ == "__main__":
    main()
