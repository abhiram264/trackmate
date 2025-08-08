from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Claim(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    found_item_id: int = Field(foreign_key="found_items.id", nullable=False)
    claim_reason: str
    contact_info: str
    additional_proof: Optional[str] = None
    status: str = Field(default="pending")
    verified_by: Optional[int] = Field(default=None, foreign_key="users.id")
    verification_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
