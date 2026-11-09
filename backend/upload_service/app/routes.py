
import json
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.shared.rabbitmq import publish_message
from backend.upload_service.app.database import get_db
from backend.upload_service.app.models import Video
from backend.upload_service.app.schemas import VideoUploadResponse
from backend.upload_service.app.storage import (
    delete_uploaded_file,
    save_uploaded_file,
)
from backend.upload_service.app.validators import (
    validate_file_size,
    validate_upload,
)

router = APIRouter(prefix="/videos", tags=["Videos"])


def extract_video_metadata(file_path: str) -> dict:
    """
    Extract video metadata when FFprobe is available.
    Return empty metadata when FFprobe is unavailable.
    """

    ffprobe_path = shutil.which("ffprobe")

    if not ffprobe_path:
        return {}

    try:
        result = subprocess.run(
            [
                ffprobe_path,
                "-v", "error",
                "-show_entries",
                "format=duration:stream=width,height,codec_name",
                "-of", "json",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )

        metadata = json.loads(result.stdout)

        streams = metadata.get("streams", [])
        video_stream = next(
            (
                stream for stream in streams
                if "width" in stream and "height" in stream
            ),
            {},
        )

        duration = metadata.get("format", {}).get("duration")

        return {
            "duration": int(float(duration)) if duration else None,
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
        }

    except (
        subprocess.SubprocessError,
        ValueError,
        json.JSONDecodeError,
        OSError,
    ):
        return {}


@router.post("/upload", response_model=VideoUploadResponse, status_code=201)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate filename and extension.
    extension = await validate_upload(file)

    video_id = str(uuid.uuid4())
    stored_filename = f"{video_id}{extension}"

    file_path = None

    try:
        # Save the uploaded file.
        file_path, file_size = save_uploaded_file(
            file.file,
            stored_filename,
        )

        # Validate uploaded file size.
        validate_file_size(file_size)

        # Extract metadata if FFprobe is installed.
        metadata = extract_video_metadata(file_path)

        # Create video database record.
        video = Video(
            id=video_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            storage_path=file_path,
            content_type=file.content_type,
            file_size=file_size,
            duration=metadata.get("duration"),
            width=metadata.get("width"),
            height=metadata.get("height"),
            status="uploaded",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(video)
        db.commit()
        db.refresh(video)

    except ValueError as exc:
        db.rollback()
        if file_path:
            delete_uploaded_file(file_path)

        status_code = (
            413 if "size" in str(exc).lower()
            else 400
        )
        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )

    except Exception as exc:
        db.rollback()
        if file_path:
            delete_uploaded_file(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Video upload failed: {str(exc)}",
        )

    finally:
        await file.close()

    # Publish an upload event to RabbitMQ.
    # Upload remains successful if RabbitMQ is temporarily unavailable.
    queue_published = False

    try:
        await publish_message(
            "video.uploaded",
            {
                "video_id": video.id,
                "filename": video.original_filename,
                "storage_path": video.storage_path,
                "file_size": video.file_size,
                "status": video.status,
            },
        )
        queue_published = True

    except Exception:
        queue_published = False

    response = VideoUploadResponse.model_validate(video)

    # Return upload details.
    return response


@router.get("", response_model=list[VideoUploadResponse])
async def list_videos(
    db: Session = Depends(get_db),
):
    videos = (
        db.query(Video)
        .order_by(Video.created_at.desc())
        .all()
    )

    return videos


@router.get("/{video_id}", response_model=VideoUploadResponse)
async def get_video(
    video_id: str,
    db: Session = Depends(get_db),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found.",
        )

    return video
