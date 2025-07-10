import os
from fastapi import FastAPI, Request, Response
from app.api.auth import router as auth_router
from app.api.people import router as people_router
from app.api.media import router as media_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(title="OCR Identity REST API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter

def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    return _rate_limit_exceeded_handler(request, exc)  # type: ignore

app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Start debugpy if DEBUG environment variable is set
if os.getenv("DEBUG") == "1":
    import debugpy
    debugpy.listen((os.getenv("DEBUG_IP", "0.0.0.0"), 5678))
    print("Debugpy is listening on port 5678. Waiting for debugger to attach...")
    debugpy.wait_for_client()

app.include_router(auth_router)
app.include_router(people_router)
app.include_router(media_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "s3": "connected"
        }
    }


# Command to run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
