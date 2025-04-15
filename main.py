from fastapi import FastAPI, File, UploadFile, HTTPException
import os

app = FastAPI()

# Start debugpy if DEBUG environment variable is set
if os.getenv("DEBUG") == "1":
    import debugpy
    debugpy.listen((os.getenv("DEBUG_IP", "0.0.0.0"), 5678))  # Use IP from environment variable
    print("Debugpy is listening on port 5678. Waiting for debugger to attach...")
    debugpy.wait_for_client()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    max_size = 2 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

    # Ensure the directory exists
    os.makedirs("storage/images", exist_ok=True)

    # Save the file to the directory
    file_path = f"storage/images/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    return {"filename": file.filename, "content_type": file.content_type, "path": file_path}

# Command to run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 4000))  # Default to 4000 if APP_PORT is not set
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
