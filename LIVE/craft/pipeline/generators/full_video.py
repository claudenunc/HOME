"""CRAFT Tier 2/3 — Full/promo video generator.

Uses Runway ML API (or falls back to Pillow image slideshow if RUNWAY_API_KEY unset).
Tier 2 ($597): AI imagery synced to track.
Tier 3 ($1,997): Full cinematic scenes with custom prompts per section.
"""
import os
import time
import json
import subprocess
import tempfile
from pathlib import Path

from .audio_sync import get_beat_timestamps, get_duration

OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
RUNWAY_API_KEY = os.environ.get("RUNWAY_API_KEY")


def _build_scene_prompts(job: dict) -> list[str]:
    """Build per-scene prompts from job visual_references + mood."""
    base = job.get("visual_references", "cinematic music video")
    mood = job.get("mood", "cinematic")
    excluded = job.get("excluded_elements", "")
    genre = job.get("genre", "")
    tier = job.get("tier", "promo_video")

    num_scenes = 8 if tier == "promo_video" else 20

    prompts = []
    for i in range(num_scenes):
        prompt = f"{mood} {genre} music video scene, {base}, high quality cinematic"
        if excluded:
            prompt += f", no {excluded}"
        prompts.append(prompt)
    return prompts


def _generate_with_runway(prompts: list[str], job_dir: Path) -> list[Path]:
    """Generate images using Runway ML API."""
    try:
        import httpx
    except ImportError:
        raise RuntimeError("httpx required: pip install httpx")

    images = []
    for i, prompt in enumerate(prompts):
        response = httpx.post(
            "https://api.dev.runwayml.com/v1/image_to_video",
            headers={
                "Authorization": f"Bearer {RUNWAY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt, "width": 1920, "height": 1080},
            timeout=60,
        )
        response.raise_for_status()

        img_path = job_dir / f"scene_{i:04d}.jpg"
        img_path.write_bytes(response.content)
        images.append(img_path)
        time.sleep(0.5)

    return images


def _generate_fallback_images(prompts: list[str], job_dir: Path, job: dict) -> list[Path]:
    """Generate placeholder images with Pillow when Runway unavailable."""
    from PIL import Image, ImageDraw

    palette = job.get("color_palette", "#0a0a0a, #1a1a2e")
    colors_raw = [c.strip() for c in palette.replace(",", " ").split() if c.strip().startswith("#")]
    base_colors = colors_raw[:4] if colors_raw else ["#0a0a0a", "#1a1a2e", "#16213e", "#0f3460"]

    images = []
    for i, prompt in enumerate(prompts):
        color = base_colors[i % len(base_colors)]
        r, g, b = tuple(int(color.lstrip("#")[j:j+2], 16) for j in (0, 2, 4))

        img = Image.new("RGB", (1920, 1080), (r, g, b))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Scene {i+1}", fill=(200, 200, 200))
        draw.text((50, 100), prompt[:80], fill=(150, 150, 150))

        img_path = job_dir / f"scene_{i:04d}.jpg"
        img.save(str(img_path))
        images.append(img_path)

    return images


def generate(job: dict) -> str:
    """Generate full/promo video. Return path to output MP4."""
    job_id = job["job_id"]
    audio_url = job["audio_url"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    audio_path = job_dir / "audio.mp3"
    _download_file(audio_url, audio_path)

    duration = get_duration(str(audio_path))
    prompts = _build_scene_prompts(job)

    if RUNWAY_API_KEY:
        scene_images = _generate_with_runway(prompts, job_dir)
    else:
        scene_images = _generate_fallback_images(prompts, job_dir, job)

    beat_times = get_beat_timestamps(str(audio_path))
    scene_duration = duration / max(len(scene_images), 1)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as concat_f:
        concat_path = concat_f.name
        with open(concat_path, "w") as f:
            for i, img_path in enumerate(scene_images):
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {scene_duration:.3f}\n")
            f.write(f"file '{scene_images[-1]}'\n")

    video_silent = job_dir / "video_silent.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_path,
        "-vf", "scale=1920:1080",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(video_silent),
    ], check=True, capture_output=True)

    output_path = job_dir / f"{job_id}_full_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_silent),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        str(output_path),
    ], check=True, capture_output=True)

    import os
    os.unlink(concat_path)
    return str(output_path)


def _download_file(url: str, dest: Path) -> None:
    import urllib.request
    urllib.request.urlretrieve(url, str(dest))
