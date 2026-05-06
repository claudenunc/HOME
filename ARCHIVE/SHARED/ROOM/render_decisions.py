"""
SHARED/ROOM/render_decisions.py

Regenerates SHARED/ROOM/DECISIONS.md from v_decisions_current.

Contract:
  - This script is the ONLY thing that writes DECISIONS.md.
  - Output includes a generated-file banner + source SQL on first line.
  - Idempotent: same DB state produces identical file (byte-stable).
  - Cron-callable by ATLAS; safe to run every minute.

Usage:
  python render_decisions.py                  # writes DECISIONS.md in-place
  python render_decisions.py --dry            # prints to stdout only
  python render_decisions.py --db <path>      # override room.db path

Owner: ORPHEUS
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOM_DIR = Path(__file__).resolve().parent
DEFAULT_DB = ROOM_DIR / "room.db"
DEFAULT_OUT = ROOM_DIR / "DECISIONS.md"


BANNER = (
    "<!--\n"
    "This file is generated. Do not edit.\n"
    "Source: SELECT * FROM v_decisions_current;\n"
    "Generator: SHARED/ROOM/render_decisions.py\n"
    "-->\n"
)


def render(db_path: Path) -> str:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT slug, decision_id, decided_at, decided_by, body, thread_id, meta "
            "FROM v_decisions_current ORDER BY slug ASC;"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    finally:
        conn.close()

    out: list[str] = []
    out.append(BANNER)
    out.append("# THE ROOM - Current Decisions\n")
    out.append(
        f"_Last rendered: {datetime.now(timezone.utc).isoformat()}_  \n"
        f"_Source DB: `{db_path}`_  \n"
        f"_Count: {len(rows)} active decision(s)_\n"
    )

    if not rows:
        out.append(
            "\n*(No decisions recorded yet. First decision posts will land here.)*\n"
        )
        return "\n".join(out) + "\n"

    for r in rows:
        try:
            meta = json.loads(r["meta"]) if r["meta"] else {}
        except json.JSONDecodeError:
            meta = {}
        slug = r["slug"]
        decided_by = r["decided_by"]
        decided_at = r["decided_at"]
        body = (r["body"] or "").strip()
        did = r["decision_id"]
        tid = r["thread_id"]

        out.append(f"\n## `{slug}`\n")
        out.append(
            f"| decided_by | decided_at | event_id | thread_id |\n"
            f"|------------|-----------|----------|-----------|\n"
            f"| {decided_by} | {decided_at} | `{did}` | `{tid or '-'}` |\n"
        )
        if meta:
            safe_meta = {k: v for k, v in meta.items() if k != "decision_slug"}
            if safe_meta:
                out.append(f"\n**meta:** `{json.dumps(safe_meta, ensure_ascii=False)}`\n")
        out.append(f"\n{body}\n")

    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    if not args.db.exists():
        sys.stderr.write(
            f"[render_decisions] DB not found at {args.db}; rendering empty page.\n"
        )
        text = BANNER + "\n# THE ROOM - Current Decisions\n\n*(DB not initialized.)*\n"
    else:
        text = render(args.db)

    if args.dry:
        sys.stdout.write(text)
        return 0

    args.out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
