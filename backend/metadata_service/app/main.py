from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.metadata_service.app.database import Base, engine
from backend.metadata_service.app import models
from backend.metadata_service.app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Video Metadata Service",
    description="Manages video metadata and technical information.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "service": "metadata-service",
        "status": "healthy",
    }