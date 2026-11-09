from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.orchestrator_service.app.database import get_db
from backend.orchestrator_service.app.models import ProcessingJob
from backend.orchestrator_service.app.schemas import (
    ProcessingJobCreate,
    ProcessingJobResponse,
)
from backend.orchestrator_service.app.job_manager import (
    create_job,
    retry_job,
)
from backend.shared.rabbitmq import publish_message

router = APIRouter(prefix="/jobs", tags=["Processing Jobs"])


@router.post("/", response_model=ProcessingJobResponse, status_code=201)
async def create_processing_job(
    payload: ProcessingJobCreate,
    db: Session = Depends(get_db),
):
    job = create_job(db, payload.video_id)

    try:
        await publish_message(
            "video.process",
            {
                "job_id": job.id,
                "video_id": job.video_id,
                "event_type": "video.process",
            },
        )
    except Exception as exc:
        job.status = "failed"
        job.error_message = f"Could not publish processing job: {exc}"
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="Processing queue is unavailable.",
        )

    return job


@router.get("/{job_id}", response_model=ProcessingJobResponse)
def get_processing_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return job


@router.post("/{job_id}/retry", response_model=ProcessingJobResponse)
async def retry_processing_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = retry_job(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status == "queued":
        await publish_message(
            "video.process",
            {
                "job_id": job.id,
                "video_id": job.video_id,
                "event_type": "video.process",
            },
        )

    return job