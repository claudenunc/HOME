"""CRAFT intake validator — checks a submitted job JSON against intake_schema.json."""
import json
import sys
from pathlib import Path


SCHEMA_PATH = Path(__file__).parent / "intake_schema.json"


def validate(job: dict) -> tuple[bool, list[str]]:
    """Return (is_valid, list_of_errors)."""
    schema = json.loads(SCHEMA_PATH.read_text())
    errors = []

    tier = job.get("tier")
    if tier not in schema["tiers"]:
        errors.append(f"Invalid tier '{tier}'. Must be one of: {list(schema['tiers'])}")
        return False, errors

    for field in schema["required_fields"]:
        if not job.get(field):
            errors.append(f"Missing required field: {field}")

    for field in schema["tier_specific"].get(tier, []):
        if not job.get(field):
            errors.append(f"Missing tier-required field for {tier}: {field}")

    if job.get("delivery_format") not in schema["delivery_formats"]:
        errors.append(f"Invalid delivery_format. Must be one of: {schema['delivery_formats']}")

    if not job.get("rights_confirmed"):
        errors.append("rights_confirmed must be true")

    if not job.get("deposit_paid"):
        errors.append("deposit_paid must be true — no work starts without 50% deposit")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validator.py <job.json>")
        sys.exit(1)

    path = Path(sys.argv[1])
    job = json.loads(path.read_text())
    valid, errors = validate(job)

    if valid:
        print(f"✅ Job valid: {path.name}")
        tier_info = json.loads(SCHEMA_PATH.read_text())["tiers"][job["tier"]]
        print(f"   Tier: {job['tier']} — ${tier_info['price_usd']}")
        print(f"   Turnaround: {tier_info.get('turnaround_hours', tier_info.get('turnaround_days', '?'))} {'hrs' if 'turnaround_hours' in tier_info else 'days'}")
    else:
        print(f"❌ Job invalid: {path.name}")
        for e in errors:
            print(f"   — {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
