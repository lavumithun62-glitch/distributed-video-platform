import shutil
import subprocess
from pathlib import Path

from backend.shared.config import settings


def generate_thumbnail(
    video_path: str,
    video_id: str,
    timestamp: int = 5,
) -> dict:

    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg is not installed or not available in PATH."
        )

    output_dir = settings.thumbnail_path / video_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "thumbnail.jpg"

    command = [
        ffmpeg,
        "-y",
        "-ss", str(timestamp),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        str(output_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Thumbnail generation failed: {result.stderr[-2000:]}"
        )

    return {
        "video_id": video_id,
        "thumbnail_path": str(output_path),
        "timestamp_seconds": timestamp,
    }