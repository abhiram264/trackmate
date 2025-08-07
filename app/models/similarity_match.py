"""
Model to store AI-generated similarity matches between lost and found items
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum

class MatchType(str, Enum):
    IMAGE_SIMILARITY = "image_similarity"
    TEXT_SIMILARITY = "text_similarity"
    COMBINED_SIMILARITY = "combined_similarity"
    CROSS_MODAL = "cross_modal"  # image-to-text or text-to-image

class MatchStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    CONFIRMED = "confirmed"

class SimilarityMatch(SQLModel, table=True):
    __tablename__ = "similarity_matches"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Item references
    lost_item_id: int = Field(foreign_key="lost_items.id", nullable=False)
    found_item_id: int = Field(foreign_key="found_items.id", nullable=False)

    # Match details
    match_type: MatchType = Field(nullable=False)
    similarity_score: float = Field(nullable=False)  # 0.0 to 1.0
    confidence_level: float = Field(nullable=False)  # Model confidence

    # Match metadata
    embedding_model: str = Field(nullable=False)  # "clip-vit-b-32"
    algorithm_version: str = Field(nullable=False)  # For tracking improvements

    # Additional context
    matching_features: Optional[str] = Field(default=None, max_length=1000)  # What matched
    location_bonus: Optional[float] = Field(default=None)  # Location-based boost
    time_bonus: Optional[float] = Field(default=None)  # Recency boost

    # Review status
    status: MatchStatus = Field(default=MatchStatus.PENDING)
    reviewed_by: Optional[int] = Field(foreign_key="users.id", default=None)
    review_notes: Optional[str] = Field(default=None)

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
