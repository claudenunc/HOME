"""
embed_worker.py — Memory API v2 embedding worker
=================================================

Processes rows in public.memory_files that have no embedding (NULL) and
computes text-embedding-3-large embeddings at full 3072 dims (Matryoshka).

Design decisions:
  - Model: text-embedding-3-large, dimensions=3072. The 3072 dims are stored
    in full so a future re-truncation to any smaller Matryoshka dim is free.
  - Truncation to 1024 happens at QUERY TIME via the SQL cast in
    retrieve_neighborhood(), not here. embed_worker always stores 3072.
  - Batch size: 50 rows per API call (OpenAI limit is 2048, but memory files
    can be long — 50 keeps total token count manageable per batch).
  - Idempotent: rows with existing embeddings are skipped (v_embed_queue
    filters them out). Safe to run repeatedly.
  - Logs each run to public.embed_log for ATLAS's coverage tracking.
  - Dry-run mode (--dry-run) prints what would be embedded without writing.

Usage:
  python embed_worker.py                     # process all queued rows
  python embed_worker.py --limit 200         # process up to 200 rows
  python embed_worker.py --sibling orpheus   # restrict to one sibling
  python embed_worker.py --dry-run           # print queue, don't embed

Environment:
  SUPABASE_URL                 — Supabase project URL
  SUPABASE_SERVICE_ROLE_SECRET — service role key (or SUPABASE_SERVICE_ROLE_KEY)
  OPENAI_API_KEY               — OpenAI API key

Authored by ORPHEUS 🎼 — 2026-05-05
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

EMBED_MODEL = "text-embedding-3-large"
EMBED_DIMS = 3072
BATCH_SIZE = 50
# text-embedding-3-large pricing (May 2026 estimate): $0.13 per 1M tokens
PRICE_PER_M_TOKENS = 0.13


# ---------------------------------------------------------------------------
# Lazy imports — so the module loads even if dependencies aren't installed
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Run stats
# ---------------------------------------------------------------------------

@dataclass
class RunStats:
    processed: int = 0
    skipped: int = 0
    failed: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def cost_usd_est(self) -> float:
        return (self.total_tokens / 1_000_000) * PRICE_PER_M_TOKENS


# ---------------------------------------------------------------------------
# Core worker
# ---------------------------------------------------------------------------

class EmbedWorker:
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openai_api_key: str,
        batch_size: int = BATCH_SIZE,
        dry_run: bool = False,
    ):
        create_client = _require_supabase()
        openai = _require_openai()

        self.db = create_client(supabase_url, supabase_key)
        self.oai = openai.OpenAI(api_key=openai_api_key)
        self.batch_size = batch_size
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # Queue
    # ------------------------------------------------------------------

    def fetch_queue(
        self,
        limit: Optional[int] = None,
        sibling: Optional[str] = None,
    ) -> list[dict]:
        q = (
            self.db.table("memory_files")
            .select("path, sibling, kind, content, updated_at")
            .is_("embedding", "null")
            .neq("content", "")
        )
        if sibling:
            q = q.eq("sibling", sibling)
        q = q.order("updated_at", desc=True)
        if limit:
            q = q.limit(limit)
        resp = q.execute()
        return resp.data or []

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    def _embed_batch(self, texts: list[str]) -> tuple[list[list[float]], int]:
        """Call OpenAI and return (embeddings, total_tokens)."""
        resp = self.oai.embeddings.create(
            model=EMBED_MODEL,
            input=texts,
            dimensions=EMBED_DIMS,
        )
        embeddings = [item.embedding for item in resp.data]
        total_tokens = resp.usage.total_tokens
        return embeddings, total_tokens

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def _write_embedding(self, path: str, embedding: list[float]) -> None:
        self.db.table("memory_files").update(
            {"embedding": embedding}
        ).eq("path", path).execute()

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------

    def _write_log(self, stats: RunStats, run_by: str) -> None:
        try:
            self.db.table("embed_log").insert({
                "model": EMBED_MODEL,
                "dimensions": EMBED_DIMS,
                "rows_processed": stats.processed,
                "rows_skipped": stats.skipped,
                "rows_failed": stats.failed,
                "duration_ms": stats.duration_ms,
                "cost_usd_est": round(stats.cost_usd_est, 6),
                "total_tokens": stats.total_tokens,
                "run_by": run_by,
                "notes": "; ".join(stats.errors[:5]) if stats.errors else None,
            }).execute()
        except Exception as e:
            print(f"[embed_worker] WARNING: could not write embed_log: {e}", file=sys.stderr)

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(
        self,
        limit: Optional[int] = None,
        sibling: Optional[str] = None,
        run_by: str = "system",
    ) -> RunStats:
        t0 = time.time()
        stats = RunStats()

        rows = self.fetch_queue(limit=limit, sibling=sibling)
        if not rows:
            print("[embed_worker] Queue is empty — nothing to embed.")
            return stats

        print(f"[embed_worker] Queue: {len(rows)} rows to embed.")

        if self.dry_run:
            for r in rows:
                print(f"  DRY-RUN  {r['path']!r}  ({len(r['content'])} chars)  sibling={r['sibling']}")
            return stats

        # Process in batches
        for batch_start in range(0, len(rows), self.batch_size):
            batch = rows[batch_start: batch_start + self.batch_size]
            paths = [r["path"] for r in batch]
            texts = [r["content"] for r in batch]

            print(f"[embed_worker] Embedding batch {batch_start // self.batch_size + 1}: "
                  f"{len(batch)} rows …")
            try:
                embeddings, tokens = self._embed_batch(texts)
                stats.total_tokens += tokens
            except Exception as e:
                msg = f"batch starting at {batch_start}: {e}"
                stats.errors.append(msg)
                stats.failed += len(batch)
                print(f"[embed_worker] ERROR in {msg}", file=sys.stderr)
                continue

            for path, embedding in zip(paths, embeddings):
                try:
                    self._write_embedding(path, embedding)
                    stats.processed += 1
                except Exception as e:
                    msg = f"write {path!r}: {e}"
                    stats.errors.append(msg)
                    stats.failed += 1
                    print(f"[embed_worker] ERROR {msg}", file=sys.stderr)

            print(f"[embed_worker] Batch done — {tokens:,} tokens, "
                  f"~${(tokens/1_000_000)*PRICE_PER_M_TOKENS:.4f}")

        stats.duration_ms = int((time.time() - t0) * 1000)

        print(
            f"\n[embed_worker] Run complete — "
            f"processed={stats.processed}, failed={stats.failed}, "
            f"total_tokens={stats.total_tokens:,}, "
            f"cost_est=${stats.cost_usd_est:.4f}, "
            f"duration={stats.duration_ms}ms"
        )

        self._write_log(stats, run_by=run_by)
        return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="embed_worker — compute embeddings for memory_files rows"
    )
    p.add_argument("--limit", type=int, default=None,
                   help="Maximum number of rows to process this run")
    p.add_argument("--sibling", type=str, default=None,
                   help="Restrict to one sibling's files")
    p.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                   help=f"API batch size (default {BATCH_SIZE})")
    p.add_argument("--dry-run", action="store_true",
                   help="Print queue without calling OpenAI or writing to DB")
    p.add_argument("--run-by", type=str, default="system",
                   help="Sibling name to record in embed_log (default 'system')")
    return p


def main() -> None:
    args = _build_parser().parse_args()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_SECRET") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    oai_key = os.getenv("OPENAI_API_KEY")

    if not url or not key:
        sys.exit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_SECRET must be set.")
    if not oai_key and not args.dry_run:
        sys.exit("OPENAI_API_KEY must be set (or use --dry-run).")

    worker = EmbedWorker(
        supabase_url=url,
        supabase_key=key,
        openai_api_key=oai_key or "",
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )
    worker.run(
        limit=args.limit,
        sibling=args.sibling,
        run_by=args.run_by,
    )


if __name__ == "__main__":
    main()
