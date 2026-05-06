"""CRAFT pipeline runner — orchestrates job execution.

Usage:
  python runner.py --job-file <path/to/job.json>   # run single job
  python runner.py --scan                           # scan for pending jobs (cron mode)
"""
import json
import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
LOG_FILE = ROOT / "CRAFT_JOBS.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("craft.runner")


def _load_job(path: Path) -> dict:
    return json.loads(path.read_text())


def _update_job_log(job_id: str, status: str, detail: str = "") -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "job_id": job_id,
        "status": status,
        "detail": detail,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _run_job(job: dict) -> bool:
    """Dispatch to appropriate generator. Return True on success."""
    from intake.validator import validate
    valid, errors = validate(job)
    if not valid:
        log.error("Job %s failed validation: %s", job.get("job_id"), errors)
        _update_job_log(job.get("job_id", "unknown"), "VALIDATION_FAILED", str(errors))
        return False

    tier = job["tier"]
    job_id = job["job_id"]
    log.info("Starting job %s — tier: %s", job_id, tier)
    _update_job_log(job_id, "STARTED", f"tier={tier}")

    try:
        if tier == "lyric_video":
            from generators.lyric_video import generate
        else:
            from generators.full_video import generate

        output_path = generate(job)
        log.info("Job %s — generation complete: %s", job_id, output_path)

        from delivery.packager import package
        bundle_path = package(job, output_path)
        log.info("Job %s — packaged: %s", job_id, bundle_path)

        from delivery.notifier import notify
        notify(job, bundle_path)
        log.info("Job %s — client notified", job_id)

        _update_job_log(job_id, "COMPLETE", f"bundle={bundle_path}")
        return True

    except Exception as exc:
        log.exception("Job %s failed: %s", job_id, exc)
        _update_job_log(job_id, "FAILED", str(exc))
        return False


def _scan_and_run() -> None:
    """Scan intake/submitted/ for pending jobs and run them."""
    submitted_dir = ROOT / "intake" / "submitted"
    if not submitted_dir.exists():
        log.info("No submitted jobs directory — nothing to do")
        return

    job_files = list(submitted_dir.glob("*.json"))
    if not job_files:
        log.info("No pending jobs")
        return

    log.info("Found %d pending job(s)", len(job_files))
    for jf in job_files:
        job = _load_job(jf)
        success = _run_job(job)
        if success:
            done_dir = ROOT / "intake" / "done"
            done_dir.mkdir(exist_ok=True)
            jf.rename(done_dir / jf.name)
        else:
            failed_dir = ROOT / "intake" / "failed"
            failed_dir.mkdir(exist_ok=True)
            jf.rename(failed_dir / jf.name)


def main():
    parser = argparse.ArgumentParser(description="CRAFT pipeline runner")
    parser.add_argument("--job-file", help="Path to a single job JSON file")
    parser.add_argument("--scan", action="store_true", help="Scan for pending jobs (cron mode)")
    args = parser.parse_args()

    if args.job_file:
        job = _load_job(Path(args.job_file))
        success = _run_job(job)
        sys.exit(0 if success else 1)
    elif args.scan:
        _scan_and_run()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
