"""
Pydantic schemas for API request/response validation
"""

# User schemas
from .user import (
    UserSignup,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest
)

# Lost item schemas
from .lost_item import (
    LostItemCreate,
    LostItemUpdate,
    LostItemResponse,
    LostItemPublic,
    PaginatedLostItems
)

# Found item schemas
from .found_item import (
    FoundItemCreate,
    FoundItemUpdate,
    FoundItemResponse,
    FoundItemPublic,
    PaginatedFoundItems
)

# Claim schemas
from .claim import (
    ClaimCreate,
    ClaimUpdate,
    ClaimResponse,
    ClaimApproval,
    ClaimRejection,
    PaginatedClaims
)

# Image schemas
from .image_schema import (
    ImageUpload,
    ImageResponse,
    ImageSearchRequest,
    ImageSearchResult,
    SimilarImagesResponse
)

# Base schemas
from .base_schema import (
    MessageResponse,
    ErrorResponse,
    PaginationParams,
    SearchParams
)

__all__ = [
    # User schemas
    "UserSignup",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "RefreshTokenRequest",

    # Lost item schemas
    "LostItemCreate",
    "LostItemUpdate",
    "LostItemResponse",
    "LostItemPublic", 
    "PaginatedLostItems",

    # Found item schemas
    "FoundItemCreate",
    "FoundItemUpdate",
    "FoundItemResponse",
    "FoundItemPublic",
    "PaginatedFoundItems",

    # Claim schemas
    "ClaimCreate",
    "ClaimUpdate",
    "ClaimResponse",
    "ClaimApproval",
    "ClaimRejection",
    "PaginatedClaims",

    # Image schemas
    "ImageUpload",
    "ImageResponse",
    "ImageSearchRequest",
    "ImageSearchResult",
    "SimilarImagesResponse",

    # Base schemas
    "MessageResponse",
    "ErrorResponse", 
    "PaginationParams",
    "SearchParams",
]

