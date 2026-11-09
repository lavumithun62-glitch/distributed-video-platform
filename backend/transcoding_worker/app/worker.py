import asyncio
import json
import logging
from pathlib import Path
from uuid import uuid4

import aio_pika

from backend.shared.config import settings
from backend.shared.rabbitmq import get_rabbitmq_connection
from backend.transcoding_worker.app.database import Base, SessionLocal, engine
from backend.transcoding_worker.app.models import TranscodingOutput
from backend.transcoding_worker.app.transcoder import transcode_video

logger = logging.getLogger(__name__)

QUEUE_NAME = "video.process"


async def process_video_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode("utf-8"))

        video_id = data["video_id"]
        job_id = data["job_id"]

        matching_files = list(settings.upload_path.glob(f"{video_id}.*"))

        if not matching_files:
            raise FileNotFoundError(
                f"Uploaded video not found for ID: {video_id}"
            )

        input_path = str(matching_files[0])

        for resolution in ["360p", "720p", "1080p"]:
            result = await asyncio.to_thread(
                transcode_video,
                input_path,
                video_id,
                resolution,
            )

            db = SessionLocal()

            try:
                output = TranscodingOutput(
                    id=str(uuid4()),
                    video_id=video_id,
                    job_id=job_id,
                    resolution=result["resolution"],
                    output_path=result["output_path"],
                    file_size=result["file_size"],
                    status="completed",
                )

                db.add(output)
                db.commit()

            except Exception:
                db.rollback()
                raise

            finally:
                db.close()

        logger.info("Video transcoding completed: %s", video_id)


async def run_worker():
    Base.metadata.create_all(bind=engine)

    connection = await get_rabbitmq_connection()

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            QUEUE_NAME,
            durable=True,
        )

        logger.info("Worker waiting for video-processing messages...")

        await queue.consume(process_video_message)

        await asyncio.Future()