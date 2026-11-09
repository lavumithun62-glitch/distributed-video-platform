from fastapi import FastAPI

from backend.delivery_service.app.routes import router

app = FastAPI(
    title="Media Delivery Service",
    description="Serves transcoded videos and generated thumbnails.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "service": "media-delivery-service",
        "status": "healthy",
    }