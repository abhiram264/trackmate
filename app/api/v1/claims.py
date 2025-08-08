from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.claim import Claim
from app.models.found_item import FoundItem
from app.models.user import User
from app.schemas.claim import (
    ClaimCreate, ClaimResponse, ClaimApproval, ClaimRejection, PaginatedClaims
)
from app.schemas.base_schema import MessageResponse
from app.database import get_db
from app.api.deps import get_current_active_user, get_admin_user

router = APIRouter()

@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new claim for a found item"""

    found_item = db.query(FoundItem).filter(FoundItem.id == claim_data.found_item_id).first()
    if not found_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Found item not found")

    if found_item.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot claim your own item")

    existing = db.query(Claim).filter(
        Claim.found_item_id == claim_data.found_item_id,
        Claim.user_id == current_user.id,
        Claim.status.in_(["pending", "approved"]),
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already claimed this item")

    now = datetime.utcnow()
    new_claim = Claim(
        found_item_id=claim_data.found_item_id,
        user_id=current_user.id,
        claim_reason=claim_data.claim_reason,
        contact_info=claim_data.contact_info,
        additional_proof=claim_data.additional_proof,
        status="pending",
        created_at=now,
        updated_at=now,
    )

    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim


@router.get("/", response_model=PaginatedClaims)
async def get_claims(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all claims (admin only)"""
    query = db.query(Claim)
    if status:
        query = query.filter(Claim.status == status)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = (total + limit - 1) // limit
    return PaginatedClaims(claims=items, total=total, page=page, per_page=limit, pages=pages)


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get specific claim details"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
    if claim.user_id != current_user.id and current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return claim


@router.put("/{claim_id}/approve", response_model=ClaimResponse)
async def approve_claim(
    claim_id: int,
    approval_data: ClaimApproval,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Approve a pending claim (admin only)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
    if claim.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending claims can be approved")

    now = datetime.utcnow()
    claim.status = "approved"
    claim.verified_by = current_user.id
    claim.verification_notes = approval_data.approval_notes
    claim.updated_at = now

    item = db.query(FoundItem).filter(FoundItem.id == claim.found_item_id).first()
    if item:
        item.status = "claimed"
        item.updated_at = now

    db.commit()
    db.refresh(claim)
    return claim


@router.put("/{claim_id}/reject", response_model=ClaimResponse)
async def reject_claim(
    claim_id: int,
    rejection_data: ClaimRejection,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Reject a pending claim (admin only)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
    if claim.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending claims can be rejected")

    claim.status = "rejected"
    claim.verified_by = current_user.id
    claim.rejection_reason = rejection_data.rejection_reason
    claim.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(claim)
    return claim


@router.get("/my-claims/", response_model=PaginatedClaims)
async def get_my_claims(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current user’s claims"""
    query = db.query(Claim).filter(Claim.user_id == current_user.id)
    if status:
        query = query.filter(Claim.status == status)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = (total + limit - 1) // limit
    return PaginatedClaims(claims=items, total=total, page=page, per_page=limit, pages=pages)


@router.delete("/{claim_id}", response_model=MessageResponse)
async def cancel_claim(
    claim_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cancel a pending claim (owner or admin)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
    if claim.user_id != current_user.id and current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if claim.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending claims can be cancelled")

    db.delete(claim)
    db.commit()
    return MessageResponse(message="Claim cancelled successfully", success=True)
