import os
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database_session import get_db
from app.core.celery_app import celery_app
from app.tasks.ocr_tasks import process_ocr_image
from app.tasks.media_tasks import upload_media_to_s3
from app.services.s3_service import s3_service
from app.utils.media_utils import MediaManager
from app.models.user import User, UserCreate, UserLogin, UserRead
from app.core.jwt_utils import create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status
from app.models.media import Media
from app.models.people import People
from app.services.people_service import people_service
from rules.validation_file_size_type import validate_file_size_type
from app.api.auth import router as auth_router
from app.api.people import router as people_router
from app.api.media import router as media_router

app = FastAPI(title="OCR Identity REST API", version="2.0.0")

# Start debugpy if DEBUG environment variable is set
if os.getenv("DEBUG") == "1":
    import debugpy
    debugpy.listen((os.getenv("DEBUG_IP", "0.0.0.0"), 5678))
    print("Debugpy is listening on port 5678. Waiting for debugger to attach...")
    debugpy.wait_for_client()

app.include_router(auth_router)
app.include_router(people_router)
app.include_router(media_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "s3": "connected"
        }
    }


# Command to run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
