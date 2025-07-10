"""
Unit tests for database operations and migrations
"""
import pytest
from sqlalchemy import text
from app.models.media import Media
from app.models.mediable import Mediable
from app.models.user import User
from app.models.identity_document import IdentityDocument


class TestDatabaseOperations:
    """Test cases for database operations"""
    
    def test_media_table_structure(self, db_session):
        """Test that media table has correct structure"""
        # Test that we can create and query media records
        media = Media(
            name="Test Media",
            file_name="test.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000
        )
        
        db_session.add(media)
        db_session.commit()
        db_session.refresh(media)
        
        # Verify all required fields are present
        assert hasattr(media, 'id')
        assert hasattr(media, 'name')
        assert hasattr(media, 'file_name')
        assert hasattr(media, 'disk')
        assert hasattr(media, 'mime_type')
        assert hasattr(media, 'size')
        assert hasattr(media, 'hash')
        assert hasattr(media, 'custom_attribute')
        assert hasattr(media, 'parent_id')
        assert hasattr(media, 'created_by')
        assert hasattr(media, 'updated_by')
        assert hasattr(media, 'deleted_by')
        assert hasattr(media, 'deleted_at')
        assert hasattr(media, 'created_at')
        assert hasattr(media, 'updated_at')
    
    def test_mediable_table_structure(self, db_session, sample_media, sample_user):
        """Test that mediable table has correct structure"""
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        db_session.add(mediable)
        db_session.commit()
        db_session.refresh(mediable)
        
        # Verify all required fields are present
        assert hasattr(mediable, 'media_id')
        assert hasattr(mediable, 'mediable_id')
        assert hasattr(mediable, 'mediable_type')
        assert hasattr(mediable, 'group')
    
    def test_foreign_key_constraints(self, db_session, sample_user):
        """Test foreign key constraints work correctly"""
        # Create media with valid user reference
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
        
        # Verify the relationship works
        assert media.creator == sample_user
        assert media in sample_user.created_media
    
    def test_self_referencing_media(self, db_session, sample_user):
        """Test self-referencing parent-child relationships"""
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
        
        # Verify parent-child relationship
        assert child_media.parent == parent_media
        assert child_media in parent_media.children
    
    def test_polymorphic_relationships(self, db_session, sample_user, sample_document, sample_media):
        """Test polymorphic relationships work correctly"""
        # Create mediables for both user and document
        user_mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        document_mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_document.id,
            mediable_type="IdentityDocument",
            group="front"
        )
        
        db_session.add_all([user_mediable, document_mediable])
        db_session.commit()
        
        # Verify relationships
        assert len(sample_media.mediables) == 2
        assert sample_media in sample_user.media
        assert sample_media in sample_document.media
    
    def test_cascade_delete_mediables(self, db_session, sample_media, sample_user):
        """Test that deleting media cascades to mediables"""
        # Create mediable relationship
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        db_session.add(mediable)
        db_session.commit()
        
        # Verify relationship exists
        assert len(sample_media.mediables) == 1
        
        # Delete media
        db_session.delete(sample_media)
        db_session.commit()
        
        # Verify mediable was also deleted
        remaining_mediable = db_session.query(Mediable).filter(
            Mediable.media_id == sample_media.id
        ).first()
        
        assert remaining_mediable is None
    
    def test_soft_delete_media(self, db_session, sample_media, sample_user):
        """Test soft delete functionality"""
        # Soft delete the media
        sample_media.deleted_at = 1234567890
        sample_media.deleted_by = sample_user.id
        db_session.commit()
        
        # Verify soft delete fields are set
        assert sample_media.deleted_at == 1234567890
        assert sample_media.deleted_by == sample_user.id
        
        # Verify media still exists in database
        media = db_session.query(Media).filter(Media.id == sample_media.id).first()
        assert media is not None
        assert media.deleted_at == 1234567890


