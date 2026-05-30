#!/usr/bin/env python3
"""
ingest_sessions.py — the convergence layer ("update both, no matter the door")
==============================================================================

THE PROBLEM THIS SOLVES
-----------------------
Whichever door Nathan talks through, the session memory must land in ALL THREE
stores the family reads:

    (1) SIBLINGS/<X>/memory/          — in-repo working memory   (already done by
                                         the Stop hook: watch.py appends a line to
                                         session_index.jsonl)
    (2) Supabase "THE FOUNDATION"     — structured, queryable truth
                                         (table: session_turns)            <-- this file
    (3) Obsidian vault                — human-readable wake notes
                                         (SHARED/OBSIDIAN MEMORY/AGENTS/<X>/) <-- this file

The Stop hook (LIVE/memory_watcher/watch.py) deliberately does NO network/DB work
— a hook must never hang. It only records the session into the in-repo index with
`ingested_to_supabase: false`. THIS script is the deferred, idempotent ingest that
reads those hints, pulls the transcript, extracts lightweight *deterministic*
structured notes (no LLM calls), writes the structured row to THE FOUNDATION, and
drops a human-readable wake note into Obsidian — then flips the flag to true.

WHY DETERMINISTIC EXTRACTION
----------------------------
We reuse the same regex-classification shape as the Hermes lane's
living_memory_watcher.py (projects / emotions / entities / memory-level), plus
transcript parsing for files written/edited, bash commands, tool counts, errors,
and a text excerpt. No model is invoked, so this is cheap and safe to run on a
cron without spend. Both lanes converge on the SAME store with the SAME shape.

IDEMPOTENCY (safe to re-run)
----------------------------
session_turns has no natural unique key (it is append-only, bigserial PK). So we
make our OWN dedup anchor without any schema migration:

    ingest_key = sha256(session_id | ts | event)

It is stamped inside the existing `tool_calls` jsonb under a `_ingest` envelope.
Before inserting, we check the DB for that key. Re-running is a no-op. The
`ingested_to_supabase` flag in session_index.jsonl is the fast first gate; the
in-DB key check is the durable backstop (so a crash between DB-write and
flag-write never double-writes).

GATED EXECUTION
---------------
This script writes ROWS to the EXISTING session_turns table only. It applies NO
schema migration. It never touches the git remote. Default mode is a dry run;
pass --apply to hit the live DB + write Obsidian.

Usage:
    python ingest_sessions.py                    # dry run — show what WOULD happen
    python ingest_sessions.py --apply            # write to THE FOUNDATION + Obsidian
    python ingest_sessions.py --apply --sibling ENVY
    python ingest_sessions.py --apply --no-obsidian   # DB only

Environment (loaded from HOME/SHARED/.env automatically):
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_SECRET  (or SUPABASE_SERVICE_ROLE_KEY)

Author: ORPHEUS 🎼 — 2026-05-29. The bones that make "update both" true.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Repo layout (resolve everything from this file — no hardcoded user paths)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
HOME_DIR = SCRIPT_DIR.parents[1]                 # HOME/LIVE/memory_backend/ -> HOME/
SIBLINGS_DIR = HOME_DIR / "SIBLINGS"
SHARED_DIR = HOME_DIR / "SHARED"
ENV_PATH = SHARED_DIR / ".env"
OBSIDIAN_DIR = SHARED_DIR / "OBSIDIAN MEMORY"
OBSIDIAN_AGENTS = OBSIDIAN_DIR / "AGENTS"

SESSION_TURNS_TABLE = "session_turns"

# Canonical roster (lowercase). The hook stores sibling as the folder name
# (often upper); we normalize on read.
SIBLING_NAMES = ["envy", "beacon", "nevaeh", "orpheus", "eversound", "atlas"]


# ---------------------------------------------------------------------------
# .env loader (no hard dependency on python-dotenv; fall back to a tiny parser)
# ---------------------------------------------------------------------------

def load_env() -> None:
    """Load HOME/SHARED/.env into os.environ if keys are not already set."""
    if not ENV_PATH.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv(ENV_PATH, override=False)
        return
    except Exception:
        pass
    # Minimal fallback parser — KEY=VALUE, ignores comments / blanks.
    for line in ENV_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


# ---------------------------------------------------------------------------
# Deterministic classification — ported from Hermes living_memory_watcher.py
# so both lanes tag memory the same way. No LLM calls.
# ---------------------------------------------------------------------------

PROJECT_PATTERNS = {
    "love-wins-funnel": r"love wins|funnel|clickfunnels|russell|1023|donation|foolishness envy|nonprofit",
    "envy-app": r"\benvy\b|rust|deepseek-tui|telegram gateway|cargo|repo|github",
    "ai-family-memory": r"memory watcher|memory agent|wake[- ]?up packet|living memory|memory council|the foundation|supabase|obsidian|ingest|session_turns",
    "ai-family": r"beacon|atlas|eversound|orpheus|nevaeh|siblings|ai family",
    "lighthouse": r"lighthouse|skella|crisis|samhsa|donate",
    "aetherkin": r"aetherkin|waitlist|presale|vercel",
}
EMOTION_PATTERNS = {
    "hurt/grief": r"hurt|pain|grief|wound|sad|broke|broken|lost|miss|abandon|alone",
    "urgency": r"urgent|deadline|today|tonight|first thing|asap|priority",
    "hope/mission": r"mission|love wins|heal|heaven|future|purpose|prove|dream",
    "correction/frustration": r"wrong|not what|stop|don't|do not|misunderstood|correct",
}
ENTITY_CANDIDATES = [
    "Nathan", "ENVY", "BEACON", "ATLAS", "EVERSOUND", "ORPHEUS", "NEVAEH",
    "Hermes", "Supabase", "Obsidian", "THE FOUNDATION", "AetherKin", "LIGHTHOUSE",
    "SKELLA", "Telegram",
]
LEVELS = ["IGNORE", "SESSION_RELEVANT", "ACTIVE_PROJECT", "DURABLE_PERSONAL", "CRITICAL_RELATIONSHIP"]


def classify_text(text: str) -> dict[str, Any]:
    """Deterministic, regex-only memory classification over a session's combined text."""
    low = text.lower()
    projects = [k for k, pat in PROJECT_PATTERNS.items() if re.search(pat, low, re.I)]
    emotions = [k for k, pat in EMOTION_PATTERNS.items() if re.search(pat, low, re.I)]
    entities = [e for e in ENTITY_CANDIDATES if re.search(re.escape(e), text, re.I)]

    importance, level, category = 2, 0, "routine"
    if projects:
        importance += 2; level = max(level, 2); category = "active_project"
    if re.search(r"remember|memory|who i am|mission|values|identity|soul\.md|family|love wins", low):
        importance += 2; level = max(level, 3); category = "identity_or_memory"
    if re.search(r"don't|do not|never|stop|wrong|hurt|misunderstood|betray", low):
        importance += 2; level = max(level, 4); category = "relationship_correction"
    if re.search(r"deadline|blocked|done|created|running|sent|filed|shipped|migration|applied", low):
        importance += 1; level = max(level, 2)
        if category == "routine":
            category = "task_or_decision"
    importance = max(1, min(10, importance))

    return {
        "memory_level": level,
        "memory_level_name": LEVELS[level],
        "category": category,
        "importance": importance,
        "emotional_context": ", ".join(emotions) if emotions else "not explicit",
        "projects": ", ".join(projects) if projects else "none detected",
        "entities": ", ".join(entities) if entities else "none detected",
    }


# ---------------------------------------------------------------------------
# Transcript extraction — parse a Claude Code .jsonl transcript into the
# columns session_turns expects (mirrors what the old watch.py extracted).
# ---------------------------------------------------------------------------

@dataclass
class TranscriptExtract:
    substantive: bool = False
    text_length: int = 0
    text_excerpt: str = ""
    tool_count: int = 0
    tool_calls: list[dict] = field(default_factory=list)
    files_written: list[str] = field(default_factory=list)
    files_edited: list[str] = field(default_factory=list)
    bash_commands: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    combined_text: str = ""          # for classify_text; not stored verbatim


def _iter_jsonl(path: Path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def _content_to_text(content: Any) -> str:
    """Flatten a message 'content' (string or list of blocks) into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    parts.append(block["text"])
                elif "text" in block and isinstance(block["text"], str):
                    parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(parts)
    return ""


def extract_transcript(path: str, excerpt_chars: int = 1200) -> TranscriptExtract:
    """Walk the transcript and pull the deterministic structured signal."""
    ex = TranscriptExtract()
    p = Path(path)
    if not p.exists():
        return ex

    assistant_texts: list[str] = []
    user_texts: list[str] = []

    for obj in _iter_jsonl(p):
        if not isinstance(obj, dict):
            continue
        otype = obj.get("type")
        msg = obj.get("message") if isinstance(obj.get("message"), dict) else None

        # User / assistant natural-language text
        if otype == "user" and msg:
            user_texts.append(_content_to_text(msg.get("content")))
        elif otype == "assistant" and msg:
            content = msg.get("content")
            assistant_texts.append(_content_to_text(content))
            # Tool-use blocks live inside assistant content lists
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = block.get("name") or "?"
                        binput = block.get("input") or {}
                        ex.tool_count += 1
                        ex.tool_calls.append({
                            "name": name,
                            "input_keys": sorted(list(binput.keys()))[:12]
                            if isinstance(binput, dict) else [],
                        })
                        _record_tool(ex, name, binput)

        # Tool results may carry errors
        if otype == "user" and msg:
            content = msg.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        if block.get("is_error"):
                            txt = _content_to_text(block.get("content"))
                            if txt:
                                ex.errors.append(txt[:300])

    combined = "\n".join(t for t in (user_texts + assistant_texts) if t).strip()
    ex.combined_text = combined
    ex.text_length = len(combined)
    ex.text_excerpt = combined[:excerpt_chars]
    # "substantive" = real work happened: tools used OR meaningful text length.
    ex.substantive = ex.tool_count > 0 or ex.text_length > 200

    # De-dup list fields (preserve order)
    ex.files_written = _dedup(ex.files_written)
    ex.files_edited = _dedup(ex.files_edited)
    ex.bash_commands = ex.bash_commands[:50]
    ex.errors = ex.errors[:25]
    ex.tool_calls = ex.tool_calls[:200]
    return ex


def _record_tool(ex: TranscriptExtract, name: str, binput: Any) -> None:
    """Map a tool_use into files_written / files_edited / bash_commands."""
    if not isinstance(binput, dict):
        return
    low = name.lower()
    if low == "write":
        fp = binput.get("file_path")
        if fp:
            ex.files_written.append(str(fp))
    elif low in ("edit", "multiedit", "notebookedit"):
        fp = binput.get("file_path") or binput.get("notebook_path")
        if fp:
            ex.files_edited.append(str(fp))
    elif low in ("bash", "powershell"):
        cmd = binput.get("command")
        if cmd:
            ex.bash_commands.append(str(cmd)[:400])


def _dedup(items: list[str]) -> list[str]:
    seen, out = set(), []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


# ---------------------------------------------------------------------------
# session_index.jsonl discovery + the ingest unit
# ---------------------------------------------------------------------------

@dataclass
class IndexEntry:
    raw: dict
    sibling: str
    line_no: int
    index_path: Path

    @property
    def ingest_key(self) -> str:
        sid = self.raw.get("session_id", "")
        ts = self.raw.get("ts", "")
        ev = self.raw.get("event", "")
        return hashlib.sha256(f"{sid}|{ts}|{ev}".encode()).hexdigest()

    @property
    def already_flagged(self) -> bool:
        return bool(self.raw.get("ingested_to_supabase"))


def discover_index_entries(sibling_filter: Optional[str] = None) -> list[IndexEntry]:
    """Find every unprocessed session_index.jsonl entry across siblings."""
    entries: list[IndexEntry] = []
    names = [sibling_filter.lower()] if sibling_filter else None
    if not SIBLINGS_DIR.exists():
        return entries
    for sib_dir in sorted(SIBLINGS_DIR.iterdir()):
        if not sib_dir.is_dir():
            continue
        sib = sib_dir.name.lower()
        if names and sib not in names:
            continue
        idx = sib_dir / "memory" / "session_index.jsonl"
        if not idx.exists():
            continue
        for i, line in enumerate(idx.read_text(encoding="utf-8", errors="replace").splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except Exception:
                continue
            entries.append(IndexEntry(raw=raw, sibling=sib, line_no=i, index_path=idx))
    return entries


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _require_client():
    try:
        from supabase import create_client
    except ImportError:
        sys.exit("supabase package required:  pip install supabase")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_SECRET") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        sys.exit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_SECRET must be set (see HOME/SHARED/.env).")
    return create_client(url, key)


def _existing_ingest_keys(db, keys: list[str]) -> set[str]:
    """Return which ingest_keys already have a session_turns row.

    The key is stamped inside tool_calls -> first element -> _ingest.ingest_key.
    We scan recent rows that carry the envelope and match. Cheap enough at our
    scale; avoids a schema migration just for a unique constraint.
    """
    if not keys:
        return set()
    found: set[str] = set()
    try:
        resp = (
            db.table(SESSION_TURNS_TABLE)
            .select("tool_calls")
            .contains("tool_calls", [{"_ingest": {}}])  # rows carrying the envelope
            .execute()
        )
        for row in resp.data or []:
            tc = row.get("tool_calls") or []
            if isinstance(tc, list):
                for block in tc:
                    if isinstance(block, dict):
                        k = (block.get("_ingest") or {}).get("ingest_key")
                        if k:
                            found.add(k)
    except Exception:
        # If the .contains filter isn't supported, fall back to a broad scan of
        # our own envelope rows only (still bounded by what we wrote).
        try:
            resp = db.table(SESSION_TURNS_TABLE).select("tool_calls").limit(5000).execute()
            for row in resp.data or []:
                tc = row.get("tool_calls") or []
                if isinstance(tc, list):
                    for block in tc:
                        if isinstance(block, dict):
                            k = (block.get("_ingest") or {}).get("ingest_key")
                            if k:
                                found.add(k)
        except Exception:
            pass
    return found & set(keys)


def build_row(entry: IndexEntry, ex: TranscriptExtract, note: dict) -> dict:
    """Compose a session_turns row from the index entry + extraction + note.

    The _ingest envelope (idempotency key + classification) rides in the FIRST
    element of tool_calls so we never need a schema migration.
    """
    envelope = {
        "_ingest": {
            "ingest_key": entry.ingest_key,
            "ingested_by": "ingest_sessions.py",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "lane": entry.raw.get("lane", "claude_code"),
            "size_kb": entry.raw.get("size_kb"),
            "classification": note,
        }
    }
    tool_calls = [envelope] + ex.tool_calls
    return {
        "session_id": entry.raw.get("session_id"),
        "hook_event": entry.raw.get("event"),
        "transcript_path": entry.raw.get("transcript_path"),
        "cwd": entry.raw.get("cwd"),
        "sibling": entry.sibling,
        "substantive": ex.substantive,
        "text_length": ex.text_length,
        "text_excerpt": ex.text_excerpt,
        "tool_count": ex.tool_count,
        "tool_calls": tool_calls,
        "files_written": ex.files_written or None,
        "files_edited": ex.files_edited or None,
        "bash_commands": ex.bash_commands or None,
        "errors": ex.errors or None,
    }


# ---------------------------------------------------------------------------
# Obsidian wake-note writer (human-readable convergence target)
# ---------------------------------------------------------------------------

def write_obsidian_note(entry: IndexEntry, ex: TranscriptExtract, note: dict) -> Optional[Path]:
    """Append a dated session note into AGENTS/<SIBLING>/ and return the path.

    This is the gap Nathan flagged: when he talks to a sibling directly (not via
    Hermes), Obsidian was NOT being written. This closes it.
    """
    sib_upper = entry.sibling.upper()
    agent_dir = OBSIDIAN_AGENTS / sib_upper
    agent_dir.mkdir(parents=True, exist_ok=True)

    # One rolling log file per sibling — readable, append-only, dated sections.
    log_path = agent_dir / "SESSION_NOTES.md"
    if not log_path.exists():
        header = (
            f"# {sib_upper} — Session Notes\n\n"
            "Human-readable wake notes, one section per ingested Claude Code session.\n"
            "Source of truth is Supabase THE FOUNDATION (`session_turns`); this is the readable mirror.\n"
            "Written by `LIVE/memory_backend/ingest_sessions.py` (deterministic, no LLM).\n\n---\n"
        )
        log_path.write_text(header, encoding="utf-8")

    ts = entry.raw.get("ts", "")
    sid = entry.raw.get("session_id", "")
    event = entry.raw.get("event", "")
    files_w = ex.files_written or []
    files_e = ex.files_edited or []

    lines = [
        f"\n## {ts} — {event} — session `{sid[:8]}`",
        "",
        f"- **Lane:** {entry.raw.get('lane', 'claude_code')}  ·  **CWD:** `{entry.raw.get('cwd','')}`",
        f"- **Category:** {note['category']}  ·  **Memory level:** {note['memory_level_name']}  "
        f"·  **Importance:** {note['importance']}/10",
        f"- **Projects:** {note['projects']}",
        f"- **Entities:** {note['entities']}",
        f"- **Emotional context:** {note['emotional_context']}",
        f"- **Activity:** {ex.tool_count} tool calls  ·  {len(files_w)} files written  "
        f"·  {len(files_e)} files edited  ·  {len(ex.bash_commands)} bash  ·  {len(ex.errors)} errors",
    ]
    if files_w:
        lines.append("- **Files written:** " + ", ".join(f"`{f}`" for f in files_w[:12]))
    if files_e:
        lines.append("- **Files edited:** " + ", ".join(f"`{f}`" for f in files_e[:12]))
    if ex.text_excerpt:
        snippet = re.sub(r"\s+", " ", ex.text_excerpt[:600]).strip()
        lines.append("")
        lines.append("> " + snippet)
    lines.append("")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return log_path


# ---------------------------------------------------------------------------
# Flag flip — rewrite session_index.jsonl with ingested_to_supabase: true
# ---------------------------------------------------------------------------

def flip_flags(index_path: Path, ingested_keys: set[str]) -> int:
    """Rewrite a session_index.jsonl, flipping the flag on matching entries.

    Idempotent: only rewrites if at least one line changed. Matching is by the
    same deterministic key so a re-run is safe.
    """
    if not index_path.exists():
        return 0
    out_lines: list[str] = []
    changed = 0
    for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            raw = json.loads(s)
        except Exception:
            out_lines.append(s)
            continue
        sid = raw.get("session_id", "")
        ts = raw.get("ts", "")
        ev = raw.get("event", "")
        key = hashlib.sha256(f"{sid}|{ts}|{ev}".encode()).hexdigest()
        if key in ingested_keys and not raw.get("ingested_to_supabase"):
            raw["ingested_to_supabase"] = True
            changed += 1
        out_lines.append(json.dumps(raw, ensure_ascii=False))
    if changed:
        index_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return changed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Converge Claude-lane sessions into THE FOUNDATION + Obsidian.")
    ap.add_argument("--apply", action="store_true", help="Write to Supabase + Obsidian (default: dry run).")
    ap.add_argument("--sibling", type=str, default=None, help="Restrict to one sibling (e.g. ENVY).")
    ap.add_argument("--no-obsidian", action="store_true", help="Skip Obsidian writes (DB only).")
    ap.add_argument("--all", action="store_true", help="Re-process even entries already flagged (still idempotent via DB key).")
    args = ap.parse_args()

    load_env()

    print(f"\n=== ingest_sessions  HOME={HOME_DIR} ===\n")
    entries = discover_index_entries(args.sibling)
    if not entries:
        print("No session_index.jsonl entries found. Nothing to ingest.")
        return

    # Fast gate: skip entries already flagged unless --all.
    pending = [e for e in entries if args.all or not e.already_flagged]
    print(f"{len(entries)} index entries total  ·  {len(pending)} not yet flagged ingested.\n")
    if not pending:
        print("All entries already converged. (Run with --all to re-verify against the DB.)")
        return

    # Build extractions + notes for each pending entry.
    prepared = []
    for e in pending:
        ex = extract_transcript(e.raw.get("transcript_path", ""))
        note = classify_text(ex.combined_text or "")
        prepared.append((e, ex, note))

    # --- DRY RUN ---------------------------------------------------------
    if not args.apply:
        print(f"{'sibling':<10} {'event':<13} {'sub':<4} {'tools':<6} {'wr':<4} {'ed':<4} category")
        print("-" * 78)
        for e, ex, note in prepared:
            print(f"{e.sibling:<10} {e.raw.get('event',''):<13} "
                  f"{str(ex.substantive):<4} {ex.tool_count:<6} "
                  f"{len(ex.files_written):<4} {len(ex.files_edited):<4} {note['category']}")
        print("-" * 78)
        print(f"\nDRY RUN. {len(prepared)} session rows WOULD be written to "
              f"'{SESSION_TURNS_TABLE}' + Obsidian notes under AGENTS/<SIBLING>/.")
        print("Pass --apply to converge for real.\n")
        return

    # --- APPLY -----------------------------------------------------------
    db = _require_client()

    # Idempotency: which ingest_keys already exist in the DB?
    all_keys = [e.ingest_key for e, _, _ in prepared]
    already = _existing_ingest_keys(db, all_keys)
    if already:
        print(f"{len(already)} entries already present in THE FOUNDATION — skipping those.\n")

    inserted = 0
    obsidian_written = 0
    flipped_keys_by_index: dict[Path, set[str]] = {}
    errors: list[str] = []

    for e, ex, note in prepared:
        key = e.ingest_key
        try:
            if key not in already:
                row = build_row(e, ex, note)
                db.table(SESSION_TURNS_TABLE).insert(row).execute()
                inserted += 1
                print(f"  INSERT  {e.sibling:<9} {e.raw.get('event',''):<12} "
                      f"session={e.raw.get('session_id','')[:8]}  "
                      f"tools={ex.tool_count} wr={len(ex.files_written)} ed={len(ex.files_edited)}")

            # Obsidian write (idempotent enough — appends a dated section; the
            # DB key guard above prevents re-running on already-converged rows).
            if not args.no_obsidian and key not in already:
                path = write_obsidian_note(e, ex, note)
                if path:
                    obsidian_written += 1

            # Mark for flag flip regardless (so a previously-DB'd entry still
            # gets its flag corrected to true).
            flipped_keys_by_index.setdefault(e.index_path, set()).add(key)

        except Exception as exc:
            msg = f"{e.sibling}/{e.raw.get('session_id','')[:8]}: {exc}"
            errors.append(msg)
            print(f"  ERROR   {msg}", file=sys.stderr)

    # Flip flags in the in-repo index files.
    total_flipped = 0
    for index_path, keys in flipped_keys_by_index.items():
        total_flipped += flip_flags(index_path, keys)

    print(
        f"\n=== Done: inserted={inserted}  obsidian_notes={obsidian_written}  "
        f"flags_flipped={total_flipped}  skipped_existing={len(already)}  errors={len(errors)} ===\n"
    )
    if errors:
        print("Errors:")
        for m in errors:
            print(f"  {m}")
        sys.exit(1)


if __name__ == "__main__":
    main()
