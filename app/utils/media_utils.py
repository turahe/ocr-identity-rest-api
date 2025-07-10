from typing import List, Optional, Type, Union
from sqlalchemy.orm import Session
from app.models.media import Media
from app.models.mediable import Mediable
from app.models.user import User
from app.models.identity_document import IdentityDocument


class MediaManager:
    """Utility class for managing polymorphic media relationships"""
    
    @staticmethod
    def attach_media_to_model(
        db: Session,
        model: Union[User, IdentityDocument],
        media: Media,
        group: str = "default"
    ) -> Mediable:
        """Attach media to a model through polymorphic relationship"""
        mediable = Mediable(
            media_id=media.id,
            mediable_id=model.id,
            mediable_type=model.__class__.__name__,
            group=group
        )
        db.add(mediable)
        db.commit()
        return mediable
    
    @staticmethod
    def detach_media_from_model(
        db: Session,
        model: Union[User, IdentityDocument],
        media: Media,
        group: Optional[str] = None
    ) -> bool:
        """Detach media from a model"""
        query = db.query(Mediable).filter(
            Mediable.media_id == media.id,
            Mediable.mediable_id == model.id,
            Mediable.mediable_type == model.__class__.__name__
        )
        
        if group:
            query = query.filter(Mediable.group == group)
        
        mediable = query.first()
        if mediable:
            db.delete(mediable)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_model_media(
        db: Session,
        model: Union[User, IdentityDocument],
        group: Optional[str] = None
    ) -> List[Media]:
        """Get all media associated with a model"""
        query = db.query(Media).join(Mediable).filter(
            Mediable.mediable_id == model.id,
            Mediable.mediable_type == model.__class__.__name__
        )
        
        if group:
            query = query.filter(Mediable.group == group)
        
        return query.all()
    
    @staticmethod
    def get_media_by_type_and_id(
        db: Session,
        model_type: str,
        model_id: str,
        group: Optional[str] = None
    ) -> List[Media]:
        """Get media by model type and ID"""
        query = db.query(Media).join(Mediable).filter(
            Mediable.mediable_id == model_id,
            Mediable.mediable_type == model_type
        )
        
        if group:
            query = query.filter(Mediable.group == group)
        
        return query.all()
    
    @staticmethod
    def get_media_relationships(
        db: Session,
        media: Media
    ) -> List[Mediable]:
        """Get all relationships for a media item"""
        return db.query(Mediable).filter(Mediable.media_id == media.id).all()
    
    @staticmethod
    def create_media(
        db: Session,
        name: str,
        file_name: str,
        disk: str,
        mime_type: str,
        size: int,
        created_by: Optional[str] = None,
        hash: Optional[str] = None,
        custom_attribute: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Media:
        """Create a new media record"""
        import time
        
        media = Media(
            name=name,
            file_name=file_name,
            disk=disk,
            mime_type=mime_type,
            size=size,
            created_by=created_by,
            hash=hash,
            custom_attribute=custom_attribute,
            parent_id=parent_id,
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        db.add(media)
        db.commit()
        db.refresh(media)
        return media
    
    @staticmethod
    def delete_media(
        db: Session,
        media: Media,
        deleted_by: Optional[str] = None
    ) -> bool:
        """Soft delete a media record"""
        import time
        
        media.deleted_at = int(time.time())
        media.deleted_by = deleted_by
        db.commit()
        return True
    
    @staticmethod
    def get_media_by_group(
        db: Session,
        model: Union[User, IdentityDocument],
        group: str
    ) -> List[Media]:
        """Get media for a model by group"""
        return MediaManager.get_model_media(db, model, group)
    
    @staticmethod
    def get_media_by_type(
        db: Session,
        model: Union[User, IdentityDocument],
        mime_type: str
    ) -> List[Media]:
        """Get media for a model by MIME type"""
        return db.query(Media).join(Mediable).filter(
            Mediable.mediable_id == model.id,
            Mediable.mediable_type == model.__class__.__name__,
            Media.mime_type == mime_type
        ).all()


# Convenience functions
def attach_media_to_user(db: Session, user: User, media: Media, group: str = "default") -> Mediable:
    """Attach media to a user"""
    return MediaManager.attach_media_to_model(db, user, media, group)


def attach_media_to_document(db: Session, document: IdentityDocument, media: Media, group: str = "default") -> Mediable:
    """Attach media to an identity document"""
    return MediaManager.attach_media_to_model(db, document, media, group)


def get_user_media(db: Session, user: User, group: Optional[str] = None) -> List[Media]:
    """Get all media for a user"""
    return MediaManager.get_model_media(db, user, group)


def get_document_media(db: Session, document: IdentityDocument, group: Optional[str] = None) -> List[Media]:
    """Get all media for an identity document"""
    return MediaManager.get_model_media(db, document, group) 