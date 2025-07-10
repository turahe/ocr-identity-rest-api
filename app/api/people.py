from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.services.people_service import people_service
from app.models.people import People
from app.core.database_session import get_db
from app.schemas.people import PeopleCreate, PeopleUpdate, PeopleRead
from app.api.auth import get_current_user_or_apikey
from app.services.ektp_image_generator import EKTPImageGenerator
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from app.services.s3_service import s3_service
from app.models.media import Media
from app.utils.media_utils import MediaManager

router = APIRouter(prefix="/people", tags=["people"])

@router.post("/", response_model=PeopleRead)
async def create_person(
    person_data: PeopleCreate,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_apikey)
):
    try:
        # Use authenticated user's UUID for created_by_uuid
        from uuid import UUID
        if hasattr(current_user, 'id'):
            created_by_uuid = UUID(str(current_user.id))
        else:
            raise HTTPException(status_code=401, detail="No user UUID available from authentication")
        person = people_service.create_person(db, person_data.dict(), created_by_uuid)
        return person
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{person_id}", response_model=PeopleRead)
async def get_person(person_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user_or_apikey)):
    try:
        from uuid import UUID
        person = people_service.get(db, UUID(person_id))
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[PeopleRead])
async def get_people(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    religion: Optional[str] = None,
    citizenship: Optional[str] = None,
    marital_status: Optional[str] = None,
    nationality: Optional[str] = None,
    ethnicity: Optional[str] = None,
    job: Optional[str] = None,
    blood_type: Optional[str] = None,
    place_of_birth: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_apikey)
):
    try:
        search_data = {}
        if name:
            search_data['name'] = name
        if gender:
            search_data['gender'] = gender
        if religion:
            search_data['religion'] = religion
        if citizenship:
            search_data['citizenship'] = citizenship
        if marital_status:
            search_data['marital_status'] = marital_status
        if nationality:
            search_data['nationality'] = nationality
        if ethnicity:
            search_data['ethnicity'] = ethnicity
        if job:
            search_data['job'] = job
        if blood_type:
            search_data['blood_type'] = blood_type
        if place_of_birth:
            search_data['place_of_birth'] = place_of_birth
        if search_data:
            people = people_service.search_advanced(db, search_data, skip, limit)
        else:
            people = people_service.get_multi(db, skip, limit)
        return people
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{person_id}", response_model=PeopleRead)
async def update_person(
    person_id: str,
    person_data: PeopleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_apikey)
):
    try:
        from uuid import UUID
        if hasattr(current_user, 'id'):
            updated_by_uuid = UUID(str(current_user.id))
        else:
            raise HTTPException(status_code=401, detail="No user UUID available from authentication")
        person = people_service.update_person(db, UUID(person_id), person_data.dict(exclude_unset=True), updated_by_uuid)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{person_id}")
async def delete_person(
    person_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_apikey)
):
    try:
        from uuid import UUID
        if hasattr(current_user, 'id'):
            deleted_by_uuid = UUID(str(current_user.id))
        else:
            raise HTTPException(status_code=401, detail="No user UUID available from authentication")
        success = people_service.delete(db, UUID(person_id), deleted_by_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Person not found")
        return {"status": "success", "message": "Person deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{search_term}", response_model=list[PeopleRead])
async def search_people(
    search_term: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        search_fields = ['full_name', 'citizenship_identity']
        people = people_service.search(db, search_term, search_fields, skip, limit)
        return people
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/citizenship/{citizenship_identity}", response_model=PeopleRead)
async def get_person_by_citizenship_identity(
    citizenship_identity: str,
    db: Session = Depends(get_db),
):
    try:
        person = people_service.get_by_citizenship_identity(db, citizenship_identity)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/")
async def get_people_statistics(db: Session = Depends(get_db)):
    try:
        stats = people_service.get_statistics(db)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ektp-image/{citizenship_identity}")
async def generate_ektp_image(
    citizenship_identity: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_apikey)
):
    person = db.query(People).filter(People.citizenship_identity == citizenship_identity).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    # Prepare data for EKTPImageGenerator (mapping fields as needed)
    data = {
        "province": person.nationality or "-",
        "city": person.ethnicity or "-",
        "nik": person.citizenship_identity,
        "full_name": person.full_name,
        "place_of_birth": person.place_of_birth or "-",
        "birth_date": person.date_of_birth.isoformat() if getattr(person, 'date_of_birth', None) else "-",
        "gender": person.gender,
        "blood_type": person.blood_type or "-",
        "address": "-",  # Add mapping if available
        "rt_rw": "-",     # Add mapping if available
        "village": "-",   # Add mapping if available
        "district": "-",  # Add mapping if available
        "religion": person.religion,
        "marital_status": person.marital_status,
        "occupation": person.job or "-",
        "citizenship": person.citizenship,
        "expiry_date": "SEUMUR HIDUP",  # or map if available
        "issue_date": person.created_at.strftime('%d-%m-%Y') if getattr(person, 'created_at', None) else "-",
        "photo_path": ""  # Provide a valid photo path or base64 if available
    }
    generator = EKTPImageGenerator()
    template = generator._get_template_path()
    image = Image.open(template)
    draw = ImageDraw.Draw(image)
    generator.draw_text_elements(draw, data)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # Upload to S3 using bytes
    buffer.seek(0)
    file_bytes = buffer.getvalue()
    s3_result = s3_service.upload_file(file_bytes, f"ektp_{person.citizenship_identity}.png", content_type="image/png")
    s3_key = s3_result['key']
    s3_url = s3_result['url']
    # Save metadata to media table
    media = MediaManager.create_media(
        db=db,
        name=f"eKTP {person.full_name}",
        file_name=s3_key,
        disk="s3",
        mime_type="image/png",
        size=len(file_bytes),
        created_by=str(current_user.id) if hasattr(current_user, 'id') else None,
        hash=s3_result.get('hash'),
        custom_attribute="ektp"
    )
    return {
        "s3_url": s3_url,
        "base64_image": img_base64,
        "media_id": str(media.id)
    } 