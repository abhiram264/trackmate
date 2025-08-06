from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum

# Add these enums to your lost_item.py file
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

# Your existing LostItem model (update it to use the enums)
class LostItem(SQLModel, table=True):
    __tablename__ = "lost_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=100)
    description: str = Field(nullable=False, max_length=1000)
    category: ItemCategory = Field(nullable=False)  # Use the enum
    location_lost: str = Field(nullable=False)
    date_lost: datetime = Field(nullable=False)
    status: ItemStatus = Field(default=ItemStatus.ACTIVE)  # Use the enum
    
    # Optional fields
    contact_info: Optional[str] = Field(default=None)
    reward_offered: Optional[str] = Field(default=None)
    
    # Foreign key
    user_id: int = Field(foreign_key="users.id", nullable=False)
    
    # AI matching field
    description_embedding: Optional[str] = Field(default=None)
    
    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
