"""CRAFT Tier 1 — Lyric video generator.

Deps: Pillow, ffmpeg (CLI), no paid API keys required.
Output: MP4 with animated lyrics overlaid on a visual background.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

from .audio_sync import get_lyric_timestamps, get_duration


OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _make_frame(
    text: str,
    width: int,
    height: int,
    bg_color: tuple,
    text_color: tuple,
    font_size: int,
    frame_path: Path,
) -> None:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - w) // 2
    y = (height - h) // 2
    draw.text((x, y), text, fill=text_color, font=font)
    img.save(str(frame_path))


def generate(job: dict) -> str:
    """Generate lyric video. Return path to output MP4."""
    job_id = job["job_id"]
    audio_url = job["audio_url"]
    lyrics_raw = job.get("lyrics", "")
    palette = job.get("color_palette", "#0a0a0a, #ffffff")
    delivery_format = job.get("delivery_format", "mp4_1080p")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    audio_path = job_dir / "audio.mp3"
    _download_file(audio_url, audio_path)

    colors = [c.strip() for c in palette.replace(",", " ").split() if c.strip().startswith("#")]
    bg_color = _hex_to_rgb(colors[0]) if colors else (10, 10, 10)
    text_color = _hex_to_rgb(colors[1]) if len(colors) > 1 else (255, 255, 255)

    w, h = (1080, 1080) if "square" in delivery_format else (1920, 1080)
    if "vertical" in delivery_format:
        w, h = 1080, 1920

    timestamps = get_lyric_timestamps(lyrics_raw, str(audio_path))
    duration = get_duration(str(audio_path))

    frames_dir = job_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as concat_f:
        concat_path = concat_f.name

        entries = []
        for i, entry in enumerate(timestamps):
            start = entry["time"]
            end = timestamps[i + 1]["time"] if i + 1 < len(timestamps) else duration
            seg_duration = max(end - start, 0.5)

            frame_path = frames_dir / f"frame_{i:04d}.png"
            _make_frame(
                entry["text"], w, h, bg_color, text_color,
                font_size=max(48, h // 15),
                frame_path=frame_path,
            )
            entries.append((frame_path, seg_duration))

        if not entries:
            blank = frames_dir / "blank.png"
            _make_frame("", w, h, bg_color, text_color, 48, blank)
            entries = [(blank, duration)]

        with open(concat_path, "w") as f:
            for fp, dur in entries:
                f.write(f"file '{fp}'\n")
                f.write(f"duration {dur:.3f}\n")
            f.write(f"file '{entries[-1][0]}'\n")

    video_silent = job_dir / "video_silent.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_path,
        "-vf", f"scale={w}:{h}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(video_silent),
    ], check=True, capture_output=True)

    output_path = job_dir / f"{job_id}_lyric_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_silent),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        str(output_path),
    ], check=True, capture_output=True)

    os.unlink(concat_path)
    return str(output_path)


def _download_file(url: str, dest: Path) -> None:
    """Download a file from URL to dest path."""
    import urllib.request
    urllib.request.urlretrieve(url, str(dest))
