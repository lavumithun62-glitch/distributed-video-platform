import shutil
import subprocess
from pathlib import Path

from backend.shared.config import settings


def transcode_video(
    input_path: str,
    video_id: str,
    resolution: str,
) -> dict:

    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg is not installed or not available in PATH."
        )

    resolutions = {
        "360p": 640,
        "720p": 1280,
        "1080p": 1920,
    }

    if resolution not in resolutions:
        raise ValueError("Unsupported resolution.")

    output_dir = settings.processed_path / video_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{resolution}.mp4"
    width = resolutions[resolution]

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", f"scale='min({width},iw)':-2",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(output_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=3600,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg transcoding failed: {result.stderr[-2000:]}"
        )

    return {
        "resolution": resolution,
        "output_path": str(output_path),
        "file_size": output_path.stat().st_size,
    }