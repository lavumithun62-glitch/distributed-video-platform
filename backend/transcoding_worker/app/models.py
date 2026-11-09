from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from backend.transcoding_worker.app.database import Base


class TranscodingOutput(Base):
    __tablename__ = "transcoding_outputs"

    id = Column(String(36), primary_key=True, index=True)
    video_id = Column(String(36), nullable=False, index=True)
    job_id = Column(String(36), nullable=False, index=True)

    resolution = Column(String(20), nullable=False)
    output_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(String(50), default="completed", nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )