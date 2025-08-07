"""
Updated Lost Item model with embedding fields for CLIP integration
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, JSON

class ItemCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    ACCESSORIES = "accessories"
    BOOKS = "books"
    DOCUMENTS = "documents"
    SPORTS = "sports"
    BAGS = "bags"
    JEWELRY = "jewelry"
    KEYS = "keys"
    OTHERS = "others"

class ItemStatus(str, Enum):
    ACTIVE = "active"
    CLAIMED = "claimed"
    RESOLVED = "resolved"
    EXPIRED = "expired"

class LostItem(SQLModel, table=True):
    __tablename__ = "lost_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=100)
    description: str = Field(nullable=False, max_length=1000)
    category: ItemCategory = Field(nullable=False)
    location_lost: str = Field(nullable=False)
    date_lost: datetime = Field(nullable=False)
    status: ItemStatus = Field(default=ItemStatus.ACTIVE)

    # Optional fields
    contact_info: Optional[str] = Field(default=None)
    reward_offered: Optional[str] = Field(default=None)

    # Foreign key
    user_id: int = Field(foreign_key="users.id", nullable=False)

    # AI/ML fields - Updated for CLIP integration
    description_embedding: Optional[str] = Field(default=None, max_length=8192)  # JSON string of vector
    image_embedding: Optional[str] = Field(default=None, max_length=8192)  # JSON string of vector
    combined_embedding: Optional[str] = Field(default=None, max_length=8192)  # Combined vector

    # Metadata for embeddings
    embedding_model: Optional[str] = Field(default=None)  # "clip-vit-b-32"
    embedding_version: Optional[str] = Field(default=None)  # Version tracking
    has_images: bool = Field(default=False)  # Whether item has associated images

    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Add method to get embedding as list
    def get_description_embedding(self) -> Optional[list]:
        """Convert JSON string embedding back to list"""
        if self.description_embedding:
            import json
            return json.loads(self.description_embedding)
        return None

    def get_combined_embedding(self) -> Optional[list]:
        """Get combined embedding as list"""
        if self.combined_embedding:
            import json
            return json.loads(self.combined_embedding)
        return None
