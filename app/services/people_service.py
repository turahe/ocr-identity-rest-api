"""
People CRUD service for managing people records
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .base_crud_service import BaseCRUDService
from app.models.people import People


class PeopleService(BaseCRUDService[People]):
    """People CRUD service with specific operations"""
    
    def __init__(self):
        super().__init__(People)
    
    def create_person(
        self, 
        db: Session, 
        person_data: Dict[str, Any], 
        created_by: Optional[UUID] = None
    ) -> People:
        """Create a new person record"""
        # Convert date string to date object if provided
        if 'date_of_birth' in person_data and person_data['date_of_birth']:
            if isinstance(person_data['date_of_birth'], str):
                person_data['date_of_birth'] = date.fromisoformat(person_data['date_of_birth'])
        
        return self.create(db, person_data, created_by)
    
    def update_person(
        self, 
        db: Session, 
        person_id: UUID, 
        person_data: Dict[str, Any], 
        updated_by: Optional[UUID] = None
    ) -> Optional[People]:
        """Update a person record"""
        # Convert date string to date object if provided
        if 'date_of_birth' in person_data and person_data['date_of_birth']:
            if isinstance(person_data['date_of_birth'], str):
                person_data['date_of_birth'] = date.fromisoformat(person_data['date_of_birth'])
        
        return self.update(db, person_id, person_data, updated_by)
    
    def get_by_citizenship_identity(self, db: Session, citizenship_identity: str) -> Optional[People]:
        """Get person by citizenship identity number"""
        return db.query(People).filter(People.citizenship_identity == citizenship_identity).first()
    
    def search_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Search people by name (full name or partial match)"""
        return db.query(People).filter(
            People.full_name.ilike(f"%{name}%")
        ).offset(skip).limit(limit).all()
    
    def get_by_gender(self, db: Session, gender: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by gender"""
        return db.query(People).filter(People.gender == gender).offset(skip).limit(limit).all()
    
    def get_by_religion(self, db: Session, religion: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by religion"""
        return db.query(People).filter(People.religion == religion).offset(skip).limit(limit).all()
    
    def get_by_citizenship(self, db: Session, citizenship: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by citizenship type"""
        return db.query(People).filter(People.citizenship == citizenship).offset(skip).limit(limit).all()
    
    def get_by_marital_status(self, db: Session, marital_status: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by marital status"""
        return db.query(People).filter(People.marital_status == marital_status).offset(skip).limit(limit).all()
    
    def get_by_age_range(self, db: Session, min_age: int, max_age: int, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by age range"""
        from datetime import date
        today = date.today()
        min_date = date(today.year - max_age, today.month, today.day)
        max_date = date(today.year - min_age, today.month, today.day)
        
        return db.query(People).filter(
            and_(
                People.date_of_birth >= min_date,
                People.date_of_birth <= max_date
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_birth_place(self, db: Session, place_of_birth: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by place of birth"""
        return db.query(People).filter(
            People.place_of_birth.ilike(f"%{place_of_birth}%")
        ).offset(skip).limit(limit).all()
    
    def get_by_nationality(self, db: Session, nationality: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by nationality"""
        return db.query(People).filter(
            People.nationality.ilike(f"%{nationality}%")
        ).offset(skip).limit(limit).all()
    
    def get_by_ethnicity(self, db: Session, ethnicity: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by ethnicity"""
        return db.query(People).filter(
            People.ethnicity.ilike(f"%{ethnicity}%")
        ).offset(skip).limit(limit).all()
    
    def get_by_job(self, db: Session, job: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by job/profession"""
        return db.query(People).filter(
            People.job.ilike(f"%{job}%")
        ).offset(skip).limit(limit).all()
    
    def get_by_blood_type(self, db: Session, blood_type: str, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by blood type"""
        return db.query(People).filter(People.blood_type == blood_type).offset(skip).limit(limit).all()
    
    def get_by_disability_status(self, db: Session, disability_status: int, skip: int = 0, limit: int = 100) -> List[People]:
        """Get people by disability status"""
        return db.query(People).filter(People.disability_status == disability_status).offset(skip).limit(limit).all()
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get people statistics"""
        total_count = db.query(People).count()
        
        # Gender distribution
        gender_stats = db.query(
            People.gender,
            func.count(People.id).label('count')
        ).group_by(People.gender).all()
        
        # Religion distribution
        religion_stats = db.query(
            People.religion,
            func.count(People.id).label('count')
        ).group_by(People.religion).all()
        
        # Citizenship distribution
        citizenship_stats = db.query(
            People.citizenship,
            func.count(People.id).label('count')
        ).group_by(People.citizenship).all()
        
        # Marital status distribution
        marital_stats = db.query(
            People.marital_status,
            func.count(People.id).label('count')
        ).group_by(People.marital_status).all()
        
        return {
            'total_count': total_count,
            'gender_distribution': {stat.gender: stat.count for stat in gender_stats},
            'religion_distribution': {stat.religion: stat.count for stat in religion_stats},
            'citizenship_distribution': {stat.citizenship: stat.count for stat in citizenship_stats},
            'marital_status_distribution': {stat.marital_status: stat.count for stat in marital_stats}
        }
    
    def search_advanced(
        self, 
        db: Session, 
        search_data: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100
    ) -> List[People]:
        """Advanced search with multiple criteria"""
        query = db.query(People)
        
        # Build filters based on search criteria
        filters = []
        
        if 'name' in search_data and search_data['name']:
            filters.append(People.full_name.ilike(f"%{search_data['name']}%"))
        
        if 'citizenship_identity' in search_data and search_data['citizenship_identity']:
            filters.append(People.citizenship_identity.ilike(f"%{search_data['citizenship_identity']}%"))
        
        if 'gender' in search_data and search_data['gender']:
            filters.append(People.gender == search_data['gender'])
        
        if 'religion' in search_data and search_data['religion']:
            filters.append(People.religion == search_data['religion'])
        
        if 'citizenship' in search_data and search_data['citizenship']:
            filters.append(People.citizenship == search_data['citizenship'])
        
        if 'marital_status' in search_data and search_data['marital_status']:
            filters.append(People.marital_status == search_data['marital_status'])
        
        if 'nationality' in search_data and search_data['nationality']:
            filters.append(People.nationality.ilike(f"%{search_data['nationality']}%"))
        
        if 'ethnicity' in search_data and search_data['ethnicity']:
            filters.append(People.ethnicity.ilike(f"%{search_data['ethnicity']}%"))
        
        if 'job' in search_data and search_data['job']:
            filters.append(People.job.ilike(f"%{search_data['job']}%"))
        
        if 'blood_type' in search_data and search_data['blood_type']:
            filters.append(People.blood_type == search_data['blood_type'])
        
        if 'place_of_birth' in search_data and search_data['place_of_birth']:
            filters.append(People.place_of_birth.ilike(f"%{search_data['place_of_birth']}%"))
        
        # Apply filters
        if filters:
            query = query.filter(and_(*filters))
        
        return query.offset(skip).limit(limit).all()


# Create global people service instance
people_service = PeopleService() 