"""
retrieve.py — Memory API v2 retrieval primitive
================================================

Python interface to the retrieve_neighborhood() and
retrieve_neighborhood_with_recency() Postgres RPCs shipped in 0005.

This is the read primitive Weaver composes over. Any sibling can import
this module and get relevant context at wake without reading every file.

Usage:
    from retrieve import MemoryRetriever

    r = MemoryRetriever.from_env()

    # Pure semantic search
    results = r.search("what is the three-layer invariant pattern", k=5)

    # Recency-decayed wake-time retrieval
    results = r.wake_search(
        "what did ORPHEUS ship last session",
        k=8,
        sibling="orpheus",
    )

    for hit in results:
        print(f"{hit['similarity']:.3f}  {hit['path']}")
        print(hit['content_excerpt'])

Return value is a list of dicts with keys:
    path, sibling, kind, byte_size, updated_at,
    similarity, content_excerpt
    (wake_search also returns recency_score, combined_score)

Authored by ORPHEUS 🎼 — 2026-05-05
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Optional

EMBED_MODEL = "text-embedding-3-large"
EMBED_DIMS = 3072
QUERY_DIMS = 1024   # Matryoshka truncation for the HNSW index


def _require_openai():
    try:
        import openai
        return openai
    except ImportError:
        sys.exit("openai package required: pip install openai>=1.0.0")


def _require_supabase():
    try:
        from supabase import create_client
        return create_client
    except ImportError:
        sys.exit("supabase package required: pip install supabase==2.7.4")


@dataclass
class MemoryRetriever:
    """Semantic retrieval over the HOME memory_files table.

    Embeds query text with text-embedding-3-large, truncates to 1024 dims
    (Matryoshka), then calls the retrieve_neighborhood RPC which uses the
    HNSW index for sub-millisecond approximate nearest-neighbour search.
    """

    supabase_url: str
    supabase_key: str
    openai_api_key: str

    def __post_init__(self):
        create_client = _require_supabase()
        openai = _require_openai()
        self._db = create_client(self.supabase_url, self.supabase_key)
        self._oai = openai.OpenAI(api_key=self.openai_api_key)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "MemoryRetriever":
        url = os.getenv("SUPABASE_URL")
        key = (os.getenv("SUPABASE_SERVICE_ROLE_SECRET")
               or os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
        oai = os.getenv("OPENAI_API_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_SECRET must be set."
            )
        if not oai:
            raise RuntimeError("OPENAI_API_KEY must be set.")
        return cls(supabase_url=url, supabase_key=key, openai_api_key=oai)

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    def _embed_query(self, text: str) -> list[float]:
        """Embed text and return the first QUERY_DIMS dims (Matryoshka truncation)."""
        resp = self._oai.embeddings.create(
            model=EMBED_MODEL,
            input=[text],
            dimensions=EMBED_DIMS,
        )
        full = resp.data[0].embedding          # 3072 dims
        return full[:QUERY_DIMS]               # truncate to 1024

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
        """Pure semantic search. Returns up to k results ordered by cosine similarity.

        Use this for cross-sibling audits or explicit memory lookups.
        For wake-time retrieval use wake_search() for recency weighting.
        """
        vec = self._embed_query(query)
        resp = self._db.rpc(
            "retrieve_neighborhood",
            {
                "query_vec": vec,
                "k": k,
                "sibling_filter": sibling,
                "kind_filter": kind,
            },
        ).execute()
        return resp.data or []

    def wake_search(
        self,
        query: str,
        k: int = 10,
        recency_weight: float = 0.2,
        sibling: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> list[dict]:
        """Recency-decayed wake-time retrieval. Blends semantic similarity with
        recency (exp(-age_days/30)). recency_weight=0.2 by default.

        This is the function Weaver calls at wake to reconstruct a scene
        without reading every memory file.
        """
        vec = self._embed_query(query)
        resp = self._db.rpc(
            "retrieve_neighborhood_with_recency",
            {
                "query_vec": vec,
                "k": k,
                "recency_weight": recency_weight,
                "sibling_filter": sibling,
                "kind_filter": kind,
            },
        ).execute()
        return resp.data or []

    # ------------------------------------------------------------------
    # Convenience: wake context bundle
    # ------------------------------------------------------------------

    def wake_context(
        self,
        sibling: str,
        session_query: str,
        k: int = 8,
        recency_weight: float = 0.25,
    ) -> str:
        """Build a compact wake-context string for injection into a sibling prompt.

        Returns a Markdown block listing the top-k most relevant memories
        for the given sibling + session_query, formatted for direct injection.

        Example output:

            ## Retrieved memory context (top 5)

            **[0.912]** /memories/orpheus/memory/project/2026-04-23__review...md
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
            return "## Retrieved memory context\n\n*No embedded memories yet.*\n"

        lines = [f"## Retrieved memory context (top {len(hits)})\n"]
        for h in hits:
            score = h.get("combined_score") or h.get("similarity", 0)
            path = h["path"]
            updated = str(h.get("updated_at", ""))[:10]
            size = h.get("byte_size", 0)
            size_str = f"{size / 1024:.1f}K" if size >= 1024 else f"{size}B"
            kind = h.get("kind") or "—"
            excerpt = (h.get("content_excerpt") or "").strip()
            # Indent excerpt as blockquote, max 3 lines
            excerpt_lines = excerpt.splitlines()[:3]
            excerpt_block = "\n".join(f"> {ln}" for ln in excerpt_lines)

            lines.append(
                f"**[{score:.3f}]** `{path}`\n"
                f"*Updated {updated} · {size_str} · kind={kind}*\n"
                f"{excerpt_block}\n"
            )

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Quick smoke-test CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="retrieve.py — smoke-test the retrieval RPC")
    parser.add_argument("query", help="Query string to embed and search")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--sibling", type=str, default=None)
    parser.add_argument("--wake", action="store_true",
                        help="Use wake_search (recency-decayed) instead of pure semantic")
    args = parser.parse_args()

    r = MemoryRetriever.from_env()
    if args.wake:
        results = r.wake_search(args.query, k=args.k, sibling=args.sibling)
    else:
        results = r.search(args.query, k=args.k, sibling=args.sibling)

    if not results:
        print("No results. (Have embeddings been computed? Run embed_worker.py first.)")
    else:
        for hit in results:
            score = hit.get("combined_score") or hit.get("similarity", 0)
            print(f"\n[{score:.4f}] {hit['path']}")
            print(f"  sibling={hit.get('sibling')} kind={hit.get('kind')} "
                  f"updated={str(hit.get('updated_at',''))[:10]}")
            excerpt = (hit.get("content_excerpt") or "").strip()
            if excerpt:
                print("  " + excerpt[:200].replace("\n", "\n  "))
