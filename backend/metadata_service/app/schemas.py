from datetime import datetime
from pydantic import BaseModel, ConfigDict

class VideoMetadataCreate(BaseModel):
    video_id: str
    duration: int | None = None
    width: int | None = None
    height: int | None = None
    codec: str | None = None
    format: str | None = None
    file_size: int

class VideoMetadataResponse(VideoMetadataCreate):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)