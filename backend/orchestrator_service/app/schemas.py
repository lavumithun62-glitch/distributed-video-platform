from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProcessingJobCreate(BaseModel):
    video_id: str


class ProcessingJobResponse(BaseModel):
    id: str
    video_id: str
    status: str
    retry_count: int
    max_retries: int
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)