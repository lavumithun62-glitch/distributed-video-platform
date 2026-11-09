from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.shared.config import settings

from backend.upload_service.app.database import (
    Base,
    engine,
)

from backend.upload_service.app import models
from backend.upload_service.app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Video Upload Service",
    description="Upload and validate video files.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "service": "upload-service",
        "status": "healthy",
    }