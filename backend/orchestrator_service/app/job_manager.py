from uuid import uuid4

from sqlalchemy.orm import Session

from backend.orchestrator_service.app.models import ProcessingJob


def create_job(db: Session, video_id: str):
    existing_job = (
        db.query(ProcessingJob)
        .filter(
            ProcessingJob.video_id == video_id,
            ProcessingJob.status.in_(["queued", "processing"])
        )
        .first()
    )

    if existing_job:
        return existing_job

    job = ProcessingJob(
        id=str(uuid4()),
        video_id=video_id,
        status="queued",
        retry_count=0,
        max_retries=3,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def update_job_status(
    db: Session,
    job_id: str,
    status: str,
    error_message: str | None = None,
):
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id
    ).first()

    if not job:
        return None

    job.status = status
    job.error_message = error_message

    db.commit()
    db.refresh(job)

    return job


def retry_job(db: Session, job_id: str):
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id
    ).first()

    if not job:
        return None

    if job.retry_count >= job.max_retries:
        job.status = "failed"
        job.error_message = "Maximum retry attempts exceeded."
    else:
        job.retry_count += 1
        job.status = "queued"
        job.error_message = None

    db.commit()
    db.refresh(job)

    return job