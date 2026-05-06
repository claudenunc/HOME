"""Audio sync utilities — beat detection and timestamp extraction.

Deps: librosa (optional), ffprobe (standard with ffmpeg)
Falls back to fixed-interval timestamps if librosa unavailable.
"""
import subprocess
import json
from pathlib import Path


def get_duration(audio_path: str) -> float:
    """Return audio duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            audio_path,
        ],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def get_beat_timestamps(audio_path: str, interval_seconds: float = 2.0) -> list[float]:
    """Return beat timestamps in seconds.

    Uses librosa if available; falls back to fixed interval.
    Fixed interval is sufficient for lyric video sync.
    """
    try:
        import librosa
        y, sr = librosa.load(audio_path)
        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        return librosa.frames_to_time(beat_frames, sr=sr).tolist()
    except ImportError:
        duration = get_duration(audio_path)
        return [i * interval_seconds for i in range(int(duration / interval_seconds))]


def get_lyric_timestamps(lyrics_raw: str, audio_path: str) -> list[dict]:
    """Parse lyrics with optional [MM:SS] timestamps.

    If no timestamps present, distribute lines evenly across duration.
    Returns list of {time: float, text: str}.
    """
    import re
    duration = get_duration(audio_path)
    lines = [l.strip() for l in lyrics_raw.strip().splitlines() if l.strip()]

    timestamped = []
    untimestamped = []

    for line in lines:
        match = re.match(r'^\[(\d+):(\d+(?:\.\d+)?)\]\s*(.*)', line)
        if match:
            m, s, text = match.groups()
            timestamped.append({"time": int(m) * 60 + float(s), "text": text})
        else:
            untimestamped.append(line)

    if timestamped:
        return timestamped

    if not uninstalled := untimestamped:
        return []
    step = duration / max(len(uninstalled), 1)
    return [{"time": i * step, "text": t} for i, t in enumerate(uninstalled)]
