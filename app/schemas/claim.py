from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ClaimCreate(BaseModel):
    """Schema for creating claims"""
    found_item_id: int
    claim_reason: str
    contact_info: str
    additional_proof: Optional[str] = None

class ClaimUpdate(BaseModel):
    """Schema for updating claims (admin only)"""
    status: Optional[str] = None
    verification_notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class ClaimResponse(BaseModel):
    """Schema for claim response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    found_item_id: int
    claim_reason: str
    contact_info: str
    additional_proof: Optional[str] = None
    status: str
    verified_by: Optional[int] = None
    verification_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ClaimApproval(BaseModel):
    """Schema for claim approval"""
    approval_notes: Optional[str] = None

class ClaimRejection(BaseModel):
    """Schema for claim rejection"""
    rejection_reason: str

class PaginatedClaims(BaseModel):
    """Schema for paginated claims response"""
    claims: list[ClaimResponse]
    total: int
    page: int
    per_page: int
    pages: int
