"""
Pydantic schemas for API request/response validation

This module aggregates all request and response schemas used throughout the TrackMate API:
- Authentication and user management
- Lost and found items
- Claims workflow
- Image handling
- AI/CLIP similarity matching
"""

# User schemas
from .user import (
    UserSignup,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)

# Lost item schemas
from .lost_item import (
    LostItemCreate,
    LostItemUpdate,
    LostItemResponse,
    LostItemPublic,
    PaginatedLostItems,
)

# Found item schemas
from .found_item import (
    FoundItemCreate,
    FoundItemUpdate,
    FoundItemResponse,
    FoundItemPublic,
    PaginatedFoundItems,
)

# Claim schemas
from .claim import (
    ClaimCreate,
    ClaimUpdate,
    ClaimResponse,
    ClaimApproval,
    ClaimRejection,
    PaginatedClaims,
)

# Image schemas
from .image_schema import (
    ImageUpload,
    ImageResponse,
    ImageSearchRequest,
    ImageSearchResult,
    SimilarImagesResponse,
)

# Base schemas
from .base_schema import (
    MessageResponse,
    ErrorResponse,
    PaginationParams,
    SearchParams,
)

# CLIP AI schemas
from .clip_schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
    SimilarityRequest,
    SimilarityResult,
    SimilarityResponse,
    TextSearchRequest,
    ImageSearchRequest as ClipImageSearchRequest,
    MatchReviewRequest,
    MatchReviewResponse,
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    EmbeddingStatsResponse,
)

__version__ = "1.0.0"
__author__ = "TrackMate Development Team"

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

    # CLIP AI schemas
    "EmbeddingRequest",
    "EmbeddingResponse",
    "SimilarityRequest",
    "SimilarityResult",
    "SimilarityResponse",
    "TextSearchRequest",
    "ClipImageSearchRequest",
    "MatchReviewRequest",
    "MatchReviewResponse",
    "BatchEmbeddingRequest",
    "BatchEmbeddingResponse",
    "EmbeddingStatsResponse",
]
