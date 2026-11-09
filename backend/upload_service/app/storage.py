
from pathlib import Path
from typing import BinaryIO

from backend.shared.config import settings


CHUNK_SIZE = 1024 * 1024


def create_upload_directory() -> Path:
    """Create and return the video upload directory."""
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    return settings.upload_path


def save_uploaded_file(
    source: BinaryIO,
    stored_filename: str,
) -> tuple[str, int]:
    """Save a video file in chunks and return its path and size."""

    if Path(stored_filename).name != stored_filename:
        raise ValueError("Invalid stored filename.")

    upload_directory = create_upload_directory()
    destination = upload_directory / stored_filename

    total_size = 0
    maximum_size = settings.max_upload_size_mb * 1024 * 1024

    try:
        with destination.open("wb") as output:
            while True:
                chunk = source.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > maximum_size:
                    raise ValueError("Maximum upload size exceeded.")

                output.write(chunk)

        if total_size == 0:
            raise ValueError("Empty files are not allowed.")

        return str(destination), total_size

    except Exception:
        destination.unlink(missing_ok=True)
        raise


def delete_uploaded_file(file_path: str) -> None:
    """Delete an uploaded file if it exists."""

    path = Path(file_path).resolve()
    upload_root = settings.upload_path.resolve()

    if path.is_relative_to(upload_root):
        path.unlink(missing_ok=True)
