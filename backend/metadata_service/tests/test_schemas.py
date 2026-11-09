import pytest
from pydantic import ValidationError

from backend.metadata_service.app.schemas import VideoMetadataCreate


def test_valid_video_metadata():
    metadata = VideoMetadataCreate(
        video_id="video-123",
        duration=120,
        width=1920,
        height=1080,
        codec="h264",
        format="mp4",
        file_size=5000000,
    )

    assert metadata.video_id == "video-123"
    assert metadata.width == 1920
    assert metadata.height == 1080


def test_metadata_requires_video_id():
    with pytest.raises(ValidationError):
        VideoMetadataCreate(file_size=5000000)


def test_metadata_requires_file_size():
    with pytest.raises(ValidationError):
        VideoMetadataCreate(video_id="video-123")