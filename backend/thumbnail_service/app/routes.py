from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.thumbnail_service.app.database import get_db
from backend.thumbnail_service.app.models import VideoThumbnail
from backend.thumbnail_service.app.generator import generate_thumbnail

router = APIRouter(prefix="/thumbnails", tags=["Thumbnails"])


class ThumbnailRequest(BaseModel):
    video_path: str
    timestamp_seconds: int = 5


@router.post("/{video_id}", status_code=201)
def create_thumbnail(
    video_id: str,
    payload: ThumbnailRequest,
    db: Session = Depends(get_db),
):
    try:
        result = generate_thumbnail(
            payload.video_path,
            video_id,
            payload.timestamp_seconds,
        )

        thumbnail = VideoThumbnail(
            id=str(uuid4()),
            video_id=video_id,
            thumbnail_path=result["thumbnail_path"],
            timestamp_seconds=result["timestamp_seconds"],
        )

        db.add(thumbnail)
        db.commit()
        db.refresh(thumbnail)

        return {
            "message": "Thumbnail generated successfully",
            "thumbnail_id": thumbnail.id,
            "video_id": video_id,
            "thumbnail_path": thumbnail.thumbnail_path,
        }

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Thumbnail generation failed: {exc}",
        ) from exc


@router.get("/{video_id}")
def get_thumbnails(
    video_id: str,
    db: Session = Depends(get_db),
):
    thumbnails = db.query(VideoThumbnail).filter(
        VideoThumbnail.video_id == video_id
    ).all()

    return thumbnails