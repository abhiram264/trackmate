"""
Database models for TrackMate system

This module centralizes all ORM model classes and related enums:
- User and role definitions
- Student registry lookup
- Lost and found items with status/category enums
- Claims, match logs, images
- AI-powered similarity matches
"""

from .user import User, UserRole
from .student_registry import StudentRegistry
from .lost_item import LostItem, ItemCategory, ItemStatus
from .found_item import FoundItem
from .claim import Claim
from .match_log import MatchLog
from .image_model import Image
from .similarity_match import SimilarityMatch, MatchType, MatchStatus

__version__ = "1.0.0"
__author__ = "TrackMate Development Team"

# Model counts by module
MODEL_COUNTS = {
    "User": 1,
    "StudentRegistry": 1,
    "LostItem": 1,
    "FoundItem": 1,
    "Claim": 1,
    "MatchLog": 1,
    "Image": 1,
    "SimilarityMatch": 1,
}

# Available model names for introspection
__all__ = [
    "User",
    "UserRole",
    "StudentRegistry",
    "LostItem",
    "ItemCategory",
    "ItemStatus",
    "FoundItem",
    "Claim",
    "MatchLog",
    "Image",
    "SimilarityMatch",
    "MatchType",
    "MatchStatus",
]
