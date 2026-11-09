from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.orchestrator_service.app.database import Base, engine
from backend.orchestrator_service.app import models
from backend.orchestrator_service.app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Video Transcoding Orchestrator",
    description="Manages video-processing jobs and retries.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "service": "transcoding-orchestrator",
        "status": "healthy",
    }