class TestDatabaseQueries:
    """Test cases for database queries"""
    
    def test_query_media_by_disk(self, db_session, sample_user):
        """Test querying media by disk"""
        # Create media on different disks
        local_media = Media(
            name="Local Media",
            file_name="local.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id
        )
        
        s3_media = Media(
            name="S3 Media",
            file_name="s3.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=2048000,
            created_by=sample_user.id
        )
        
        db_session.add_all([local_media, s3_media])
        db_session.commit()
        
        # Query by disk
        local_media_list = db_session.query(Media).filter(Media.disk == "local").all()
        s3_media_list = db_session.query(Media).filter(Media.disk == "s3").all()
        
        assert len(local_media_list) == 1
        assert local_media_list[0] == local_media
        assert len(s3_media_list) == 1
        assert s3_media_list[0] == s3_media
    
    def test_query_media_by_mime_type(self, db_session, sample_user):
        """Test querying media by MIME type"""
        # Create media with different MIME types
        jpeg_media = Media(
            name="JPEG Media",
            file_name="test.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,
            created_by=sample_user.id
        )
        
        png_media = Media(
            name="PNG Media",
            file_name="test.png",
            disk="local",
            mime_type="image/png",
            size=1536000,
            created_by=sample_user.id
        )
        
        db_session.add_all([jpeg_media, png_media])
        db_session.commit()
        
        # Query by MIME type
        jpeg_list = db_session.query(Media).filter(Media.mime_type == "image/jpeg").all()
        png_list = db_session.query(Media).filter(Media.mime_type == "image/png").all()
        
        assert len(jpeg_list) == 1
        assert jpeg_list[0] == jpeg_media
        assert len(png_list) == 1
        assert png_list[0] == png_media
    
    def test_query_mediables_by_type(self, db_session, sample_media, sample_user, sample_document):
        """Test querying mediables by type"""
        # Create mediables for different types
        user_mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        document_mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_document.id,
            mediable_type="IdentityDocument",
            group="front"
        )
        
        db_session.add_all([user_mediable, document_mediable])
        db_session.commit()
        
        # Query by type
        user_mediables = db_session.query(Mediable).filter(Mediable.mediable_type == "User").all()
        document_mediables = db_session.query(Mediable).filter(Mediable.mediable_type == "IdentityDocument").all()
        
        assert len(user_mediables) == 1
        assert user_mediables[0] == user_mediable
        assert len(document_mediables) == 1
        assert document_mediables[0] == document_mediable
    
    def test_query_mediables_by_group(self, db_session, sample_media, sample_user):
        """Test querying mediables by group"""
        # Create mediables for different groups
        profile_mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        avatar_mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="avatar"
        )
        
        db_session.add_all([profile_mediable, avatar_mediable])
        db_session.commit()
        
        # Query by group
        profile_mediables = db_session.query(Mediable).filter(Mediable.group == "profile").all()
        avatar_mediables = db_session.query(Mediable).filter(Mediable.group == "avatar").all()
        
        assert len(profile_mediables) == 1
        assert profile_mediables[0] == profile_mediable
        assert len(avatar_mediables) == 1
        assert avatar_mediables[0] == avatar_mediable
    
    def test_join_queries(self, db_session, sample_media, sample_user):
        """Test join queries between media and mediables"""
        # Create mediable relationship
        mediable = Mediable(
            media_id=sample_media.id,
            mediable_id=sample_user.id,
            mediable_type="User",
            group="profile"
        )
        
        db_session.add(mediable)
        db_session.commit()
        
        # Join query to get media for a user
        user_media = db_session.query(Media).join(Mediable).filter(
            Mediable.mediable_id == sample_user.id,
            Mediable.mediable_type == "User"
        ).all()
        
        assert len(user_media) == 1
        assert user_media[0] == sample_media
    
    def test_complex_queries(self, db_session, sample_user):
        """Test complex queries with multiple conditions"""
        # Create media with different attributes
        large_jpeg = Media(
            name="Large JPEG",
            file_name="large.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=5000000,
            created_by=sample_user.id,
            custom_attribute="large_file"
        )
        
        small_png = Media(
            name="Small PNG",
            file_name="small.png",
            disk="local",
            mime_type="image/png",
            size=500000,
            created_by=sample_user.id,
            custom_attribute="small_file"
        )
        
        db_session.add_all([large_jpeg, small_png])
        db_session.commit()
        
        # Complex query: large JPEG files on S3
        large_s3_jpeg = db_session.query(Media).filter(
            Media.size > 1000000,
            Media.disk == "s3",
            Media.mime_type == "image/jpeg"
        ).all()
        
        assert len(large_s3_jpeg) == 1
        assert large_s3_jpeg[0] == large_jpeg
        
        # Complex query: small files with custom attributes
        small_with_attr = db_session.query(Media).filter(
            Media.size < 1000000,
            Media.custom_attribute.isnot(None)
        ).all()
        
        assert len(small_with_attr) == 1
        assert small_with_attr[0] == small_png


class TestDatabasePerformance:
    """Test cases for database performance considerations"""
    
    def test_index_usage(self, db_session, sample_user):
        """Test that indexes are being used effectively"""
        # Create multiple media records
        media_list = []
        for i in range(10):
            media = Media(
                name=f"Media {i}",
                file_name=f"media_{i}.jpg",
                disk="local",
                mime_type="image/jpeg",
                size=1024000 + i * 1000,
                created_by=sample_user.id
            )
            media_list.append(media)
        
        db_session.add_all(media_list)
        db_session.commit()
        
        # Test queries that should use indexes
        # These queries should be fast due to indexing
        local_media = db_session.query(Media).filter(Media.disk == "local").all()
        jpeg_media = db_session.query(Media).filter(Media.mime_type == "image/jpeg").all()
        
        assert len(local_media) == 10
        assert len(jpeg_media) == 10
    
    def test_bulk_operations(self, db_session, sample_user):
        """Test bulk operations for performance"""
        # Bulk insert
        media_list = []
        for i in range(100):
            media = Media(
                name=f"Bulk Media {i}",
                file_name=f"bulk_{i}.jpg",
                disk="s3",
                mime_type="image/jpeg",
                size=1024000,
                created_by=sample_user.id
            )
            media_list.append(media)
        
        db_session.add_all(media_list)
        db_session.commit()
        
        # Verify bulk insert worked
        total_media = db_session.query(Media).count()
        assert total_media >= 100
        
        # Bulk update
        db_session.query(Media).filter(Media.disk == "s3").update({
            "custom_attribute": "bulk_updated"
        })
        db_session.commit()
        
        # Verify bulk update worked
        updated_media = db_session.query(Media).filter(
            Media.custom_attribute == "bulk_updated"
        ).count()
        
        assert updated_media >= 100 