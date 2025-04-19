import hashlib

from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from extract_text_identity import read_image
from rules.validation_file_size_type import validate_file_size_type

app = FastAPI()

# Start debugpy if DEBUG environment variable is set
if os.getenv("DEBUG") == "1":
    import debugpy
    debugpy.listen((os.getenv("DEBUG_IP", "0.0.0.0"), 5678))  # Use IP from environment variable
    print("Debugpy is listening on port 5678. Waiting for debugger to attach...")
    debugpy.wait_for_client()


@app.get("/")
async def root():
    return {"message": "Hello version 1.0"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    content = await validate_file_size_type(file)

    # Compute the hash of the file content
    file_hash = hashlib.sha256(content).hexdigest()
    # Ensure the directory exists
    os.makedirs("storage/images", exist_ok=True)
    # Generate a sluggable file name
    original_name, ext = os.path.splitext(file.filename)
    sluggable_name = f"{file_hash}{ext}"
    file_path = f"storage/images/{sluggable_name}"

    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text from the saved image
    try:
        ocr = read_image(file_path)
        extracted_text = ocr.output()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "path": file_path,
        "result": extracted_text
    }

# Command to run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
