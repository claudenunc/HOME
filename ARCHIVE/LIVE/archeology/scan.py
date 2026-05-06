"""
HOME Archeology — Phase 2 Scanner
==================================

Metadata-only filesystem walker. Produces one JSONL line per file with:
path, size_bytes, mtime_iso, ext, head64_sha256, error.

Read-only. Never opens more than the first 64 KB of any file.
Skips common build/cache dirs (.git, node_modules, __pycache__, venv, .venv, dist, build).

Built by BEACON 🏮 for the HOME AI family.
Thesis: The proof IS the assembly. See HOME/DOCTRINE/THESIS.md.

Usage:
    python scan.py <root> --out <manifest.jsonl>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

HEAD_BYTES = 64 * 1024  # 64 KB — enough for near-dupe detection, cheap to read

SKIP_DIR_NAMES = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", ".cache", ".mypy_cache",
    ".pytest_cache", ".tox", ".idea", ".vscode",
}


def walk_files(root: Path) -> Iterator[Path]:
    """Yield every file under root, skipping noise directories.

    Permission errors on subtrees are swallowed so a single bad dir
    doesn't kill the whole scan.
    """
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            yield Path(dirpath) / name


def hash_head(path: Path, n: int = HEAD_BYTES) -> str:
    """SHA-256 of the first n bytes. Enough to dedupe near-identical files cheaply."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        h.update(f.read(n))
    return h.hexdigest()


def describe(path: Path, root: Path) -> dict:
    """Return a manifest record for a single file. Never raises."""
    try:
        st = path.stat()
        return {
            "path": str(path.relative_to(root)).replace("\\", "/"),
            "abs_path": str(path),
            "size_bytes": st.st_size,
            "mtime_iso": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
            "ext": path.suffix.lower(),
            "head64_sha256": hash_head(path) if st.st_size > 0 else "",
        }
    except (PermissionError, OSError) as e:
        return {
            "path": str(path).replace("\\", "/"),
            "error": f"{type(e).__name__}: {e}",
        }


def scan(root: Path, out: Path) -> dict:
    """Walk root, write JSONL to out, return a summary dict."""
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    total_bytes = 0
    errors = 0
    ext_counts: dict[str, int] = {}

    with out.open("w", encoding="utf-8") as fh:
        for file_path in walk_files(root):
            rec = describe(file_path, root)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
            if "error" in rec:
                errors += 1
            else:
                total_bytes += rec["size_bytes"]
                ext_counts[rec["ext"]] = ext_counts.get(rec["ext"], 0) + 1

    return {
        "root": str(root),
        "manifest": str(out),
        "file_count": count,
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / 1024 / 1024, 2),
        "error_count": errors,
        "top_extensions": sorted(ext_counts.items(), key=lambda kv: -kv[1])[:15],
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Metadata-only filesystem scanner for HOME archeology.")
    p.add_argument("root", type=Path, help="Directory to scan")
    p.add_argument("--out", type=Path, required=True, help="Output JSONL path")
    args = p.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    print(f"Scanning {root} ...")
    summary = scan(root, args.out)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
