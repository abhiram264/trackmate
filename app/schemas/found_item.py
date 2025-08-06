from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

# Add the enums (if not importing from models)
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

class FoundItemCreate(BaseModel):
    """Schema for creating found items"""
    title: str
    description: str
    category: ItemCategory
    location_found: str
    date_found: datetime
    current_location: Optional[str] = None
    handover_instructions: Optional[str] = None

class FoundItemUpdate(BaseModel):
    """Schema for updating found items"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ItemCategory] = None
    location_found: Optional[str] = None
    date_found: Optional[datetime] = None
    current_location: Optional[str] = None
    handover_instructions: Optional[str] = None
    status: Optional[ItemStatus] = None

class FoundItemResponse(BaseModel):
    """Schema for found item response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    category: ItemCategory
    location_found: str
    date_found: datetime
    status: ItemStatus
    current_location: Optional[str] = None
    handover_instructions: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

class FoundItemPublic(BaseModel):
    """Schema for public found item view"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    category: ItemCategory
    location_found: str
    date_found: datetime
    status: ItemStatus
    handover_instructions: Optional[str] = None
    created_at: datetime

class PaginatedFoundItems(BaseModel):
    """Schema for paginated found items response"""
    items: list[FoundItemResponse]
    total: int
    page: int
    per_page: int
    pages: int
