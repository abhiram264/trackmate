from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

class Claim(SQLModel,table = True):
    id: Optional[int] = Field(default = None,primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    found_item_id : int = Field(foreign_key="found_item.id")
    claim_reason: str
    status: str = Field(default = "pending")
    verified_by: Optional[int] = Field(default = None,foreign_key="users.id")
    created_at: datetime = Field(default_factory = lambda:datetime.now(timezone.utc))

