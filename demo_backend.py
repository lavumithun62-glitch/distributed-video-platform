from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Video Processing Platform Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Video Platform Demo API", "mode": "DEMO"}

@app.get("/health")
def health():
    return {"service": "Demo Backend", "status": "healthy", "mode": "DEMO"}

@app.get("/demo/dashboard")
def dashboard():
    return {
        "mode": "DEMO",
        "total_videos": 3,
        "completed": 1,
        "processing": 1,
        "uploaded": 1,
        "videos": [
            {
                "id": "VID-001",
                "filename": "sample_video.mp4",
                "status": "completed",
                "size": "25 MB",
                "resolutions": ["1080p", "720p", "360p"],
                "thumbnail": "Generated"
            },
            {
                "id": "VID-002",
                "filename": "training_demo.mp4",
                "status": "processing",
                "size": "48 MB",
                "resolutions": [],
                "thumbnail": "Pending"
            },
            {
                "id": "VID-003",
                "filename": "presentation.mp4",
                "status": "uploaded",
                "size": "16 MB",
                "resolutions": [],
                "thumbnail": "Pending"
            }
        ],
        "services": {
            "API Gateway": "Demo",
            "Upload Service": "Demo",
            "Metadata Service": "Demo",
            "Transcoding Orchestrator": "Demo",
            "Thumbnail Service": "Demo",
            "Delivery Service": "Demo"
        }
    }

@app.get("/demo/videos")
def videos():
    return {"mode": "DEMO", "videos": dashboard()["videos"]}

@app.get("/demo/jobs")
def jobs():
    return {
        "mode": "DEMO",
        "jobs": [
            {"job_id": "JOB-001", "video_id": "VID-001", "status": "completed", "progress": 100},
            {"job_id": "JOB-002", "video_id": "VID-002", "status": "processing", "progress": 65}
        ]
    }
