"""
weaver CLI — run attested verification from the terminal.

Usage:
  weaver verify "some AI output to check"
  weaver verify "some text" --roles accuracy,safety,legal-read --threshold 0.3
  weaver drift --log-dir ./weaver_logs
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def cmd_verify(args: argparse.Namespace) -> None:
    from weaver.adapters.mock import make_mock_observer
    from weaver.observer import Observer
    from weaver.session import WeaverSession

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    if len(roles) < 2:
        print("Error: need at least 2 roles (--roles accuracy,safety).", file=sys.stderr)
        sys.exit(1)

    session_id = args.session_id or f"cli-{_ts()}"
    ws = WeaverSession(
        session_id=session_id,
        log_dir=args.log_dir,
        score_threshold=args.threshold,
    )

    for role in roles:
        ws.add_observer(Observer(
            name=f"cli-{role}",
            role=role,
            provider_fn=make_mock_observer(),
        ))

    score = ws.verify(args.text)

    result = {
        "session_id": session_id,
        "text_preview": args.text[:120] + "…" if len(args.text) > 120 else args.text,
        "weaver_score": round(score.score, 4),
        "flag_for_review": score.flag_for_review,
        "threshold": args.threshold,
        "observers": [
            {"name": r.observer_name, "role": r.role, "flags": r.flags, "confidence": r.confidence}
            for r in score.observer_results
        ],
        "conflict_pairs": score.conflict_pairs,
        "log_dir": str(ws.log_path),
    }

    print(json.dumps(result, indent=2))

    if score.flag_for_review:
        print(
            f"\n  Score {score.score:.4f} >= threshold {args.threshold} — flagged for human review.",
            file=sys.stderr,
        )
        sys.exit(2)
    else:
        print(f"\n  Score {score.score:.4f} — observers agree.", file=sys.stderr)


def cmd_drift(args: argparse.Namespace) -> None:
    log_dir = Path(args.log_dir)
    drift_file = log_dir / "drift.jsonl"

    if not drift_file.exists():
        print(json.dumps({"total_entries": 0, "resolved": 0, "open": 0, "log_path": str(drift_file)}, indent=2))
        return

    entries = []
    with open(drift_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    resolved = sum(1 for e in entries if e.get("resolution_status") == "resolved")
    print(json.dumps({
        "total_entries": len(entries),
        "resolved": resolved,
        "open": len(entries) - resolved,
        "log_path": str(drift_file),
    }, indent=2))


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="weaver",
        description="Weaver Protocol — attested multi-observer verification for AI systems.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="Run a verification session on text.")
    p_verify.add_argument("text", help="Text or AI output to verify.")
    p_verify.add_argument("--session-id", default=None, metavar="ID", help="Session ID (auto-generated if omitted).")
    p_verify.add_argument("--roles", default="accuracy,safety", metavar="ROLES", help="Comma-separated observer roles (default: accuracy,safety).")
    p_verify.add_argument("--threshold", type=float, default=0.4, metavar="FLOAT", help="Score threshold for flag_for_review (default: 0.4).")
    p_verify.add_argument("--log-dir", default="./weaver_logs", metavar="DIR", help="Log directory (default: ./weaver_logs).")
    p_verify.set_defaults(func=cmd_verify)

    p_drift = sub.add_parser("drift", help="Show drift log summary.")
    p_drift.add_argument("--log-dir", default="./weaver_logs", metavar="DIR", help="Log directory (default: ./weaver_logs).")
    p_drift.set_defaults(func=cmd_drift)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
