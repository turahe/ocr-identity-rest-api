"""
Unit tests for MediaManager utility functions
"""
import pytest
import time
from app.utils.media_utils import (
    MediaManager,
    attach_media_to_user,
    attach_media_to_document,
    get_user_media,
    get_document_media
)
from app.models.media import Media
from app.models.mediable import Mediable
import uuid


class TestMediaManager:
    """Test cases for MediaManager utility class"""
    
    def test_create_media(self, db_session, sample_user):
        """Test creating media using MediaManager"""
        media = MediaManager.create_media(
            db=db_session,
            name="Test Media",
            file_name="test.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id,
            hash="testhash123",
            custom_attribute="test_attr",
            parent_id=None
        )
        
        assert media.id is not None
        assert media.name == "Test Media"
        assert media.file_name == "test.jpg"
        assert media.disk == "s3"
        assert media.mime_type == "image/jpeg"
        assert media.size == 1024000
        assert media.created_by == sample_user.id
        assert media.hash == "testhash123"
        assert media.custom_attribute == "test_attr"
        assert media.created_at is not None
        assert media.updated_at is not None
    
    def test_create_media_with_parent(self, db_session, sample_user):
        """Test creating media with parent relationship"""
        parent_media = MediaManager.create_media(
            db=db_session,
            name="Parent Media",
            file_name="parent.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=2048000,
            created_by=sample_user.id
        )
        
        child_media = MediaManager.create_media(
            db=db_session,
            name="Child Media",
            file_name="child.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id,
            parent_id=parent_media.id
        )
        
        assert child_media.parent_id == parent_media.id
        assert child_media.parent == parent_media
    
    def test_delete_media(self, db_session, sample_media, sample_user):
        """Test soft deleting media"""
        result = MediaManager.delete_media(
            db=db_session,
            media=sample_media,
            deleted_by=sample_user.id
        )
        
        assert result is True
        assert sample_media.deleted_at is not None
        assert sample_media.deleted_by == sample_user.id
    
    def test_attach_media_to_model(self, db_session, sample_user, sample_media):
        """Test attaching media to a model"""
        mediable = MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        assert mediable.media_id == sample_media.id
        assert mediable.mediable_id == sample_user.id
        assert mediable.mediable_type == "User"
        assert mediable.group == "profile"
    
    def test_detach_media_from_model(self, db_session, sample_user, sample_media):
        """Test detaching media from a model"""
        # First attach
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Then detach
        result = MediaManager.detach_media_from_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        assert result is True
        
        # Verify it's gone
        mediable = db_session.query(Mediable).filter(
            Mediable.media_id == sample_media.id,
            Mediable.mediable_id == sample_user.id
        ).first()
        
        assert mediable is None
    
    def test_detach_media_not_found(self, db_session, sample_user, sample_media):
        """Test detaching media that doesn't exist"""
        result = MediaManager.detach_media_from_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        assert result is False
    
    def test_get_model_media(self, db_session, sample_user, sample_media):
        """Test getting media for a model"""
        # Attach media
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Get media
        media_list = MediaManager.get_model_media(db_session, sample_user)
        
        assert len(media_list) == 1
        assert media_list[0] == sample_media
    
    def test_get_model_media_by_group(self, db_session, sample_user, sample_media):
        """Test getting media for a model by group"""
        # Attach media to different groups
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Create another media
        media2 = MediaManager.create_media(
            db=db_session,
            name="Avatar",
            file_name="avatar.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=512000,
            created_by=sample_user.id
        )
        
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=media2,
            group="avatar"
        )
        
        # Get media by group
        profile_media = MediaManager.get_model_media(db_session, sample_user, group="profile")
        avatar_media = MediaManager.get_model_media(db_session, sample_user, group="avatar")
        
        assert len(profile_media) == 1
        assert profile_media[0] == sample_media
        assert len(avatar_media) == 1
        assert avatar_media[0] == media2
    
    def test_get_media_by_type_and_id(self, db_session, sample_user, sample_media):
        """Test getting media by type and ID"""
        # Attach media
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Get media by type and ID
        media_list = MediaManager.get_media_by_type_and_id(
            db_session,
            "User",
            str(sample_user.id)
        )
        
        assert len(media_list) == 1
        assert media_list[0] == sample_media
    
    def test_get_media_relationships(self, db_session, sample_media, sample_user):
        """Test getting media relationships"""
        # Create relationships
        mediable1 = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        mediable2 = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="avatar"
        )
        
        db_session.add_all([mediable1, mediable2])
        db_session.commit()
        
        # Get relationships
        relationships = MediaManager.get_media_relationships(db_session, sample_media)
        
        assert len(relationships) == 2
        assert relationships[0].mediable_type == "User"
        assert relationships[1].mediable_type == "User"
    
    def test_get_media_by_type(self, db_session, sample_user, sample_media):
        """Test getting media by MIME type"""
        # Attach media
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Get media by type
        jpeg_media = MediaManager.get_media_by_type(db_session, sample_user, "image/jpeg")
        
        assert len(jpeg_media) == 1
        assert jpeg_media[0] == sample_media
    
    def test_get_media_by_type_no_match(self, db_session, sample_user, sample_media):
        """Test getting media by MIME type with no matches"""
        # Attach media
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Get media by type that doesn't match
        png_media = MediaManager.get_media_by_type(db_session, sample_user, "image/png")
        
        assert len(png_media) == 0


