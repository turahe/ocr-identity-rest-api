from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.media import Media
from app.services.s3_service import s3_service
from app.utils.media_utils import MediaManager
from app.core.database_session import get_db
from app.api.auth import get_current_user_or_apikey

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/{media_id}")
async def get_media_info(media_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user_or_apikey)):
    try:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        s3_url = None
        if str(media.disk) == "s3":
            s3_url = s3_service.generate_presigned_url(str(media.file_name))
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

@router.delete("/{media_id}")
async def delete_media(media_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user_or_apikey)):
    try:
        from uuid import UUID
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        if str(media.disk) == "s3":
            try:
                s3_service.delete_file(str(media.file_name))
            except Exception as e:
                print(f"Failed to delete S3 file: {e}")
        # Use authenticated user's UUID for deleted_by
        if hasattr(current_user, 'id'):
            deleted_by_uuid = str(current_user.id)
        else:
            raise HTTPException(status_code=401, detail="No user UUID available from authentication")
        MediaManager.delete_media(db, media, deleted_by=deleted_by_uuid)
        return {
            "status": "success",
            "message": f"Media {media_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 