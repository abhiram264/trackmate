from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core import settings, verify_token
from app.api.v1 import auth, lost_items, found_items, claims, images, clip

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(lost_items.router, prefix="/api/v1/lost-items", tags=["Lost Items"])
app.include_router(found_items.router, prefix="/api/v1/found-items", tags=["Found Items"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])
app.include_router(images.router, prefix="/api/v1/images", tags=["Images"])
app.include_router(clip.router, prefix="/api/v1/clip", tags=["AI Matching"])

@app.get("/")
async def root():
    return {
        "message": "🚀 TrackMate API is running!",
        "version": settings.app_version,
        "docs": "/docs",
        "environment": settings.environment,
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug,
    }

@app.on_event("startup")
async def startup_event():
    from app.database import init_db
    init_db()
    print("🚀 TrackMate API started successfully!")
    print("📚 API Documentation: http://localhost:8000/docs")
    print(f"🔧 Environment: {settings.environment}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
    )
