from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum

# Add the same enums here too
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

# Your FoundItem model
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
    
    # AI matching field
    description_embedding: Optional[str] = Field(default=None)
    
    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
