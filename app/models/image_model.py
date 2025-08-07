"""
Enhanced Image model with CLIP embedding support
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum

class ImageType(str, Enum):
    LOST_ITEM = "lost_item"
    FOUND_ITEM = "found_item"
    REFERENCE = "reference"  # Stock photos for comparison

class ImageStatus(str, Enum):
    ACTIVE = "active"
    PROCESSING = "processing"  # Embedding generation in progress
    PROCESSED = "processed"
    FAILED = "failed"

class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Basic image info
    filename: str = Field(nullable=False)
    original_filename: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    mime_type: str = Field(nullable=False)

    # Item association
    item_type: ImageType = Field(nullable=False)
    item_id: int = Field(nullable=False)  # References lost_items.id or found_items.id

    # User info
    uploaded_by: int = Field(foreign_key="users.id", nullable=False)

    # CLIP embeddings
    image_embedding: Optional[str] = Field(default=None, max_length=8192)
    embedding_model: Optional[str] = Field(default=None)
    embedding_status: ImageStatus = Field(default=ImageStatus.ACTIVE)

    # Image metadata
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    is_primary: bool = Field(default=False)  # Main image for the item

    # Processing info
    processing_error: Optional[str] = Field(default=None)
    processing_attempts: int = Field(default=0)

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_image_embedding(self) -> Optional[list]:
        """Get image embedding as list"""
        if self.image_embedding:
            import json
            return json.loads(self.image_embedding)
        return None
