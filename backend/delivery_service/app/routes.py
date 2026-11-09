from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.shared.config import settings

router = APIRouter(tags=["Media Delivery"])


@router.get("/videos/{video_id}/outputs")
def get_video_outputs(video_id: str):
    output_dir = settings.processed_path / video_id

    if not output_dir.exists():
        raise HTTPException(
            status_code=404,
            detail="No processed videos found.",
        )

    outputs = []

    for file_path in sorted(output_dir.glob("*.mp4")):
        outputs.append({
            "resolution": file_path.stem,
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "url": f"/media/videos/{video_id}/{file_path.name}",
        })

    return {
        "video_id": video_id,
        "total_outputs": len(outputs),
        "outputs": outputs,
    }


@router.get("/videos/{video_id}/thumbnails")
def get_video_thumbnail(video_id: str):
    thumbnail_path = (
        settings.thumbnail_path / video_id / "thumbnail.jpg"
    )

    if not thumbnail_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Thumbnail not found.",
        )

    return {
        "video_id": video_id,
        "thumbnail_url": f"/media/thumbnails/{video_id}",
    }


@router.get("/media/videos/{video_id}/{filename}")
def stream_video(video_id: str, filename: str):
    if Path(filename).name != filename or not filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = settings.processed_path / video_id / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Video file not found.")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename,
    )


@router.get("/media/thumbnails/{video_id}")
def serve_thumbnail(video_id: str):
    file_path = settings.thumbnail_path / video_id / "thumbnail.jpg"

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Thumbnail not found.")

    return FileResponse(
        file_path,
        media_type="image/jpeg",
    )