from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime

from backend.upload_service.app.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, index=True)

    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)

    storage_path = Column(String(1000), nullable=False)

    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=False)

    duration = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    status = Column(
        String(50),
        default="uploaded",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )