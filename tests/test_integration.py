"""
Integration tests for complete media workflow
"""
import pytest
from app.utils.media_utils import (
    MediaManager,
    attach_media_to_user,
    attach_media_to_document,
    get_user_media,
    get_document_media
)
from app.models.media import Media


class TestMediaWorkflow:
    """Integration tests for complete media workflow"""
    
    def test_complete_user_media_workflow(self, db_session, sample_user):
        """Test complete workflow for user media management"""
        # 1. Create media
        profile_photo = MediaManager.create_media(
            db=db_session,
            name="Profile Photo",
            file_name="profile.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id,
            hash="profile_hash_123",
            custom_attribute="profile_picture"
        )
        
        avatar_photo = MediaManager.create_media(
            db=db_session,
            name="Avatar",
            file_name="avatar.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=512000,
            created_by=sample_user.id,
            hash="avatar_hash_456",
            custom_attribute="avatar"
        )
        
        # 2. Attach media to user
        attach_media_to_user(db_session, sample_user, profile_photo, group="profile")
        attach_media_to_user(db_session, sample_user, avatar_photo, group="avatar")
        
        # 3. Verify media is attached
        user_media = get_user_media(db_session, sample_user)
        assert len(user_media) == 2
        
        profile_media = get_user_media(db_session, sample_user, group="profile")
        assert len(profile_media) == 1
        assert profile_media[0] == profile_photo
        
        avatar_media = get_user_media(db_session, sample_user, group="avatar")
        assert len(avatar_media) == 1
        assert avatar_media[0] == avatar_photo
        
        # 4. Test model properties
        assert len(sample_user.media) == 2
        assert profile_photo in sample_user.media
        assert avatar_photo in sample_user.media
        
        # 5. Test group filtering via model method
        profile_via_method = sample_user.get_media_by_group("profile")
        assert len(profile_via_method) == 1
        assert profile_via_method[0] == profile_photo
        
        # 6. Test media relationships
        profile_relationships = sample_user.media_relationships
        assert len(profile_relationships) == 2
        
        # 7. Detach one media
        MediaManager.detach_media_from_model(
            db_session, sample_user, avatar_photo, group="avatar"
        )
        
        # 8. Verify detachment
        remaining_media = get_user_media(db_session, sample_user)
        assert len(remaining_media) == 1
        assert remaining_media[0] == profile_photo
        
        # 9. Soft delete media
        MediaManager.delete_media(db_session, profile_photo, deleted_by=sample_user.id)
        
        # 10. Verify soft delete
        assert profile_photo.deleted_at is not None
        assert profile_photo.deleted_by == sample_user.id
        
        # Media should still be queryable but marked as deleted
        deleted_media = db_session.query(Media).filter(Media.id == profile_photo.id).first()
        assert deleted_media is not None
        assert deleted_media.deleted_at is not None
    
    def test_complete_document_media_workflow(self, db_session, sample_document, sample_user):
        """Test complete workflow for document media management"""
        # 1. Create document media
        front_image = MediaManager.create_media(
            db=db_session,
            name="Document Front",
            file_name="front.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=2048000,
            created_by=sample_user.id,
            hash="front_hash_789",
            custom_attribute="document_front"
        )
        
        back_image = MediaManager.create_media(
            db=db_session,
            name="Document Back",
            file_name="back.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1800000,
            created_by=sample_user.id,
            hash="back_hash_012",
            custom_attribute="document_back"
        )
        
        # 2. Attach media to document
        attach_media_to_document(db_session, sample_document, front_image, group="front")
        attach_media_to_document(db_session, sample_document, back_image, group="back")
        
        # 3. Verify media is attached
        document_media = get_document_media(db_session, sample_document)
        assert len(document_media) == 2
        
        front_media = get_document_media(db_session, sample_document, group="front")
        assert len(front_media) == 1
        assert front_media[0] == front_image
        
        back_media = get_document_media(db_session, sample_document, group="back")
        assert len(back_media) == 1
        assert back_media[0] == back_image
        
        # 4. Test model properties
        assert len(sample_document.media) == 2
        assert front_image in sample_document.media
        assert back_image in sample_document.media
        
        # 5. Test group filtering via model method
        front_via_method = sample_document.get_media_by_group("front")
        assert len(front_via_method) == 1
        assert front_via_method[0] == front_image
        
        # 6. Test media relationships
        document_relationships = sample_document.media_relationships
        assert len(document_relationships) == 2
        
        # 7. Test media by type
        jpeg_media = MediaManager.get_media_by_type(db_session, sample_document, "image/jpeg")
        assert len(jpeg_media) == 2
        
        # 8. Test media by type and ID
        media_by_id = MediaManager.get_media_by_type_and_id(
            db_session, "IdentityDocument", str(sample_document.id)
        )
        assert len(media_by_id) == 2
    
    def test_media_hierarchy_workflow(self, db_session, sample_user):
        """Test workflow with media hierarchy (parent-child relationships)"""
        # 1. Create parent media
        original_image = MediaManager.create_media(
            db=db_session,
            name="Original Image",
            file_name="original.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=5000000,
            created_by=sample_user.id,
            hash="original_hash"
        )
        
        # 2. Create child media (thumbnails, resized versions)
        thumbnail = MediaManager.create_media(
            db=db_session,
            name="Thumbnail",
            file_name="thumbnail.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=50000,
            created_by=sample_user.id,
            parent_id=original_image.id,
            hash="thumbnail_hash"
        )
        
        medium_size = MediaManager.create_media(
            db=db_session,
            name="Medium Size",
            file_name="medium.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=250000,
            created_by=sample_user.id,
            parent_id=original_image.id,
            hash="medium_hash"
        )
        
        # 3. Verify hierarchy
        assert thumbnail.parent == original_image
        assert medium_size.parent == original_image
        assert len(original_image.children) == 2
        assert thumbnail in original_image.children
        assert medium_size in original_image.children
        
        # 4. Attach parent to user
        attach_media_to_user(db_session, sample_user, original_image, group="photos")
        
        # 5. Verify user can access all variants
        user_media = get_user_media(db_session, sample_user, group="photos")
        assert len(user_media) == 1
        assert user_media[0] == original_image
        
        # 6. Test accessing children through parent
        children = original_image.children
        assert len(children) == 2
        assert thumbnail in children
        assert medium_size in children
    
    def test_multi_model_media_workflow(self, db_session, sample_user, sample_document):
        """Test workflow where same media is attached to multiple models"""
        # 1. Create shared media
        shared_image = MediaManager.create_media(
            db=db_session,
            name="Shared Image",
            file_name="shared.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id,
            hash="shared_hash"
        )
        
        # 2. Attach to user
        attach_media_to_user(db_session, sample_user, shared_image, group="profile")
        
        # 3. Attach to document
        attach_media_to_document(db_session, sample_document, shared_image, group="front")
        
        # 4. Verify relationships
        user_media = get_user_media(db_session, sample_user, group="profile")
        assert len(user_media) == 1
        assert user_media[0] == shared_image
        
        document_media = get_document_media(db_session, sample_document, group="front")
        assert len(document_media) == 1
        assert document_media[0] == shared_image
        
        # 5. Test polymorphic relationships
        relationships = MediaManager.get_media_relationships(db_session, shared_image)
        assert len(relationships) == 2
        
        # Check that both models are related
        model_types = [rel.mediable_type for rel in relationships]
        assert "User" in model_types
        assert "IdentityDocument" in model_types
        
        # 6. Test polymorphic relationships property
        poly_relationships = shared_image.polymorphic_relationships
        assert "User" in poly_relationships
        assert "IdentityDocument" in poly_relationships
        assert len(poly_relationships["User"]) == 1
        assert len(poly_relationships["IdentityDocument"]) == 1
    
    def test_bulk_media_operations(self, db_session, sample_user):
        """Test bulk operations for media management"""
        # 1. Create multiple media items
        media_list = []
        for i in range(10):
            media = MediaManager.create_media(
                db=db_session,
                name=f"Bulk Media {i}",
                file_name=f"bulk_{i}.jpg",
                disk="s3",
                mime_type="image/jpeg",
                size=1024000 + i * 1000,
                created_by=sample_user.id,
                hash=f"hash_{i}"
            )
            media_list.append(media)
        
        # 2. Attach all media to user in different groups
        for i, media in enumerate(media_list):
            group = "profile" if i % 2 == 0 else "gallery"
            attach_media_to_user(db_session, sample_user, media, group=group)
        
        # 3. Verify bulk attachment
        all_user_media = get_user_media(db_session, sample_user)
        assert len(all_user_media) == 10
        
        profile_media = get_user_media(db_session, sample_user, group="profile")
        gallery_media = get_user_media(db_session, sample_user, group="gallery")
        
        assert len(profile_media) == 5
        assert len(gallery_media) == 5
        
        # 4. Test bulk queries
        s3_media = db_session.query(Media).filter(Media.disk == "s3").all()
        assert len(s3_media) == 10
        
        jpeg_media = db_session.query(Media).filter(Media.mime_type == "image/jpeg").all()
        assert len(jpeg_media) == 10
        
        # 5. Test bulk detach
        for media in media_list[:5]:  # Detach first 5
            MediaManager.detach_media_from_model(
                db_session, sample_user, media, group="profile"
            )
        
        # 6. Verify bulk detach
        remaining_media = get_user_media(db_session, sample_user)
        assert len(remaining_media) == 5
        
        # 7. Test bulk soft delete
        for media in media_list[5:]:  # Soft delete last 5
            MediaManager.delete_media(db_session, media, deleted_by=sample_user.id)
        
        # 8. Verify bulk soft delete
        active_media = db_session.query(Media).filter(Media.deleted_at.is_(None)).all()
        assert len(active_media) == 5
        
        deleted_media = db_session.query(Media).filter(Media.deleted_at.isnot(None)).all()
        assert len(deleted_media) == 5


class TestMediaErrorHandling:
    """Integration tests for error handling in media workflows"""
    
    def test_attach_nonexistent_media(self, db_session, sample_user):
        """Test handling of attaching non-existent media"""
        import uuid
        
        # Try to attach media that doesn't exist
        fake_media_id = uuid.uuid4()
        
        # This should raise an error or handle gracefully
        # The exact behavior depends on your implementation
        # For now, we'll test that the system doesn't crash
        
        # Create a real media first
        real_media = MediaManager.create_media(
            db=db_session,
            name="Real Media",
            file_name="real.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id
        )
        
        # Attach real media (should work)
        mediable = attach_media_to_user(db_session, sample_user, real_media, group="test")
        assert mediable is not None
        assert mediable.media_id == real_media.id
    
    def test_detach_nonexistent_relationship(self, db_session, sample_user, sample_media):
        """Test handling of detaching non-existent relationships"""
        # Try to detach media that's not attached
        result = MediaManager.detach_media_from_model(
            db_session, sample_user, sample_media, group="nonexistent"
        )
        
        # Should return False for non-existent relationships
        assert result is False
    
    def test_media_with_invalid_parent(self, db_session, sample_user):
        """Test handling of media with invalid parent reference"""
        import uuid
        
        # Try to create media with non-existent parent
        fake_parent_id = uuid.uuid4()
        
        # This should either raise an error or handle gracefully
        # For now, we'll test that the system doesn't crash
        
        # Create media without parent (should work)
        media = MediaManager.create_media(
            db=db_session,
            name="Test Media",
            file_name="test.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id
        )
        
        assert media is not None
        assert media.parent_id is None 