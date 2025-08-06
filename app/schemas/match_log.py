from pydantic import BaseModel
from datetime import datetime

class MatchLogCreate(BaseModel):
    lost_item_id: int
    fount_item_id: int
    similarity_score: float

class MatchLogRead(MatchLogCreate):
    id: int
    matched_on: datetime

    class Config:
        orm_mode = True
        