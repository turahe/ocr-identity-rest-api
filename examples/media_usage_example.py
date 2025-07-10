"""
Example usage of polymorphic media relationships

This example demonstrates how to:
1. Create media records
2. Attach media to users and identity documents
3. Query media by different criteria
4. Manage media relationships
"""

import uuid
from sqlalchemy.orm import Session
from app.core.database_session import get_db
from app.models.user import User
from app.models.identity_document import IdentityDocument
from app.models.media import Media
from app.models.mediable import Mediable
from app.utils.media_utils import (
    MediaManager,
    attach_media_to_user,
    attach_media_to_document,
    get_user_media,
    get_document_media
)


def example_media_usage():
    """Example of using polymorphic media relationships"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Create a user
        user = User(
            username="john_doe",
            email="john@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Create an identity document
        document = IdentityDocument(
            user_id=user.id,
            document_type="passport",
            document_number="AB123456",
            issuing_country="USA",
            status="pending"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 3. Create media records
        profile_photo = MediaManager.create_media(
            db=db,
            name="Profile Photo",
            file_name="profile_photo.jpg",
            disk="local",
            mime_type="image/jpeg",
            size=1024000,  # 1MB
            created_by=user.id,
            hash="abc123hash",
            custom_attribute="profile_picture"
        )
        
        passport_front = MediaManager.create_media(
            db=db,
            name="Passport Front",
            file_name="passport_front.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=2048000,  # 2MB
            created_by=user.id,
            hash="def456hash",
            custom_attribute="document_front"
        )
        
        passport_back = MediaManager.create_media(
            db=db,
            name="Passport Back",
            file_name="passport_back.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=1800000,  # 1.8MB
            created_by=user.id,
            hash="ghi789hash",
            custom_attribute="document_back"
        )
        
        # 4. Attach media to user
        attach_media_to_user(db, user, profile_photo, group="profile")
        
        # 5. Attach media to identity document
        attach_media_to_document(db, document, passport_front, group="front")
        attach_media_to_document(db, document, passport_back, group="back")
        
        # 6. Query examples
        
        # Get all user media
        user_media = get_user_media(db, user)
        print(f"User has {len(user_media)} media items")
        
        # Get user media by group
        profile_media = get_user_media(db, user, group="profile")
        print(f"User has {len(profile_media)} profile media items")
        
        # Get document media
        document_media = get_document_media(db, document)
        print(f"Document has {len(document_media)} media items")
        
        # Get document media by group
        front_media = get_document_media(db, document, group="front")
        back_media = get_document_media(db, document, group="back")
        print(f"Document has {len(front_media)} front media and {len(back_media)} back media")
        
        # Get media by MIME type
        jpeg_media = MediaManager.get_media_by_type(db, user, "image/jpeg")
        print(f"User has {len(jpeg_media)} JPEG media items")
        
        # 7. Advanced queries
        
        # Get all media relationships for a media item
        relationships = MediaManager.get_media_relationships(db, profile_photo)
        print(f"Profile photo has {len(relationships)} relationships")
        
        # Get media by type and ID
        user_media_by_id = MediaManager.get_media_by_type_and_id(
            db, "User", str(user.id)
        )
        print(f"Found {len(user_media_by_id)} media for user by ID")
        
        # 8. Detach media
        MediaManager.detach_media_from_model(db, user, profile_photo, group="profile")
        print("Detached profile photo from user")
        
        # 9. Soft delete media
        MediaManager.delete_media(db, passport_back, deleted_by=user.id)
        print("Soft deleted passport back image")
        
        # 10. Create media with parent-child relationship
        original_image = MediaManager.create_media(
            db=db,
            name="Original Image",
            file_name="original.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=5000000,  # 5MB
            created_by=user.id
        )
        
        thumbnail = MediaManager.create_media(
            db=db,
            name="Thumbnail",
            file_name="thumbnail.jpg",
            disk="s3",
            mime_type="image/jpeg",
            size=50000,  # 50KB
            created_by=user.id,
            parent_id=original_image.id
        )
        
        print(f"Created thumbnail with parent: {thumbnail.parent_id}")
        
        # 11. Query with polymorphic relationships
        # Get all media for a model using the model's media property
        user_media_via_property = user.media
        print(f"User media via property: {len(user_media_via_property)} items")
        
        document_media_via_property = document.media
        print(f"Document media via property: {len(document_media_via_property)} items")
        
        # Get media by group using model method
        user_profile_media = user.get_media_by_group("profile")
        print(f"User profile media via method: {len(user_profile_media)} items")
        
        document_front_media = document.get_media_by_group("front")
        print(f"Document front media via method: {len(document_front_media)} items")
        
        print("\n✅ Media usage example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in media usage example: {e}")
        db.rollback()
    finally:
        db.close()


def example_media_queries():
    """Example of various media queries"""
    
    db = next(get_db())
    
    try:
        # 1. Get all media with their relationships
        all_media = db.query(Media).all()
        print(f"Total media items: {len(all_media)}")
        
        for media in all_media:
            relationships = media.polymorphic_relationships
            print(f"Media '{media.name}' has relationships:")
            for rel_type, rels in relationships.items():
                print(f"  - {rel_type}: {len(rels)} relationships")
        
        # 2. Get all mediables with their media
        all_mediables = db.query(Mediable).all()
        print(f"\nTotal mediable relationships: {len(all_mediables)}")
        
        for mediable in all_mediables:
            print(f"Mediable: {mediable.mediable_type} {mediable.mediable_id} -> Media: {mediable.media.name}")
        
        # 3. Get media by disk
        s3_media = db.query(Media).filter(Media.disk == "s3").all()
        local_media = db.query(Media).filter(Media.disk == "local").all()
        print(f"\nS3 media: {len(s3_media)} items")
        print(f"Local media: {len(local_media)} items")
        
        # 4. Get media by size range
        large_media = db.query(Media).filter(Media.size > 1000000).all()  # > 1MB
        print(f"Large media (>1MB): {len(large_media)} items")
        
        # 5. Get media by MIME type
        image_media = db.query(Media).filter(Media.mime_type.like("image/%")).all()
        print(f"Image media: {len(image_media)} items")
        
        # 6. Get media with custom attributes
        profile_media = db.query(Media).filter(Media.custom_attribute == "profile_picture").all()
        document_media = db.query(Media).filter(Media.custom_attribute.like("document_%")).all()
        print(f"Profile media: {len(profile_media)} items")
        print(f"Document media: {len(document_media)} items")
        
        print("\n✅ Media queries example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in media queries example: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Running Media Usage Examples")
    print("=" * 50)
    
    example_media_usage()
    print("\n" + "=" * 50)
    example_media_queries() 