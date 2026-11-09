@'
from pathlib import Path
from fastapi import HTTPException, UploadFile
from backend.shared.config import settings

def validate_extension(filename: str):
    extension = Path(filename).suffix.lower()
    if extension not in settings.allowed_extensions:
        raise HTTPException(status_code=415, detail="Unsupported video format.")
    return extension

def validate_file_size(size: int):
    maximum_size = settings.max_upload_size_mb * 1024 * 1024
    if size <= 0:
        raise HTTPException(status_code=400, detail="Empty files are not allowed.")
    if size > maximum_size:
        raise HTTPException(status_code=413, detail="Video exceeds the maximum upload size.")

async def validate_upload(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    return validate_extension(file.filename)
'@ | Set-Content -Encoding utf8 backend/upload_service/app/validators.py