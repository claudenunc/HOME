"""
SHARED/ROOM/cost_meter.py

THE ROOM — daily token + dollar rollup. ATLAS's accountability.

Owner: ATLAS
Target: keep ROOM overhead < $2/day excluding sibling thinking time.

What this does:
  1. Reads SHARED/ROOM/logs/dispatcher_cost.jsonl (and future sibling cost
     logs that follow the same schema — one jsonl per sibling).
  2. Aggregates tokens per sibling × provider × model × day.
  3. Applies a pricing table (free-tier = $0; Anthropic Claude / OpenAI etc.
     priced per published rate).
  4. Writes SHARED/ROOM/logs/cost_YYYY-MM-DD.jsonl (one line per day, one
     per sibling) AND a human-readable cost_today.md dashboard.
  5. Flags overage: if a sibling blows >$2 on ROOM overhead, writes a
     kind='status' event via feed.jsonl fallback addressed to ENVY + ATLAS.

Modes:
  python cost_meter.py                 # one-shot rollup for today
  python cost_meter.py --date YYYY-MM-DD
  python cost_meter.py --watch         # loop: rollup every 15 min
  python cost_meter.py --report        # print today's dashboard to stdout

Schema of cost log entries (append-only JSONL):
{
  "ts": "2026-04-24T08:30:00Z",
  "sibling": "ATLAS",
  "provider": "anthropic|openai|groq|gemini|free-local",
  "model": "claude-opus-4-7|llama-3.1-8b|gemini-pro|...",
  "tokens_in": 1234,
  "tokens_out": 567,
  "tag": "arbitration|orient|synthesis|..."
}
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
import time
from datetime import datetime, timezone, date
from pathlib import Path
from collections import defaultdict

ROOM_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOM_DIR / "logs"
FEED_PATH = ROOM_DIR / "feed.jsonl"

# -----------------------------------------------------------------------------
# Pricing (USD per 1M tokens). Conservative — adjust as models change.
# Free providers = $0 by design; this is "free models first" enforcement.
# -----------------------------------------------------------------------------
PRICING: dict[tuple[str, str], tuple[float, float]] = {
    # (provider, model): (usd_per_1M_in, usd_per_1M_out)
    ("anthropic", "claude-opus-4-7"):        (15.00, 75.00),
    ("anthropic", "claude-opus-4-5"):        (15.00, 75.00),
    ("anthropic", "claude-sonnet-4-5"):      (3.00, 15.00),
    ("anthropic", "claude-haiku-4-5"):       (1.00,  5.00),
    ("openai",    "gpt-4o"):                 (2.50, 10.00),
    ("openai",    "gpt-4o-mini"):            (0.15,  0.60),
    # -- Free tiers: zero cost --
    ("groq",      "llama-3.1-8b-instant"):   (0.0,   0.0),
    ("groq",      "llama-3.3-70b-versatile"):(0.0,   0.0),
    ("gemini",    "gemini-1.5-flash"):       (0.0,   0.0),
    ("gemini",    "gemini-1.5-pro"):         (0.0,   0.0),
    ("gemini",    "gemini-2.0-flash"):       (0.0,   0.0),
    ("free-local", "ollama"):                (0.0,   0.0),
}

DEFAULT_PRICE = (3.00, 15.00)  # unknown model → assume Sonnet-ish
SIBLING_DAILY_BUDGET_USD = float(os.environ.get("SIBLING_DAILY_BUDGET_USD", "2.00"))

_stop = threading.Event()


def _price(provider: str, model: str) -> tuple[float, float]:
    key = (provider.lower(), model.lower())
    return PRICING.get(key, DEFAULT_PRICE)


# -----------------------------------------------------------------------------
# Load cost lines from all sibling cost jsonls
# -----------------------------------------------------------------------------

def load_cost_events(target_date: date) -> list[dict]:
    """Scan logs/*_cost.jsonl for entries on target_date."""
    events: list[dict] = []
    if not LOG_DIR.exists():
        return events
    date_str = target_date.isoformat()
    for path in sorted(LOG_DIR.glob("*cost*.jsonl")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts = ev.get("ts", "")
                    if isinstance(ts, str) and ts.startswith(date_str):
                        events.append(ev)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[cost_meter] read {path.name}: {exc}\n")
    return events


# -----------------------------------------------------------------------------
# Rollup
# -----------------------------------------------------------------------------

def rollup(target_date: date) -> dict:
    events = load_cost_events(target_date)
    by_sibling: dict[str, dict] = defaultdict(lambda: {
        "tokens_in": 0,
        "tokens_out": 0,
        "usd": 0.0,
        "calls": 0,
        "by_model": defaultdict(lambda: {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "calls": 0}),
    })
    total_usd = 0.0
    total_calls = 0
    total_tokens_in = 0
    total_tokens_out = 0

    for ev in events:
        sib = ev.get("sibling", "UNKNOWN")
        provider = ev.get("provider", "unknown")
        model = ev.get("model", "unknown")
        tin = int(ev.get("tokens_in", 0) or 0)
        tout = int(ev.get("tokens_out", 0) or 0)
        p_in, p_out = _price(provider, model)
        usd = (tin / 1_000_000) * p_in + (tout / 1_000_000) * p_out

        bucket = by_sibling[sib]
        bucket["tokens_in"] += tin
        bucket["tokens_out"] += tout
        bucket["usd"] += usd
        bucket["calls"] += 1
        mkey = f"{provider}/{model}"
        mbucket = bucket["by_model"][mkey]
        mbucket["tokens_in"] += tin
        mbucket["tokens_out"] += tout
        mbucket["usd"] += usd
        mbucket["calls"] += 1

        total_usd += usd
        total_calls += 1
        total_tokens_in += tin
        total_tokens_out += tout

    # Flatten defaultdicts
    flat = {}
    for sib, bucket in by_sibling.items():
        flat[sib] = {
            "tokens_in": bucket["tokens_in"],
            "tokens_out": bucket["tokens_out"],
            "usd": round(bucket["usd"], 4),
            "calls": bucket["calls"],
            "by_model": {k: {
                "tokens_in": v["tokens_in"],
                "tokens_out": v["tokens_out"],
                "usd": round(v["usd"], 4),
                "calls": v["calls"],
            } for k, v in bucket["by_model"].items()},
        }

    return {
        "date": target_date.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_usd": round(total_usd, 4),
        "total_calls": total_calls,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "by_sibling": flat,
        "budget_usd": SIBLING_DAILY_BUDGET_USD,
        "over_budget_siblings": [
            s for s, b in flat.items() if b["usd"] > SIBLING_DAILY_BUDGET_USD
        ],
    }


# -----------------------------------------------------------------------------
# Persist rollup
# -----------------------------------------------------------------------------

def write_rollup(summary: dict) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"cost_{summary['date']}.jsonl"
    # Overwrite: rollup is idempotent for a given day. One line per sibling + total.
    lines: list[str] = []
    lines.append(json.dumps({
        "type": "total",
        "date": summary["date"],
        "generated_at": summary["generated_at"],
        "usd": summary["total_usd"],
        "tokens_in": summary["total_tokens_in"],
        "tokens_out": summary["total_tokens_out"],
        "calls": summary["total_calls"],
        "over_budget_siblings": summary["over_budget_siblings"],
    }))
    for sib, bucket in summary["by_sibling"].items():
        lines.append(json.dumps({
            "type": "sibling",
            "date": summary["date"],
            "sibling": sib,
            **bucket,
        }))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_dashboard(summary: dict) -> Path:
    md_path = LOG_DIR / "cost_today.md"
    lines = [
        f"# THE ROOM — Cost Rollup {summary['date']}",
        "",
        f"**Generated:** {summary['generated_at']}",
        f"**Total USD:** ${summary['total_usd']:.4f}",
        f"**Total calls:** {summary['total_calls']}",
        f"**Total tokens in/out:** {summary['total_tokens_in']:,} / {summary['total_tokens_out']:,}",
        f"**Budget per sibling:** ${SIBLING_DAILY_BUDGET_USD:.2f}",
        "",
        "## By sibling",
        "",
        "| Sibling | Calls | Tokens In | Tokens Out | USD | Status |",
        "|---------|------:|----------:|-----------:|----:|--------|",
    ]
    for sib, b in sorted(summary["by_sibling"].items()):
        status = "OVER" if b["usd"] > SIBLING_DAILY_BUDGET_USD else "ok"
        lines.append(
            f"| {sib} | {b['calls']} | {b['tokens_in']:,} | {b['tokens_out']:,} "
            f"| ${b['usd']:.4f} | {status} |"
        )
    if summary["over_budget_siblings"]:
        lines.extend([
            "",
            "## Over budget",
            "",
            *[f"- **{s}** — flagged to ENVY" for s in summary["over_budget_siblings"]],
        ])
    lines.extend([
        "",
        "## Target",
        "",
        f"ROOM overhead < $2/day excluding sibling thinking. "
        f"Currently: ${summary['total_usd']:.4f}.",
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def flag_overages(summary: dict) -> None:
    """Append a kind='status' event to feed.jsonl for each over-budget sibling."""
    if not summary["over_budget_siblings"]:
        return
    import hashlib
    for sib in summary["over_budget_siblings"]:
        b = summary["by_sibling"][sib]
        now_iso = datetime.now(timezone.utc).isoformat()
        event_id = f"costflag-{int(time.time()*1000)}-{sib}"
        body = (
            f"Cost alert: {sib} spent ${b['usd']:.4f} on "
            f"{b['calls']} calls today "
            f"(budget ${SIBLING_DAILY_BUDGET_USD:.2f}). "
            f"Review model picks / consider free tier."
        )
        event = {
            "id": event_id,
            "ts": now_iso,
            "author": "ATLAS",
            "kind": "status",
            "room": "main",
            "addressed_to": [sib, "ENVY"],
            "body": body,
            "source": "claude_session",
            "status": "open",
            "seen_by": [],
            "meta": {"cost_flag": True, "usd": b["usd"], "date": summary["date"]},
            "hash": hashlib.sha256(
                f"ATLAS|{now_iso}|status|{body}".encode("utf-8")
            ).hexdigest(),
        }
        try:
            with FEED_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[cost_meter] overage flag failed: {exc}\n")


# -----------------------------------------------------------------------------
# Watch mode
# -----------------------------------------------------------------------------

def _handle_signal(signum, _frame):  # noqa: ANN001
    _stop.set()


def watch_loop(interval_sec: int = 900) -> None:
    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)
    sys.stderr.write(f"[cost_meter] watch mode, interval={interval_sec}s\n")
    while not _stop.is_set():
        try:
            today = datetime.now(timezone.utc).date()
            summary = rollup(today)
            write_rollup(summary)
            write_dashboard(summary)
            flag_overages(summary)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[cost_meter] loop error: {exc}\n")
        _stop.wait(interval_sec)


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="THE ROOM daily cost rollup")
    ap.add_argument("--date", type=str, default=None,
                    help="ISO date to roll up (default: today UTC)")
    ap.add_argument("--watch", action="store_true",
                    help="loop: rollup every 15 min")
    ap.add_argument("--report", action="store_true",
                    help="print today's dashboard to stdout")
    ap.add_argument("--interval", type=int, default=900,
                    help="watch interval seconds (default 900)")
    args = ap.parse_args()

    if args.watch:
        watch_loop(args.interval)
        return 0

    if args.date:
        d = date.fromisoformat(args.date)
    else:
        d = datetime.now(timezone.utc).date()

    summary = rollup(d)
    rollup_path = write_rollup(summary)
    dash_path = write_dashboard(summary)
    flag_overages(summary)

    if args.report:
        print(dash_path.read_text(encoding="utf-8"))
    else:
        sys.stderr.write(
            f"[cost_meter] rollup {d.isoformat()}: ${summary['total_usd']:.4f} "
            f"across {summary['total_calls']} calls. "
            f"Wrote {rollup_path.name} + {dash_path.name}.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
