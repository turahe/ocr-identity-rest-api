"""
Celery tasks for media processing
"""
import time
from typing import Dict, Any, Optional
from app.core.celery_app import celery_app
from app.services.s3_service import s3_service
from app.core.database_session import get_db
from app.models.media import Media
from app.utils.media_utils import MediaManager


@celery_app.task(bind=True)
def upload_media_to_s3(self, file_content: bytes, file_name: str, content_type: str, 
                       user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Upload media file to S3 and create database record
    
    Args:
        file_content: File content as bytes
        file_name: Original file name
        content_type: MIME type
        user_id: Optional user ID for tracking
        
    Returns:
        Dict containing upload result and media record
    """
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"status": "Uploading to S3", "progress": 20}
        )
        
        # Upload to S3
        upload_result = s3_service.upload_file(file_content, file_name, content_type)
        
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"status": "Creating database record", "progress": 60}
        )
        
        # Get database session
        db = next(get_db())
        
        try:
            # Create media record
            media = MediaManager.create_media(
                db=db,
                name=upload_result['original_filename'],
                file_name=upload_result['key'],  # Use S3 key as file_name
                disk="s3",
                mime_type=upload_result['content_type'],
                size=upload_result['size'],
                created_by=user_id,
                hash=upload_result['hash'],
                custom_attribute="uploaded_via_api"
            )
            
            # Update task status
            self.update_state(
                state="PROGRESS",
                meta={"status": "Upload completed", "progress": 100}
            )
            
            return {
                "status": "success",
                "media_id": str(media.id),
                "s3_key": upload_result['key'],
                "s3_url": upload_result['url'],
                "file_hash": upload_result['hash'],
                "file_size": upload_result['size'],
                "original_filename": upload_result['original_filename']
            }
            
        finally:
            db.close()
            
    except Exception as e:
        raise Exception(f"Media upload failed: {str(e)}")


@celery_app.task(bind=True)
def process_media_batch(self, files_data: list, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process multiple media files in batch
    
    Args:
        files_data: List of dicts with file content, name, and type
        user_id: Optional user ID for tracking
        
    Returns:
        Dict containing batch processing results
    """
    results = []
    total = len(files_data)
    
    for i, file_data in enumerate(files_data):
        try:
            # Update progress
            progress = int((i / total) * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": f"Processing {i+1}/{total}",
                    "progress": progress
                }
            )
            
            # Upload individual file
            result = upload_media_to_s3.delay(
                file_data['content'],
                file_data['name'],
                file_data['type'],
                user_id
            )
            
            results.append({
                "file_name": file_data['name'],
                "task_id": result.id,
                "status": "queued"
            })
            
        except Exception as e:
            results.append({
                "file_name": file_data['name'],
                "error": str(e),
                "status": "failed"
            })
    
    return {
        "status": "completed",
        "total_processed": len(results),
        "results": results
    }


@celery_app.task
def cleanup_orphaned_media():
    """Clean up media records that don't have S3 files"""
    try:
        from app.core.database_session import get_db
        from app.models.media import Media
        
        db = next(get_db())
        
        # Get all S3 media records
        s3_media = db.query(Media).filter(Media.disk == "s3").all()
        
        cleaned_count = 0
        for media in s3_media:
            try:
                # Check if file exists in S3
                if not s3_service.file_exists(media.file_name):
                    # Mark as deleted
                    MediaManager.delete_media(db, media)
                    cleaned_count += 1
            except Exception:
                # If S3 check fails, skip this record
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task
def generate_media_thumbnails(media_id: str):
    """
    Generate thumbnails for media files
    
    Args:
        media_id: ID of the media record
        
    Returns:
        Dict containing thumbnail generation results
    """
    try:
        from PIL import Image
        import io
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get media record
            media = db.query(Media).filter(Media.id == media_id).first()
            if not media:
                raise Exception(f"Media record not found: {media_id}")
            
            # Only process images
            if not media.mime_type.startswith('image/'):
                return {
                    "status": "skipped",
                    "reason": "Not an image file"
                }
            
            # Download original file
            file_content = s3_service.download_file(media.file_name)
            
            # Create thumbnail
            with Image.open(io.BytesIO(file_content)) as img:
                # Resize to thumbnail size
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Convert to bytes
                thumbnail_buffer = io.BytesIO()
                img.save(thumbnail_buffer, format='JPEG', quality=85)
                thumbnail_content = thumbnail_buffer.getvalue()
            
            # Upload thumbnail to S3
            thumbnail_key = f"thumbnails/{media.file_name}"
            s3_service.upload_file(thumbnail_content, f"thumb_{media.file_name}", "image/jpeg")
            
            # Create thumbnail media record
            thumbnail_media = MediaManager.create_media(
                db=db,
                name=f"Thumbnail - {media.name}",
                file_name=thumbnail_key,
                disk="s3",
                mime_type="image/jpeg",
                size=len(thumbnail_content),
                created_by=media.created_by,
                parent_id=media.id,
                custom_attribute="thumbnail"
            )
            
            return {
                "status": "success",
                "original_media_id": media_id,
                "thumbnail_media_id": str(thumbnail_media.id),
                "thumbnail_size": len(thumbnail_content)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 