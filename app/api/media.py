from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.rules.validation_file_size_type import validate_file_size_type  # type: ignore
from app.services.s3_service import S3Service
from app.utils.ocr import read_image  # type: ignore
from app.utils.media_utils import MediaManager
from app.schemas.extraction_result import ExtractionResult  # type: ignore
from app.core.database_session import get_db
import tempfile
import os

router = APIRouter()
s3_service = S3Service()

@router.post("/upload-identity-document/", response_model=ExtractionResult)
async def upload_identity_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate and read file content
    content = await validate_file_size_type(file)
    if not content:
        raise HTTPException(status_code=400, detail="Invalid file or empty content.")

    # Ensure filename and content_type are not None
    filename = file.filename if file.filename is not None else ""
    content_type = file.content_type if file.content_type is not None else ""

    # Upload to S3/MinIO
    try:
        upload_result = s3_service.upload_file(
            file_content=content,
            file_name=filename,
            content_type=content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

    # Save media metadata to DB
    try:
        media = MediaManager.create_media(
            db=db,
            name=upload_result['original_filename'],
            file_name=upload_result['key'],
            disk="s3",
            mime_type=upload_result['content_type'],
            size=upload_result['size'],
            hash=upload_result['hash'],
            custom_attribute="uploaded_via_api"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save media metadata: {str(e)}")

    # Download from S3 to temp file for OCR
    try:
        # type: ignore for os.path.splitext if needed
        _, ext = os.path.splitext(str(filename))  # type: ignore
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            s3_file_content = s3_service.download_file(upload_result['key'])
            temp_file.write(s3_file_content)
            temp_file_path = temp_file.name
        ocr = read_image(temp_file_path)
        extracted_text = ocr.output()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

    return ExtractionResult(
        filename=filename,
        content_type=content_type,
        s3_url=upload_result['url'],
        media_id=str(media.id),
        result=extracted_text
    )