class TestConvenienceFunctions:
    """Test cases for convenience functions"""
    
    def test_attach_media_to_user(self, db_session, sample_user, sample_media):
        """Test attach_media_to_user convenience function"""
        mediable = attach_media_to_user(db_session, sample_user, sample_media, group="profile")
        
        assert mediable.media_id == sample_media.id
        assert mediable.mediable_id == sample_user.id
        assert mediable.mediable_type == "User"
        assert mediable.group == "profile"
    
    def test_attach_media_to_document(self, db_session, sample_document, sample_media):
        """Test attach_media_to_document convenience function"""
        mediable = attach_media_to_document(db_session, sample_document, sample_media, group="front")
        
        assert mediable.media_id == sample_media.id
        assert mediable.mediable_id == sample_document.id
        assert mediable.mediable_type == "IdentityDocument"
        assert mediable.group == "front"
    
    def test_get_user_media(self, db_session, sample_user, sample_media):
        """Test get_user_media convenience function"""
        # Attach media
        attach_media_to_user(db_session, sample_user, sample_media, group="profile")
        
        # Get media
        media_list = get_user_media(db_session, sample_user)
        
        assert len(media_list) == 1
        assert media_list[0] == sample_media
    
    def test_get_user_media_by_group(self, db_session, sample_user, sample_media):
        """Test get_user_media with group filter"""
        # Attach media
        attach_media_to_user(db_session, sample_user, sample_media, group="profile")
        
        # Get media by group
        media_list = get_user_media(db_session, sample_user, group="profile")
        
        assert len(media_list) == 1
        assert media_list[0] == sample_media
    
    def test_get_document_media(self, db_session, sample_document, sample_media):
        """Test get_document_media convenience function"""
        # Attach media
        attach_media_to_document(db_session, sample_document, sample_media, group="front")
        
        # Get media
        media_list = get_document_media(db_session, sample_document)
        
        assert len(media_list) == 1
        assert media_list[0] == sample_media
    
    def test_get_document_media_by_group(self, db_session, sample_document, sample_media):
        """Test get_document_media with group filter"""
        # Attach media
        attach_media_to_document(db_session, sample_document, sample_media, group="front")
        
        # Get media by group
        media_list = get_document_media(db_session, sample_document, group="front")
        
        assert len(media_list) == 1
        assert media_list[0] == sample_media


class TestMediaManagerEdgeCases:
    """Test cases for edge cases and error conditions"""
    
    def test_create_media_minimal_required_fields(self, db_session, sample_user):
        """Test creating media with only required fields"""
        media = MediaManager.create_media(
            db=db_session,
            name="Minimal Media",
            file_name="minimal.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024,
            created_by=sample_user.id
        )
        
        assert media.id is not None
        assert media.name == "Minimal Media"
        assert media.file_name == "minimal.jpg"
        assert media.disk == "local"
        assert media.mime_type == "image/jpeg"
        assert media.size == 1024
        assert media.created_by == sample_user.id
    
    def test_attach_media_multiple_groups(self, db_session, sample_user, sample_media):
        """Test attaching same media to multiple groups"""
        # Attach to profile group
        mediable1 = MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        # Attach to avatar group
        mediable2 = MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="avatar"
        )
        
        assert mediable1.media_id == sample_media.id
        assert mediable2.media_id == sample_media.id
        assert mediable1.group == "profile"
        assert mediable2.group == "avatar"
        
        # Verify both relationships exist
        relationships = MediaManager.get_media_relationships(db_session, sample_media)
        assert len(relationships) == 2
    
    def test_detach_media_specific_group(self, db_session, sample_user, sample_media):
        """Test detaching media from specific group only"""
        # Attach to multiple groups
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        MediaManager.attach_media_to_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="avatar"
        )
        
        # Detach only from profile group
        result = MediaManager.detach_media_from_model(
            db=db_session,
            model=sample_user,
            media=sample_media,
            group="profile"
        )
        
        assert result is True
        
        # Verify avatar relationship still exists
        relationships = MediaManager.get_media_relationships(db_session, sample_media)
        assert len(relationships) == 1
        assert relationships[0].group == "avatar"
    
    def test_get_model_media_empty(self, db_session, sample_user):
        """Test getting media for model with no media"""
        media_list = MediaManager.get_model_media(db_session, sample_user)
        
        assert len(media_list) == 0
    
    def test_get_media_by_type_and_id_not_found(self, db_session):
        """Test getting media by type and ID that doesn't exist"""
        media_list = MediaManager.get_media_by_type_and_id(
            db_session,
            "User",
            str(uuid.uuid4())
        )
        
        assert len(media_list) == 0 