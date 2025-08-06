"""
API v1 endpoints for TrackMate
Contains all version 1 API routes and routers
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .lost_items import router as lost_items_router
from .found_items import router as found_items_router
from .claims import router as claims_router
from .images import router as images_router

# Create main v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(lost_items_router, prefix="/lost-items", tags=["Lost Items"])
api_router.include_router(found_items_router, prefix="/found-items", tags=["Found Items"])
api_router.include_router(claims_router, prefix="/claims", tags=["Claims"])
api_router.include_router(images_router, prefix="/images", tags=["Images"])

# Export routers for individual use if needed
__all__ = [
    "api_router",
    "auth_router",
    "lost_items_router", 
    "found_items_router",
    "claims_router",
    "images_router"
]
