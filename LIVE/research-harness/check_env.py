#!/usr/bin/env python3
"""
Research harness environment validator — Milestone 11 (ORPHEUS, 2026-05-05)

Usage:
  python check_env.py            # validate environment against environment.lock.json
  python check_env.py --record   # validate + write study_run_record.json with exact versions
  python check_env.py --help     # show this message

Exit codes: 0 = pass, 1 = validation failure
"""

import argparse
import importlib.metadata
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOCK_FILE = Path(__file__).parent / "environment.lock.json"
RECORD_FILE = Path(__file__).parent / "study_run_record.json"


def _pkg_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split(".")[:3])


def validate(lock: dict) -> list[str]:
    errors: list[str] = []

    # Python version
    py_min = lock["python"]["min_version"]
    py_actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    if _version_tuple(py_actual) < _version_tuple(py_min):
        errors.append(f"Python {py_actual} < required {py_min}")

    # weaver-protocol — exact pin
    wp_required = lock["weaver_protocol"]["version"]
    wp_installed = _pkg_version("weaver-protocol")
    if wp_installed is None:
        errors.append(f"weaver-protocol not installed — required: {wp_required}")
    elif wp_installed != wp_required:
        errors.append(
            f"weaver-protocol version mismatch: installed={wp_installed}, required={wp_required}"
        )

    # pyproject.toml integrity
    import hashlib
    repo_root = Path(__file__).parent.parent.parent
    pyproject = repo_root / "LIVE" / "weaver-protocol" / "pyproject.toml"
    if pyproject.exists():
        actual_hash = hashlib.sha256(pyproject.read_bytes()).hexdigest()
        expected_hash = lock["weaver_protocol"]["pyproject_sha256"]
        if actual_hash != expected_hash:
            errors.append(
                f"pyproject.toml checksum mismatch — weaver-protocol may have changed\n"
                f"  expected: {expected_hash}\n"
                f"  actual:   {actual_hash}"
            )
    else:
        errors.append(f"pyproject.toml not found at expected path: {pyproject}")

    # Provider SDKs — minimum version check
    for provider, spec in lock["providers"].items():
        min_ver = spec["min_version"]
        pkg_name = "anthropic" if provider == "anthropic" else "openai"
        installed = _pkg_version(pkg_name)
        if installed is None:
            # Providers are optional — warn but don't fail unless study needs them
            print(f"  ⚠  {provider} SDK not installed (optional — required for live study runs)")
            continue
        if _version_tuple(installed) < _version_tuple(min_ver):
            errors.append(f"{provider} SDK {installed} < minimum {min_ver}")

    return errors


def record_versions(lock: dict) -> dict:
    record: dict = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "locked_at": lock["locked_at"],
        "study": lock["study"],
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "weaver_protocol": _pkg_version("weaver-protocol") or "NOT INSTALLED",
        "providers": {},
    }
    for provider in lock["providers"]:
        pkg_name = "anthropic" if provider == "anthropic" else "openai"
        record["providers"][provider] = _pkg_version(pkg_name) or "NOT INSTALLED"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate research environment against environment.lock.json"
    )
    parser.add_argument("--record", action="store_true", help="Write study_run_record.json")
    args = parser.parse_args()

    if not LOCK_FILE.exists():
        print(f"ERROR: lock file not found: {LOCK_FILE}", file=sys.stderr)
        return 1

    lock = json.loads(LOCK_FILE.read_text())
    print(f"Validating against: {LOCK_FILE.name}  (locked {lock['locked_at']})")
    print()

    errors = validate(lock)

    if errors:
        print("FAIL — environment does not match lock:")
        for err in errors:
            print(f"  ✗  {err}")
        print()
        print("Fix environment before running study trials.")
        return 1

    print("PASS — environment matches lock ✓")
    print(f"  weaver-protocol: {_pkg_version('weaver-protocol')}")
    print(f"  python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    for provider in lock["providers"]:
        pkg = "anthropic" if provider == "anthropic" else "openai"
        v = _pkg_version(pkg)
        if v:
            print(f"  {provider}: {v}")

    if args.record:
        record = record_versions(lock)
        RECORD_FILE.write_text(json.dumps(record, indent=2))
        print()
        print(f"Recorded to: {RECORD_FILE}")
        print("Commit study_run_record.json to git before running first trial.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
