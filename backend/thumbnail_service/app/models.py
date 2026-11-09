from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float

from backend.thumbnail_service.app.database import Base


class VideoThumbnail(Base):
    __tablename__ = "video_thumbnails"

    id = Column(String(36), primary_key=True, index=True)
    video_id = Column(String(36), nullable=False, index=True)

    thumbnail_path = Column(String(1000), nullable=False)
    timestamp_seconds = Column(Float, default=0.0)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )