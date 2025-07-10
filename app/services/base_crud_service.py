"""
Base CRUD service for common database operations
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseCRUDService(Generic[ModelType]):
    """Base CRUD service with common operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, db: Session, obj_in: Dict[str, Any], created_by: Optional[UUID] = None) -> ModelType:
        """Create a new record"""
        if created_by:
            obj_in["created_by"] = created_by
        
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: Union[int, UUID]) -> Optional[ModelType]:
        """Get a record by ID"""
        return db.query(self.model).filter(getattr(self.model, 'id') == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering"""
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, (list, tuple)):
                        query = query.filter(getattr(self.model, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def update(
        self, 
        db: Session, 
        id: Union[int, UUID], 
        obj_in: Dict[str, Any], 
        updated_by: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """Update a record"""
        if updated_by:
            obj_in["updated_by"] = updated_by
        
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: Union[int, UUID], deleted_by: Optional[UUID] = None) -> bool:
        """Delete a record (soft delete if deleted_at field exists)"""
        db_obj = self.get(db, id)
        if not db_obj:
            return False
        
        # Check if model supports soft delete
        if hasattr(db_obj, 'deleted_at'):
            # Soft delete
            setattr(db_obj, 'deleted_at', func.now())
            if deleted_by:
                setattr(db_obj, 'deleted_by', deleted_by)
        else:
            # Hard delete
            db.delete(db_obj)
        
        db.commit()
        return True
    
    def search(
        self, 
        db: Session, 
        search_term: str, 
        search_fields: List[str],
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Search records by term across specified fields"""
        query = db.query(self.model)
        
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                search_conditions.append(
                    getattr(self.model, field).ilike(f"%{search_term}%")
                )
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, (list, tuple)):
                        query = query.filter(getattr(self.model, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    def exists(self, db: Session, id: Union[int, UUID]) -> bool:
        """Check if a record exists"""
        return db.query(self.model).filter(getattr(self.model, 'id') == id).first() is not None 