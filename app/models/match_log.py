from typing import Optional
from sqlmodel import SQLModel,Field
from datetime import datetime, timezone

class MatchLog(SQLModel,table = True):
    id: Optional[int] = Field(default = None,primary_key=True)
    lost_item_id : int = Field(foreign_key="lost_items.id")
    found_item_id : int = Field(foreign_key="found_items.id")
    similarity_score : float
    matched_on : datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
