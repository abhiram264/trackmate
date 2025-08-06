from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(nullable=False)
    original_filename: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    file_size: int = Field(nullable=False)  # Size in bytes
    content_type: str = Field(nullable=False)  # e.g., 'image/jpeg', 'image/png'

    # For CLIP embeddings - stored as JSON string
    clip_embedding: Optional[str] = Field(default=None)

    # Link to items
    item_id: int = Field(nullable=False)
    item_type: str = Field(nullable=False)  # 'lost' or 'found'

    # User who uploaded
    uploaded_by: int = Field(foreign_key="users.id", nullable=False)

    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
