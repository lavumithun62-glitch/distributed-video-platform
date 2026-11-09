from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.thumbnail_service.app.database import Base, engine
from backend.thumbnail_service.app import models
from backend.thumbnail_service.app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Video Thumbnail Service",
    description="Generates and manages video thumbnails.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "service": "thumbnail-service",
        "status": "healthy",
    }