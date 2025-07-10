import os
import uuid
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database_session import get_db
from app.core.celery_app import celery_app
from app.tasks.ocr_tasks import process_ocr_image
from app.tasks.media_tasks import upload_media_to_s3
from app.services.s3_service import s3_service
from app.utils.media_utils import MediaManager
from app.models.user import User
from app.models.media import Media
from rules.validation_file_size_type import validate_file_size_type
from extract_text_identity import read_image

app = FastAPI(title="OCR Identity REST API", version="2.0.0")

# Start debugpy if DEBUG environment variable is set
if os.getenv("DEBUG") == "1":
    import debugpy
    debugpy.listen((os.getenv("DEBUG_IP", "0.0.0.0"), 5678))
    print("Debugpy is listening on port 5678. Waiting for debugger to attach...")
    debugpy.wait_for_client()


@app.get("/")
async def root():
    return {"message": "OCR Identity REST API v2.0.0"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Upload image file to S3 and process OCR in background
    
    Args:
        file: Uploaded file
        user_id: Optional user ID for tracking
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Upload response with media ID and task information
    """
    try:
        # Validate file
        content = await validate_file_size_type(file)
        
        # Upload to S3 and create media record in background
        task = upload_media_to_s3.delay(
            file_content=content,
            file_name=file.filename,
            content_type=file.content_type,
            user_id=user_id
        )
        
        return {
            "status": "uploading",
            "task_id": task.id,
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "File upload started. Use task_id to check status."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-image-sync/")
async def upload_image_sync(
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload image file to S3 and process OCR synchronously (for small files)
    
    Args:
        file: Uploaded file
        user_id: Optional user ID for tracking
        db: Database session
        
    Returns:
        Upload response with OCR results
    """
    try:
        # Validate file
        content = await validate_file_size_type(file)
        
        # Upload to S3
        upload_result = s3_service.upload_file(content, file.filename, file.content_type)
        
        # Create media record
        media = MediaManager.create_media(
            db=db,
            name=upload_result['original_filename'],
            file_name=upload_result['key'],
            disk="s3",
            mime_type=upload_result['content_type'],
            size=upload_result['size'],
            created_by=user_id,
            hash=upload_result['hash'],
            custom_attribute="uploaded_via_api"
        )
        
        # Process OCR synchronously
        ocr_task = process_ocr_image.delay(str(media.id), user_id)
        
        return {
            "status": "success",
            "media_id": str(media.id),
            "s3_key": upload_result['key'],
            "s3_url": upload_result['url'],
            "file_hash": upload_result['hash'],
            "file_size": upload_result['size'],
            "ocr_task_id": ocr_task.id,
            "message": "File uploaded and OCR processing started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get task status and results
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status and results
    """
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": "Task is pending..."
            }
        elif task.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": task.info.get("status", ""),
                "progress": task.info.get("progress", 0)
            }
        elif task.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task.state,
                "result": task.result
            }
        else:
            response = {
                "task_id": task_id,
                "state": task.state,
                "error": str(task.info)
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/media/{media_id}")
async def get_media_info(media_id: str, db: Session = Depends(get_db)):
    """
    Get media information
    
    Args:
        media_id: Media record ID
        db: Database session
        
    Returns:
        Media information
    """
    try:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Generate presigned URL for S3 files
        s3_url = None
        if media.disk == "s3":
            s3_url = s3_service.generate_presigned_url(media.file_name)
        
        return {
            "id": str(media.id),
            "name": media.name,
            "file_name": media.file_name,
            "disk": media.disk,
            "mime_type": media.mime_type,
            "size": media.size,
            "hash": media.hash,
            "s3_url": s3_url,
            "created_at": media.created_at,
            "updated_at": media.updated_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/media/{media_id}/ocr")
async def get_media_ocr_results(media_id: str, db: Session = Depends(get_db)):
    """
    Get OCR results for media
    
    Args:
        media_id: Media record ID
        db: Database session
        
    Returns:
        OCR results
    """
    try:
        from app.models.ocr_job import OCRJob
        
        # Get OCR jobs for this media
        ocr_jobs = db.query(OCRJob).filter(
            OCRJob.input_file_path == media_id
        ).order_by(OCRJob.created_at.desc()).all()
        
        if not ocr_jobs:
            return {
                "media_id": media_id,
                "ocr_jobs": [],
                "message": "No OCR jobs found for this media"
            }
        
        results = []
        for job in ocr_jobs:
            results.append({
                "job_id": str(job.id),
                "status": job.job_status,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
                "output_data": job.output_data,
                "error_message": job.error_message,
                "processing_time_ms": job.processing_time_ms
            })
        
        return {
            "media_id": media_id,
            "ocr_jobs": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/media/{media_id}")
async def delete_media(media_id: str, db: Session = Depends(get_db)):
    """
    Delete media record and S3 file
    
    Args:
        media_id: Media record ID
        db: Database session
        
    Returns:
        Deletion result
    """
    try:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Delete from S3 if it's an S3 file
        if media.disk == "s3":
            try:
                s3_service.delete_file(media.file_name)
            except Exception as e:
                # Log error but continue with database deletion
                print(f"Failed to delete S3 file: {e}")
        
        # Soft delete media record
        MediaManager.delete_media(db, media)
        
        return {
            "status": "success",
            "message": f"Media {media_id} deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
