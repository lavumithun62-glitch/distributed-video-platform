from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from backend.metadata_service.app.database import Base

class VideoMetadata(Base):
    __tablename__ = "video_metadata"

    id = Column(String(36), primary_key=True, index=True)
    video_id = Column(String(36), nullable=False, unique=True, index=True)
    duration = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    codec = Column(String(100), nullable=True)
    format = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
