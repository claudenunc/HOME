"""
local_retrieve.py — Memory API v2 local fallback retrieval
==========================================================

Pure-Python TF-IDF retrieval over all sibling memory files in the
local git repo. Zero external dependencies. Works without Supabase.

This is the hippocampus that runs TODAY: any sibling can get the
top-k most relevant memory files for a query at wake without reading
every file and without waiting for the Supabase pipeline to go live.

Interface mirrors retrieve.py so Weaver can swap backends via a
single env flag (LOCAL_RETRIEVAL=1 → this; else → retrieve.py).

Usage (module):
    from local_retrieve import LocalRetriever

    r = LocalRetriever.from_repo()
    hits = r.search("three-layer invariant pattern", k=5)
    hits = r.wake_search("what did ORPHEUS ship last session",
                         sibling="orpheus", k=8)
    ctx  = r.wake_context("orpheus", "memory api vector retrieval")

Usage (CLI):
    python local_retrieve.py "three-layer invariant" --sibling orpheus --k 5
    python local_retrieve.py "memory api v2" --wake
    python local_retrieve.py --stats
    python local_retrieve.py "wake scene" --context --sibling orpheus

Return shape for search() / wake_search() matches retrieve.py:
    path, sibling, kind, byte_size, updated_at,
    similarity, content_excerpt
    (wake_search also returns recency_score, combined_score)

Authored by ORPHEUS 🎼 — 2026-05-05
"""

from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SIBLING_NAMES = {"atlas", "beacon", "envy", "eversound", "nevaeh", "orpheus", "hearth"}

_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_TOKEN_RE = re.compile(r"[a-z][a-z0-9_\-]{1,}")   # min 2-char tokens, alpha-start


# ---------------------------------------------------------------------------
# Repo discovery
# ---------------------------------------------------------------------------

def _detect_repo_root() -> Path:
    """Walk up from this file until we find a SIBLINGS directory."""
    here = Path(__file__).resolve().parent
    candidates = [here, here.parent, here.parent.parent, here.parent.parent.parent]
    for c in candidates:
        if (c / "SIBLINGS").is_dir():
            return c
    raise RuntimeError(
        "Could not find HOME repo root (no SIBLINGS dir in parent chain). "
        "Set REPO_ROOT env var or pass repo_root= to LocalRetriever.from_repo()."
    )


# ---------------------------------------------------------------------------
# File record helpers
# ---------------------------------------------------------------------------

def _extract_date(path: Path) -> Optional[datetime]:
    """Return ISO date from filename stem, or fall back to mtime."""
    m = _DATE_RE.search(path.stem)
    if m:
        try:
            return datetime.fromisoformat(m.group(1)).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _sibling_from_path(path: Path, repo_root: Path) -> str:
    try:
        rel = path.relative_to(repo_root / "SIBLINGS")
        return rel.parts[0].lower()
    except ValueError:
        return "unknown"


