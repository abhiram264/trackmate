from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ImageUpload(BaseModel):
    """Schema for uploading images via form-data"""
    item_id: int
    item_type: str  # 'lost' or 'found'


class ImageResponse(BaseModel):
    """Schema for image response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    item_id: int
    item_type: str
    uploaded_by: int
    created_at: datetime


class ImageSearchRequest(BaseModel):
    """Schema for image similarity search"""
    threshold: Optional[float] = 0.7
    limit: Optional[int] = 10


class ImageSearchResult(BaseModel):
    """Schema for image search results"""
    image_id: int
    item_id: int
    item_type: str
    similarity_score: float
    image_url: str


class SimilarImagesResponse(BaseModel):
    """Schema for similar images response"""
    results: list[ImageSearchResult]
    total_found: int
    search_time_ms: float
