from fastapi import HTTPException, status, UploadFile


async def validate_file_size_type(file: UploadFile):
    """
    Validate the file size and type.
    Args:
        file:

    Returns:

    """
    file_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > file_size:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )
    return content