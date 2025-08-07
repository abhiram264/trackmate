"""
Updated Found Item model with embedding fields for CLIP integration
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum

# Define the enums in this file
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

class FoundItem(SQLModel, table=True):
    __tablename__ = "found_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=100)
    description: str = Field(nullable=False, max_length=1000)
    category: ItemCategory = Field(nullable=False)
    location_found: str = Field(nullable=False)
    date_found: datetime = Field(nullable=False)
    status: ItemStatus = Field(default=ItemStatus.ACTIVE)

    # Where item is currently kept
    current_location: Optional[str] = Field(default=None)
    handover_instructions: Optional[str] = Field(default=None)

    # Foreign key
    user_id: int = Field(foreign_key="users.id", nullable=False)

    # AI/ML fields - Updated for CLIP integration
    description_embedding: Optional[str] = Field(default=None, max_length=8192)
    image_embedding: Optional[str] = Field(default=None, max_length=8192)
    combined_embedding: Optional[str] = Field(default=None, max_length=8192)

    # Metadata
    embedding_model: Optional[str] = Field(default=None)
    embedding_version: Optional[str] = Field(default=None)
    has_images: bool = Field(default=False)

    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Helper methods
    def get_description_embedding(self) -> Optional[list]:
        if self.description_embedding:
            import json
            return json.loads(self.description_embedding)
        return None

    def get_combined_embedding(self) -> Optional[list]:
        if self.combined_embedding:
            import json
            return json.loads(self.combined_embedding)
        return None
