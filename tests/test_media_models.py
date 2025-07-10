"""
Unit tests for Media and Mediable models
"""
import pytest
import uuid
from app.models.media import Media
from app.models.mediable import Mediable
from app.models.user import User
from app.models.identity_document import IdentityDocument


class TestMediaModel:
    """Test cases for Media model"""
    
    def test_media_creation(self, db_session, sample_user):
        """Test creating a media record"""
        media = Media(
            name="Test Media",
            file_name="test.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id,
            hash="testhash123",
            custom_attribute="test_attr"
        )
        
        db_session.add(media)
        db_session.commit()
        db_session.refresh(media)
        
        assert media.id is not None
        assert media.name == "Test Media"
        assert media.file_name == "test.jpg"
        assert media.disk == "local"
        assert media.mime_type == "image/jpeg"
        assert media.size == 1024000
        assert media.created_by == sample_user.id
        assert media.hash == "testhash123"
        assert media.custom_attribute == "test_attr"
    
    def test_media_with_parent(self, db_session, sample_user):
        """Test creating media with parent relationship"""
        parent_media = Media(
            name="Parent Media",
            file_name="parent.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=2048000,
            created_by=sample_user.id
        )
        db_session.add(parent_media)
        db_session.commit()
        
        child_media = Media(
            name="Child Media",
            file_name="child.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id,
            parent_id=parent_media.id
        )
        db_session.add(child_media)
        db_session.commit()
        db_session.refresh(child_media)
        
        assert child_media.parent_id == parent_media.id
        assert child_media.parent == parent_media
        assert len(parent_media.children) == 1
        assert parent_media.children[0] == child_media
    
    def test_media_soft_delete(self, db_session, sample_user):
        """Test soft deleting a media record"""
        media = Media(
            name="Test Media",
            file_name="test.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id
        )
        db_session.add(media)
        db_session.commit()
        db_session.refresh(media)
        
        # Soft delete
        media.deleted_at = 1234567890
        media.deleted_by = sample_user.id
        db_session.commit()
        
        assert media.deleted_at == 1234567890
        assert media.deleted_by == sample_user.id
    
    def test_media_repr(self, sample_media):
        """Test media string representation"""
        expected = f"<Media(id={sample_media.id}, name='{sample_media.name}', file_name='{sample_media.file_name}')>"
        assert repr(sample_media) == expected
    
    def test_media_polymorphic_relationships(self, db_session, sample_media, sample_user):
        """Test polymorphic relationships property"""
        # Create mediable relationships
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
        
        relationships = sample_media.polymorphic_relationships
        
        assert "User" in relationships
        assert len(relationships["User"]) == 2
        assert relationships["User"][0].group == "profile"
        assert relationships["User"][1].group == "avatar"


class TestMediableModel:
    """Test cases for Mediable model"""
    
    def test_mediable_creation(self, db_session, sample_media, sample_user):
        """Test creating a mediable relationship"""
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        db_session.add(mediable)
        db_session.commit()
        db_session.refresh(mediable)
        
        assert mediable.media_id == sample_media.id
        assert mediable.mediable_id == sample_user.id
        assert mediable.mediable_type == "User"
        assert mediable.group == "profile"
    
    def test_mediable_repr(self, sample_mediable):
        """Test mediable string representation"""
        expected = f"<Mediable(media_id={sample_mediable.media_id}, mediable_type='{sample_mediable.mediable_type}', mediable_id={sample_mediable.mediable_id})>"
        assert repr(sample_mediable) == expected
    
    def test_mediable_relationship(self, sample_mediable, sample_media):
        """Test mediable relationship to media"""
        assert sample_mediable.media == sample_media
        assert sample_media.mediables[0] == sample_mediable


class TestUserMediaRelationships:
    """Test cases for User model media relationships"""
    
    def test_user_media_property(self, db_session, sample_user, sample_media):
        """Test user media property"""
        # Create mediable relationship
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        db_session.add(mediable)
        db_session.commit()
        
        # Test media property
        user_media = sample_user.media
        assert len(user_media) == 1
        assert user_media[0] == sample_media
    
    def test_user_get_media_by_group(self, db_session, sample_user, sample_media):
        """Test getting user media by group"""
        # Create mediable relationships
        mediable1 = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        # Create another media for different group
        media2 = Media(
            name="Avatar",
            file_name="avatar.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=512000,
            created_by=sample_user.id
        )
        db_session.add(media2)
        db_session.commit()
        
        mediable2 = Mediable(
            media_id=media2.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="avatar"
        )
        
        db_session.add_all([mediable1, mediable2])
        db_session.commit()
        
        # Test group filtering
        profile_media = sample_user.get_media_by_group("profile")
        avatar_media = sample_user.get_media_by_group("avatar")
        
        assert len(profile_media) == 1
        assert profile_media[0] == sample_media
        assert len(avatar_media) == 1
        assert avatar_media[0] == media2
    
    def test_user_media_relationships(self, db_session, sample_user, sample_media):
        """Test user media_relationships property"""
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        db_session.add(mediable)
        db_session.commit()
        
        relationships = sample_user.media_relationships
        assert len(relationships) == 1
        assert relationships[0].media_id == sample_media.id
        assert relationships[0].mediable_type == "User"


class TestIdentityDocumentMediaRelationships:
    """Test cases for IdentityDocument model media relationships"""
    
    def test_document_media_property(self, db_session, sample_document, sample_media):
        """Test document media property"""
        # Create mediable relationship
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_document.id,
            mediable_type="IdentityDocument",
            group="front"
        )
        db_session.add(mediable)
        db_session.commit()
        
        # Test media property
        document_media = sample_document.media
        assert len(document_media) == 1
        assert document_media[0] == sample_media
    
    def test_document_get_media_by_group(self, db_session, sample_document, sample_media):
        """Test getting document media by group"""
        # Create mediable relationships
        mediable1 = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_document.id,
            mediable_type="IdentityDocument",
            group="front"
        )
        
        # Create another media for back
        media2 = Media(
            name="Document Back",
            file_name="back.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1536000,
            created_by=sample_document.user_id
        )
        db_session.add(media2)
        db_session.commit()
        
        mediable2 = Mediable(
            media_id=media2.id,
            mediable_id=sample_document.id,
            mediable_type="IdentityDocument",
            group="back"
        )
        
        db_session.add_all([mediable1, mediable2])
        db_session.commit()
        
        # Test group filtering
        front_media = sample_document.get_media_by_group("front")
        back_media = sample_document.get_media_by_group("back")
        
        assert len(front_media) == 1
        assert front_media[0] == sample_media
        assert len(back_media) == 1
        assert back_media[0] == media2
    
    def test_document_media_relationships(self, db_session, sample_document, sample_media):
        """Test document media_relationships property"""
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_document.id,
            mediable_type="IdentityDocument",
            group="front"
        )
        db_session.add(mediable)
        db_session.commit()
        
        relationships = sample_document.media_relationships
        assert len(relationships) == 1
        assert relationships[0].media_id == sample_media.id
        assert relationships[0].mediable_type == "IdentityDocument" 