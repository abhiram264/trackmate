from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

# Add the enums
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

class LostItemCreate(BaseModel):
    """Schema for creating lost items"""
    title: str
    description: str
    category: ItemCategory
    location_lost: str
    date_lost: datetime
    contact_info: Optional[str] = None
    reward_offered: Optional[str] = None

class LostItemUpdate(BaseModel):
    """Schema for updating lost items"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ItemCategory] = None
    location_lost: Optional[str] = None
    date_lost: Optional[datetime] = None
    contact_info: Optional[str] = None
    reward_offered: Optional[str] = None
    status: Optional[ItemStatus] = None

class LostItemResponse(BaseModel):
    """Schema for lost item response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    category: ItemCategory
    location_lost: str
    date_lost: datetime
    status: ItemStatus
    contact_info: Optional[str] = None
    reward_offered: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

class LostItemPublic(BaseModel):
    """Schema for public lost item view"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    category: ItemCategory
    location_lost: str
    date_lost: datetime
    status: ItemStatus
    reward_offered: Optional[str] = None
    created_at: datetime

class PaginatedLostItems(BaseModel):
    """Schema for paginated lost items response"""
    items: list[LostItemResponse]
    total: int
    page: int
    per_page: int
    pages: int
