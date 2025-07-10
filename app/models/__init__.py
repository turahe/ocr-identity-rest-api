# Models package
from .base import Base
from .user import User
from .identity_document import IdentityDocument
from .ocr_job import OCRJob
from .audit_log import AuditLog
from .media import Media
from .mediable import Mediable

# Import all models to ensure they are registered
__all__ = [
    "Base",
    "User", 
    "IdentityDocument",
    "OCRJob",
    "AuditLog",
    "Media",
    "Mediable"
]

# Create metadata for Alembic
metadata = Base.metadata 