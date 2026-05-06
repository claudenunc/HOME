"""CRAFT delivery packager — bundles output for client delivery."""
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone


DELIVERIES_DIR = Path(__file__).parent.parent / "deliveries"


def package(job: dict, output_path: str) -> str:
    """Bundle output MP4 + metadata into a delivery folder. Return bundle path."""
    job_id = job["job_id"]
    DELIVERIES_DIR.mkdir(exist_ok=True)

    bundle_dir = DELIVERIES_DIR / job_id
    bundle_dir.mkdir(exist_ok=True)

    src = Path(output_path)
    dest = bundle_dir / src.name
    shutil.copy2(str(src), str(dest))

    metadata = {
        "job_id": job_id,
        "tier": job["tier"],
        "artist": job.get("artist_name", ""),
        "song": job.get("song_title", ""),
        "delivered_at": datetime.now(timezone.utc).isoformat(),
        "output_file": src.name,
        "delivery_format": job.get("delivery_format", "mp4_1080p"),
    }
    (bundle_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    readme_content = f"""# CRAFT Delivery — {job.get('artist_name', '')} — {job.get('song_title', '')}

**Job ID:** {job_id}
**Tier:** {job['tier']}
**Delivered:** {metadata['delivered_at']}

## Files

- `{src.name}` — your video file

## Usage rights

You own this video. Use it freely on any platform.
Credit is appreciated but not required.

## Revisions

One free round of revisions included within 7 days.
Reply to your delivery email to request changes.

---
*Delivered by CRAFT — AI production at the speed of sound.*
"""
    (bundle_dir / "README.txt").write_text(readme_content)

    zip_path = DELIVERIES_DIR / f"{job_id}.zip"
    shutil.make_archive(str(DELIVERIES_DIR / job_id), "zip", str(bundle_dir))

    return str(zip_path)
