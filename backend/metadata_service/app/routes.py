from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.metadata_service.app.database import get_db
from backend.metadata_service.app.models import VideoMetadata
from backend.metadata_service.app.schemas import (
    VideoMetadataCreate,
    VideoMetadataResponse,
)

router = APIRouter(prefix="/metadata", tags=["Video Metadata"])


@router.post("/", response_model=VideoMetadataResponse, status_code=201)
def create_metadata(
    payload: VideoMetadataCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(VideoMetadata).filter(
        VideoMetadata.video_id == payload.video_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Metadata already exists for this video.",
        )

    metadata = VideoMetadata(
        id=str(uuid4()),
        **payload.model_dump(),
    )

    db.add(metadata)
    db.commit()
    db.refresh(metadata)

    return metadata


@router.get("/{video_id}", response_model=VideoMetadataResponse)
def get_metadata(video_id: str, db: Session = Depends(get_db)):
    metadata = db.query(VideoMetadata).filter(
        VideoMetadata.video_id == video_id
    ).first()

    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata not found.")

    return metadata