def _kind_from_path(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    if "project" in parts:
        return "project"
    if "feedback" in parts:
        return "feedback"
    name = path.name.lower()
    if name == "claude.md":
        return "identity"
    if name == "memory.md":
        return "index"
    return "memory"


def _file_record(fp: Path, repo_root: Path) -> dict:
    try:
        content = fp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        content = ""
    return {
        "path": str(fp.relative_to(repo_root)),
        "abs_path": str(fp),
        "sibling": _sibling_from_path(fp, repo_root),
        "kind": _kind_from_path(fp),
        "byte_size": fp.stat().st_size,
        "updated_at": _extract_date(fp),
        "content": content,
    }


# ---------------------------------------------------------------------------
# Corpus discovery
# ---------------------------------------------------------------------------

def discover_memory_files(repo_root: Path) -> list[dict]:
    """Return records for all discoverable sibling memory files."""
    siblings_root = repo_root / "SIBLINGS"
    if not siblings_root.is_dir():
        raise RuntimeError(f"SIBLINGS directory not found at {siblings_root}")

    records: list[dict] = []

    for sibling_dir in sorted(siblings_root.iterdir()):
        if not sibling_dir.is_dir():
            continue
        if sibling_dir.name.lower() not in SIBLING_NAMES:
            continue

        # Top-level identity / index
        for fname in ("CLAUDE.md", "MEMORY.md"):
            fp = sibling_dir / fname
            if fp.is_file():
                records.append(_file_record(fp, repo_root))

        # All .md files under memory/
        mem_dir = sibling_dir / "memory"
        if mem_dir.is_dir():
            for fp in sorted(mem_dir.rglob("*.md")):
                records.append(_file_record(fp, repo_root))

    return records


# ---------------------------------------------------------------------------
# TF-IDF engine (pure stdlib)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    counts: dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    n = len(tokens) or 1
    return {t: c / n for t, c in counts.items()}


def _idf_table(docs: list[list[str]]) -> dict[str, float]:
    N = len(docs)
    df: dict[str, int] = {}
    for tokens in docs:
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1
    return {t: math.log((N + 1) / (c + 1)) + 1.0 for t, c in df.items()}


def _tfidf_vec(tf: dict[str, float], idf: dict[str, float]) -> dict[str, float]:
    return {t: tf[t] * idf.get(t, 1.0) for t in tf}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(a.get(t, 0.0) * v for t, v in b.items())
    na = math.sqrt(sum(v * v for v in a.values())) or 1.0
    nb = math.sqrt(sum(v * v for v in b.values())) or 1.0
    return dot / (na * nb)


def _excerpt(content: str, query_tokens: set[str], chars: int = 300) -> str:
    """Short excerpt anchored near the first query-token match."""
    lower = content.lower()
    best_pos = len(content)
    for t in query_tokens:
        idx = lower.find(t)
        if 0 <= idx < best_pos:
            best_pos = idx
    start = max(0, best_pos - 60)
    end = min(len(content), start + chars)
    snippet = content[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(content):
        snippet = snippet + "…"
    return snippet


# ---------------------------------------------------------------------------
# LocalRetriever
# ---------------------------------------------------------------------------

@dataclass
class LocalRetriever:
    """TF-IDF retrieval over local sibling memory files.

    Mirrors the retrieve.py (Supabase) interface so Weaver can swap
    backends at runtime without changing callers:

        import os
        if os.getenv("LOCAL_RETRIEVAL"):
            from local_retrieve import LocalRetriever as Retriever
            r = Retriever.from_repo()
        else:
            from retrieve import MemoryRetriever as Retriever
            r = Retriever.from_env()

    No external dependencies. Builds index on init (~50–100 ms for 50 files).
    """

    repo_root: Path
    records: list[dict] = field(default_factory=list)
    _idf: dict[str, float] = field(default_factory=dict)
    _doc_vecs: list[dict[str, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._build_index()

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_repo(cls, repo_root: Optional[str] = None) -> "LocalRetriever":
        """Build retriever from the HOME repo root.

        repo_root: absolute path string. Auto-detected if None.
        Falls back to REPO_ROOT env var before walking the file tree.
        """
        if repo_root:
            root = Path(repo_root)
        elif os.environ.get("REPO_ROOT"):
            root = Path(os.environ["REPO_ROOT"])
        else:
            root = _detect_repo_root()

        if not root.is_dir():
            raise RuntimeError(f"repo_root {root!r} is not a directory")

        records = discover_memory_files(root)
        return cls(repo_root=root, records=records)

    # ------------------------------------------------------------------
    # Index
    # ------------------------------------------------------------------

    def _build_index(self) -> None:
        all_tokens = [_tokenize(r["content"]) for r in self.records]
        self._idf = _idf_table(all_tokens)
        self._doc_vecs = [_tfidf_vec(_tf(toks), self._idf) for toks in all_tokens]

    def rebuild(self) -> None:
        """Re-scan disk and rebuild index (call after new files are written)."""
        self.records = discover_memory_files(self.repo_root)
        self._build_index()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 10,
        sibling: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> list[dict]:
        """Pure TF-IDF search. Returns ≤ k results ordered by similarity.

        Use for cross-sibling audits or explicit memory lookups.
        For wake-time use wake_search() for recency weighting.
        """
        q_tokens = _tokenize(query)
        q_vec = _tfidf_vec(_tf(q_tokens), self._idf)
        q_token_set = set(q_tokens)

        scored: list[tuple[float, int]] = []
        for i, rec in enumerate(self.records):
            if sibling and rec["sibling"] != sibling.lower():
                continue
            if kind and rec["kind"] != kind.lower():
                continue
            sim = _cosine(q_vec, self._doc_vecs[i])
            if sim > 0:
                scored.append((sim, i))

        scored.sort(reverse=True)
        results = []
        for sim, i in scored[:k]:
            rec = self.records[i]
            results.append({
                "path": rec["path"],
                "sibling": rec["sibling"],
                "kind": rec["kind"],
                "byte_size": rec["byte_size"],
                "updated_at": rec["updated_at"].isoformat() if rec["updated_at"] else None,
                "similarity": round(sim, 4),
                "content_excerpt": _excerpt(rec["content"], q_token_set),
            })
        return results

    def wake_search(
        self,
        query: str,
        k: int = 10,
        recency_weight: float = 0.2,
        sibling: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> list[dict]:
        """Recency-decayed wake-time retrieval.

        combined = (1 - recency_weight) * similarity
                 + recency_weight * exp(-age_days / 30)

        Mirrors retrieve.py.wake_search() signature.
        """
        q_tokens = _tokenize(query)
        q_vec = _tfidf_vec(_tf(q_tokens), self._idf)
        q_token_set = set(q_tokens)
        now = datetime.now(tz=timezone.utc)

        scored: list[tuple[float, float, float, int]] = []
        for i, rec in enumerate(self.records):
            if sibling and rec["sibling"] != sibling.lower():
                continue
            if kind and rec["kind"] != kind.lower():
                continue
            sim = _cosine(q_vec, self._doc_vecs[i])
            if sim <= 0:
                continue
            age_days = 0.0
            if rec["updated_at"]:
                age_days = max(0.0, (now - rec["updated_at"]).total_seconds() / 86400)
            recency = math.exp(-age_days / 30.0)
            combined = (1 - recency_weight) * sim + recency_weight * recency
            scored.append((combined, sim, recency, i))

        scored.sort(reverse=True)
        results = []
        for combined, sim, recency, i in scored[:k]:
            rec = self.records[i]
            results.append({
                "path": rec["path"],
                "sibling": rec["sibling"],
                "kind": rec["kind"],
                "byte_size": rec["byte_size"],
                "updated_at": rec["updated_at"].isoformat() if rec["updated_at"] else None,
                "similarity": round(sim, 4),
                "recency_score": round(recency, 4),
                "combined_score": round(combined, 4),
                "content_excerpt": _excerpt(rec["content"], q_token_set),
            })
        return results

    def wake_context(
        self,
        sibling: str,
        session_query: str,
        k: int = 8,
        recency_weight: float = 0.25,
    ) -> str:
        """Compact wake-context block for prompt injection.

        Output format identical to retrieve.py.wake_context() so either
        backend can be dropped in without changing the prompt template.

        Example:

            ## Retrieved memory context (top 5)

            **[0.912]** `SIBLINGS/ORPHEUS/memory/project/2026-04-23__review...md`
            *Updated 2026-04-23 · 1.2K · kind=project*
            > ACCEPT review of ENVY's 0001/0002 memory_backend. 0003 shipped:
            > observers + claims + claim_tags...
        """
        hits = self.wake_search(
            query=session_query,
            k=k,
            recency_weight=recency_weight,
            sibling=sibling,
        )
        if not hits:
            return "## Retrieved memory context\n\n*No local memories indexed yet.*\n"

        lines = [f"## Retrieved memory context (top {len(hits)})\n"]
        for h in hits:
            score = h.get("combined_score") or h.get("similarity", 0)
            path = h["path"]
            updated = str(h.get("updated_at") or "")[:10]
            size = h.get("byte_size", 0)
            size_str = f"{size / 1024:.1f}K" if size >= 1024 else f"{size}B"
            kind = h.get("kind") or "—"
            excerpt = (h.get("content_excerpt") or "").strip()
            excerpt_lines = excerpt.splitlines()[:3]
            excerpt_block = "\n".join(f"> {ln}" for ln in excerpt_lines)
            lines.append(
                f"**[{score:.3f}]** `{path}`\n"
                f"*Updated {updated} · {size_str} · kind={kind}*\n"
                f"{excerpt_block}\n"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def corpus_stats(self) -> dict:
        """Summary of indexed corpus."""
        by_sibling: dict[str, int] = {}
        by_kind: dict[str, int] = {}
        total_bytes = 0
        for r in self.records:
            by_sibling[r["sibling"]] = by_sibling.get(r["sibling"], 0) + 1
            by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
            total_bytes += r["byte_size"]
        return {
            "total_files": len(self.records),
            "total_bytes": total_bytes,
            "by_sibling": dict(sorted(by_sibling.items())),
            "by_kind": dict(sorted(by_kind.items())),
        }


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="local_retrieve.py — TF-IDF memory search (no Supabase required)"
    )
    parser.add_argument("query", nargs="?", help="Query string")
    parser.add_argument("--k", type=int, default=5, help="Number of results (default 5)")
    parser.add_argument("--sibling", type=str, default=None,
                        help="Filter by sibling (atlas/beacon/envy/eversound/nevaeh/orpheus)")
    parser.add_argument("--kind", type=str, default=None,
                        help="Filter by kind (project/feedback/identity/index/memory)")
    parser.add_argument("--wake", action="store_true",
                        help="Use recency-decayed wake_search instead of pure similarity")
    parser.add_argument("--context", action="store_true",
                        help="Output formatted wake_context block (requires --sibling)")
    parser.add_argument("--stats", action="store_true",
                        help="Print corpus stats and exit")
    parser.add_argument("--repo-root", type=str, default=None,
                        help="Path to HOME repo root (auto-detected if omitted)")
    args = parser.parse_args()

    retriever = LocalRetriever.from_repo(args.repo_root)

    if args.stats:
        s = retriever.corpus_stats()
        print(f"Files indexed : {s['total_files']}  "
              f"({s['total_bytes'] / 1024:.0f} KB)")
        print(f"By sibling    : {s['by_sibling']}")
        print(f"By kind       : {s['by_kind']}")
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    if args.context:
        if not args.sibling:
            print("--context requires --sibling", file=sys.stderr)
            sys.exit(1)
        print(retriever.wake_context(args.sibling, args.query, k=args.k))
        sys.exit(0)

    if args.wake:
        results = retriever.wake_search(
            args.query, k=args.k, sibling=args.sibling, kind=args.kind
        )
    else:
        results = retriever.search(
            args.query, k=args.k, sibling=args.sibling, kind=args.kind
        )

    if not results:
        print("No results. (Index empty or no matching files.)")
    else:
        for hit in results:
            score = hit.get("combined_score") or hit.get("similarity", 0)
            print(f"\n[{score:.4f}] {hit['path']}")
            print(f"  sibling={hit['sibling']}  kind={hit['kind']}  "
                  f"updated={str(hit.get('updated_at', ''))[:10]}")
            excerpt = (hit.get("content_excerpt") or "").strip()
            if excerpt:
                print("  " + excerpt[:300].replace("\n", "\n  "))
