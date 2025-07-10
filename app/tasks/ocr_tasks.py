"""
Celery tasks for OCR processing
"""
import os
import tempfile
import time
from typing import Dict, Any, Optional
from app.core.celery_app import celery_app
from app.services.s3_service import s3_service
from app.core.database_session import get_db
from app.models.media import Media
from app.models.ocr_job import OCRJob
from app.services.extract_text_identity import read_image


@celery_app.task(bind=True)
def process_ocr_image(self, media_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process OCR on uploaded image
    
    Args:
        media_id: ID of the media record
        user_id: Optional user ID for tracking
        
    Returns:
        Dict containing OCR results and job status
    """
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"status": "Downloading file from S3", "progress": 10}
        )
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get media record
            media = db.query(Media).filter(Media.id == media_id).first()
            if not media:
                raise Exception(f"Media record not found: {media_id}")
            
            # Create OCR job record
            ocr_job = OCRJob(
                user_id=user_id,
                document_id=None,  # Will be set later if needed
                job_status="processing",
                input_file_path=media.file_name,
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
            db.add(ocr_job)
            db.commit()
            db.refresh(ocr_job)
            
            # Update task status
            self.update_state(
                state="PROGRESS",
                meta={"status": "Processing OCR", "progress": 30}
            )
            
            # Download file from S3
            file_content = s3_service.download_file(media.file_name)
            
            # Create temporary file for OCR processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(media.file_name)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Process OCR
                ocr = read_image(temp_file_path)
                extracted_text = ocr.output()
                
                # Update task status
                self.update_state(
                    state="PROGRESS",
                    meta={"status": "Saving results", "progress": 80}
                )
                
                # Update OCR job with results
                ocr_job.job_status = "completed"
                ocr_job.output_data = {
                    "extracted_text": extracted_text,
                    "confidence": getattr(ocr, 'confidence', None),
                    "processing_time_ms": int((time.time() - ocr_job.created_at) * 1000)
                }
                ocr_job.updated_at = int(time.time())
                
                # Update media record with OCR results
                media.custom_attribute = f"ocr_processed_{ocr_job.id}"
                
                db.commit()
                
                return {
                    "status": "success",
                    "media_id": media_id,
                    "ocr_job_id": str(ocr_job.id),
                    "extracted_text": extracted_text,
                    "processing_time_ms": ocr_job.output_data["processing_time_ms"]
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        finally:
            db.close()
            
    except Exception as e:
        # Update OCR job with error
        try:
            db = next(get_db())
            ocr_job = db.query(OCRJob).filter(OCRJob.id == ocr_job.id).first()
            if ocr_job:
                ocr_job.job_status = "failed"
                ocr_job.error_message = str(e)
                ocr_job.updated_at = int(time.time())
                db.commit()
        except:
            pass
        
        raise Exception(f"OCR processing failed: {str(e)}")


@celery_app.task(bind=True)
def process_bulk_ocr(self, media_ids: list, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process OCR on multiple images
    
    Args:
        media_ids: List of media IDs to process
        user_id: Optional user ID for tracking
        
    Returns:
        Dict containing bulk processing results
    """
    results = []
    total = len(media_ids)
    
    for i, media_id in enumerate(media_ids):
        try:
            # Update progress
            progress = int((i / total) * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": f"Processing {i+1}/{total}",
                    "progress": progress,
                    "current": media_id
                }
            )
            
            # Process individual OCR
            result = process_ocr_image.delay(media_id, user_id)
            results.append({
                "media_id": media_id,
                "task_id": result.id,
                "status": "queued"
            })
            
        except Exception as e:
            results.append({
                "media_id": media_id,
                "error": str(e),
                "status": "failed"
            })
    
    return {
        "status": "completed",
        "total_processed": len(results),
        "results": results
    }


@celery_app.task
def cleanup_failed_ocr_jobs():
    """Clean up failed OCR jobs older than 24 hours"""
    try:
        import time
        from app.core.database_session import get_db
        from app.models.ocr_job import OCRJob
        
        db = next(get_db())
        
        # Delete failed jobs older than 24 hours
        cutoff_time = int(time.time()) - (24 * 60 * 60)
        deleted_count = db.query(OCRJob).filter(
            OCRJob.job_status == "failed",
            OCRJob.created_at < cutoff_time
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close() 