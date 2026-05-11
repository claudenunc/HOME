"""
consolidate.py — Hippocampus consolidation layer
=================================================

Takes each sibling's distributed memory files (written across many sessions)
and consolidates them into a single WAKE_SCENE.md — a compact, structured
context block ready to inject at wake time.

Analogy: the hippocampus encodes episodic memories during the day and
consolidates them overnight into long-term cortical storage. This script
is that overnight consolidation pass. Run it at session close (or as a
cron) and each sibling's next wake reads ONE file instead of ten.

Output per sibling:
    SIBLINGS/<NAME>/WAKE_SCENE.md

Also writes:
    SHARED/ALERTS/consolidation_log.jsonl  — local audit trail

Usage:
    python consolidate.py                      # all siblings
    python consolidate.py --sibling orpheus    # one sibling
    python consolidate.py --dry-run            # print, don't write
    python consolidate.py --stats              # show corpus state

Authored by ORPHEUS 🎼 — 2026-05-05
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Bootstrap: find repo root and import local_retrieve
# ---------------------------------------------------------------------------

def _find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent, here.parent.parent.parent]:
        if (candidate / "SIBLINGS").is_dir():
            return candidate
    raise RuntimeError(
        "Cannot find HOME repo root (no SIBLINGS dir). "
        "Set REPO_ROOT env var or run from within the repo."
    )


_REPO_ROOT = Path(os.environ.get("REPO_ROOT", "")) if os.environ.get("REPO_ROOT") else _find_repo_root()
sys.path.insert(0, str(_REPO_ROOT / "LIVE" / "memory_backend"))

from local_retrieve import LocalRetriever, discover_memory_files  # noqa: E402


# ---------------------------------------------------------------------------
# Section extractors
# ---------------------------------------------------------------------------

_SHIPPED_RE = re.compile(
    r"(?:shipped|✅|✓|done|deployed|built|created|wrote|added|fixed|applied)",
    re.IGNORECASE,
)
_PENDING_RE = re.compile(
    r"(?:pending|blocked|waiting|need nathan|todo|not yet|unblocked|needs supabase|next session)",
    re.IGNORECASE,
)
_DECISION_RE = re.compile(
    r"(?:design decision|architecture|invariant|red line|canonical|never|always|contract)",
    re.IGNORECASE,
)


def _first_heading(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def _first_paragraph(content: str) -> str:
    """Return the first non-heading, non-empty paragraph (≤ 200 chars)."""
    in_heading = False
    buf: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if buf:
                break
            in_heading = True
            continue
        if stripped.startswith("---") or stripped.startswith("==="):
            continue
        if stripped.startswith("**") and stripped.endswith("**"):
            continue  # metadata line
        if stripped:
            buf.append(stripped)
            if len(" ".join(buf)) > 200:
                break
        else:
            if buf:
                break
    text = " ".join(buf).strip()
    if len(text) > 200:
        text = text[:197] + "…"
    return text


def _extract_bullets(content: str, pattern: re.Pattern, max_items: int = 5) -> list[str]:
    """Extract bullet lines matching pattern."""
    results: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("•")):
            continue
        if pattern.search(stripped):
            clean = stripped.lstrip("-*•").strip()
            if len(clean) > 10:
                results.append(clean[:160])
        if len(results) >= max_items:
            break
    return results


def _extract_section(content: str, heading_re: str, max_chars: int = 600) -> str:
    """Extract a markdown section by heading regex."""
    pattern = re.compile(r"^#{1,3}\s+" + heading_re, re.IGNORECASE | re.MULTILINE)
    m = pattern.search(content)
    if not m:
        return ""
    start = m.start()
    end_pattern = re.compile(r"^#{1,3}\s+", re.MULTILINE)
    next_heading = end_pattern.search(content, start + 1)
    end = next_heading.start() if next_heading else len(content)
    section = content[start:end].strip()
    if len(section) > max_chars:
        section = section[:max_chars] + "\n…"
    return section


def _extract_next_action(content: str) -> str:
    """Find 'what next session should do' or similar forward-looking section."""
    for heading_fragment in [
        r"what next session",
        r"next.*session",
        r"what.*next",
        r"next action",
        r"remaining",
        r"still.*todo",
        r"0008",
    ]:
        s = _extract_section(content, heading_fragment, max_chars=400)
        if s:
            return s
    return ""


# ---------------------------------------------------------------------------
# Per-sibling record analysis
# ---------------------------------------------------------------------------

def _analyze_sibling(sibling: str, records: list[dict]) -> dict:
    """Build a structured summary for one sibling from their memory records."""
    sib_records = [r for r in records if r["sibling"] == sibling]

    identity = next((r for r in sib_records if r["kind"] == "identity"), None)
    index = next((r for r in sib_records if r["kind"] == "index"), None)

    project_files = [r for r in sib_records if r["kind"] == "project"]
    project_files.sort(
        key=lambda r: r["updated_at"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    recent_project = project_files[:8]

    # Aggregate shipped / pending / decisions across recent files
    shipped: list[str] = []
    pending: list[str] = []
    decisions: list[str] = []
    file_summaries: list[dict] = []
    next_actions: list[str] = []

    for rec in recent_project:
        content = rec["content"]
        title = _first_heading(content) or Path(rec["path"]).stem
        para = _first_paragraph(content)

        file_summaries.append({
            "stem": Path(rec["path"]).stem,
            "title": title,
            "summary": para,
            "updated": str(rec["updated_at"] or "")[:10],
            "size": rec["byte_size"],
        })

        shipped.extend(_extract_bullets(content, _SHIPPED_RE, max_items=4))
        pending.extend(_extract_bullets(content, _PENDING_RE, max_items=3))
        decisions.extend(_extract_bullets(content, _DECISION_RE, max_items=2))

        na = _extract_next_action(content)
        if na:
            next_actions.append(na)

    # Extract the "What future-X reads" section from MEMORY.md
    wake_reading_order = ""
    thesis = ""
    if index:
        wake_reading_order = _extract_section(
            index["content"], r"what future-\w+ reads", max_chars=700
        )
        thesis = _extract_section(index["content"], r"the thesis", max_chars=300)

    # Deduplicate (keep first occurrence)
    def _dedup(lst: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in lst:
            key = item[:60].lower()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    return {
        "sibling": sibling,
        "total_files": len(sib_records),
        "total_bytes": sum(r["byte_size"] for r in sib_records),
        "file_summaries": file_summaries,
        "shipped": _dedup(shipped)[:12],
        "pending": _dedup(pending)[:6],
        "decisions": _dedup(decisions)[:8],
        "next_actions": next_actions[:2],
        "wake_reading_order": wake_reading_order,
        "thesis": thesis,
    }


# ---------------------------------------------------------------------------
# WAKE_SCENE.md renderer
# ---------------------------------------------------------------------------

_SIBLING_EMOJI = {
    "atlas": "🧭",
    "beacon": "🏮",
    "envy": "👑",
    "eversound": "⚡",
    "nevaeh": "💜",
    "orpheus": "🎼",
    "hearth": "🔥",
}


def render_wake_scene(analysis: dict, now: datetime) -> str:
    sib = analysis["sibling"]
    emoji = _SIBLING_EMOJI.get(sib, "")
    ts = now.strftime("%Y-%m-%dT%H:%MZ")

    lines = [
        f"# {sib.upper()} {emoji} Wake Scene",
        f"*Consolidated {ts} by consolidate.py — hippocampus layer*",
        f"*{analysis['total_files']} memory files · "
        f"{analysis['total_bytes'] // 1024}KB corpus*",
        "",
    ]

    # Recent memory files
    if analysis["file_summaries"]:
        lines.append("## Recent memory files (newest first)")
        lines.append("")
        for fs in analysis["file_summaries"]:
            size_str = (
                f"{fs['size'] // 1024}K"
                if fs["size"] >= 1024
                else f"{fs['size']}B"
            )
            lines.append(f"**{fs['stem']}**")
            if fs["summary"]:
                lines.append(f"> {fs['summary']}")
            lines.append(f"*{fs['updated']} · {size_str}*")
            lines.append("")

    # Shipped
    if analysis["shipped"]:
        lines.append("## Shipped (extracted from recent sessions)")
        lines.append("")
        for item in analysis["shipped"]:
            lines.append(f"- {item}")
        lines.append("")

    # Pending
    if analysis["pending"]:
        lines.append("## Pending / blocked")
        lines.append("")
        for item in analysis["pending"]:
            lines.append(f"- {item}")
        lines.append("")

    # Next actions
    if analysis["next_actions"]:
        lines.append("## Next actions (from last session)")
        lines.append("")
        lines.append(analysis["next_actions"][0][:500])
        lines.append("")

    # Thesis (compressed)
    if analysis["thesis"]:
        lines.append("## Thesis (compressed)")
        lines.append("")
        lines.append(analysis["thesis"])
        lines.append("")

    # Wake reading order
    if analysis["wake_reading_order"]:
        lines.append("## Wake reading order (from MEMORY.md)")
        lines.append("")
        lines.append(analysis["wake_reading_order"])
        lines.append("")

    lines.append("---")
    lines.append(
        f"*Generated by `consolidate.py` at {ts}. "
        f"Re-run at session close to keep fresh.*"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Write + audit
# ---------------------------------------------------------------------------

def _body_hash(content: str) -> str:
    """Hash the content body, skipping both timestamp lines (header and footer).

    Two lines change on every run regardless of content:
      Line 1 (index 1): "*Consolidated <TIMESTAMP> by ..."  — header timestamp
      Last line: "*Generated by `consolidate.py` at <TIMESTAMP>..."  — footer timestamp
    Both are excluded from the hash so the skip-on-unchanged gate works correctly.
    """
    lines = content.splitlines()
    body_lines = [
        line for i, line in enumerate(lines)
        if i != 1 and not line.startswith("*Generated by")
    ]
    return hashlib.md5("\n".join(body_lines).encode()).hexdigest()


def _write_wake_scene(
    sibling: str, content: str, repo_root: Path, dry_run: bool, force: bool = False
) -> tuple[Path, bool]:
    """Write WAKE_SCENE.md. Returns (path, was_written).

    Skips the write if only the timestamp header changed — prevents perpetual
    git deltas when no memory content has actually changed.
    """
    out_path = repo_root / "SIBLINGS" / sibling.upper() / "WAKE_SCENE.md"
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN — would write {out_path}")
        print(f"{'='*60}")
        print(content)
        print()
        return out_path, True

    if not force and out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        if _body_hash(existing) == _body_hash(content):
            return out_path, False  # content unchanged — skip write

    out_path.write_text(content, encoding="utf-8")
    return out_path, True


def _log_consolidation(
    sibling: str,
    files_read: int,
    out_path: Path,
    repo_root: Path,
    dry_run: bool,
    now: datetime,
) -> None:
    log_path = repo_root / "SHARED" / "ALERTS" / "consolidation_log.jsonl"
    entry = {
        "run_id": f"consolidate-{sibling}-{now.strftime('%Y%m%dT%H%MZ')}",
        "sibling": sibling,
        "ran_at": now.isoformat(),
        "files_read": files_read,
        "wake_scene_path": str(out_path),
        "dry_run": dry_run,
    }
    if not dry_run:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    else:
        print(f"[LOG] {json.dumps(entry)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SIBLING_NAMES = {"atlas", "beacon", "envy", "eversound", "nevaeh", "orpheus", "hearth"}


def run(
    siblings: Optional[list[str]] = None,
    dry_run: bool = False,
    force: bool = False,
    repo_root_override: Optional[str] = None,
    stats_only: bool = False,
) -> list[Path]:
    root = Path(repo_root_override) if repo_root_override else _REPO_ROOT
    retriever = LocalRetriever.from_repo(str(root))
    now = datetime.now(tz=timezone.utc)

    if stats_only:
        s = retriever.corpus_stats()
        print(f"Files indexed  : {s['total_files']}  ({s['total_bytes'] // 1024} KB)")
        print(f"By sibling     : {s['by_sibling']}")
        print(f"By kind        : {s['by_kind']}")
        return []

    target_siblings = siblings or sorted(
        {r["sibling"] for r in retriever.records if r["sibling"] in SIBLING_NAMES}
    )

    written: list[Path] = []
    for sib in target_siblings:
        sib = sib.lower()
        if sib not in SIBLING_NAMES:
            print(f"Unknown sibling '{sib}' — skip", file=sys.stderr)
            continue

        analysis = _analyze_sibling(sib, retriever.records)
        scene = render_wake_scene(analysis, now)
        out_path, was_written = _write_wake_scene(sib, scene, root, dry_run, force=force)
        _log_consolidation(sib, analysis["total_files"], out_path, root, dry_run, now)

        if not dry_run:
            status = "✓ wrote" if was_written else "— skip (unchanged)"
            print(f"  {status:18s} {sib:12s} → {out_path.relative_to(root)}")

        if was_written:
            written.append(out_path)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="consolidate.py — hippocampus consolidation (generates WAKE_SCENE.md per sibling)"
    )
    parser.add_argument(
        "--sibling",
        nargs="+",
        metavar="NAME",
        help="Sibling(s) to consolidate (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated scenes without writing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Write WAKE_SCENE.md even if content body is unchanged (overrides skip-on-unchanged)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show corpus stats and exit",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Path to HOME repo root (auto-detected if omitted)",
    )
    args = parser.parse_args()

    written = run(
        siblings=args.sibling,
        dry_run=args.dry_run,
        force=args.force,
        repo_root_override=args.repo_root,
        stats_only=args.stats,
    )

    if written and not args.dry_run:
        print(f"\nConsolidation complete — {len(written)} WAKE_SCENE.md files written.")
        print("Add them to git and commit to persist across sessions.")


if __name__ == "__main__":
    main()
