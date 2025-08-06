from pydantic import BaseModel
from typing import Optional

class MessageResponse(BaseModel):
    """Standard message response schema"""
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str
    detail: Optional[str] = None
    success: bool = False

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = 1
    limit: int = 20
    
class SearchParams(BaseModel):
    """Standard search parameters"""
    search: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    location: Optional[str] = None
