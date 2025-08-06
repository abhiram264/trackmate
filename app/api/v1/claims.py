from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

# ✅ CORRECT imports:
from app.models.claim import Claim
from app.models.found_item import FoundItem
from app.models.user import User
from app.schemas.claim import (
    ClaimCreate, ClaimUpdate, ClaimResponse, ClaimApproval, ClaimRejection,
    PaginatedClaims
)
from app.schemas.base_schema import MessageResponse
from app.database import get_db
from app.api.deps import get_current_active_user, get_admin_user

router = APIRouter()


@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new claim for found item"""

    # Check if found item exists and is available
    found_item = db.query(FoundItem).filter(FoundItem.id == claim_data.found_item_id).first()

    if not found_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Found item not found"
        )

    if found_item.status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is not available for claiming"
        )

    # Check if user hasn't already claimed this item
    existing_claim = db.query(Claim).filter(
        Claim.found_item_id == claim_data.found_item_id,
        Claim.user_id == current_user.id,
        Claim.status.in_(["pending", "approved"])
    ).first()

    if existing_claim:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already claimed this item"
        )

    # Prevent users from claiming their own found items
    if found_item.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot claim your own found item"
        )

    new_claim = Claim(
        found_item_id=claim_data.found_item_id,
        user_id=current_user.id,
        claim_reason=claim_data.claim_reason,
        contact_info=claim_data.contact_info,
        additional_proof=claim_data.additional_proof
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
    item_type: Optional[str] = Query(None),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: Session = Depends(get_db)
):
    """List all claims (admin/staff only)"""

    query = db.query(Claim)

    if status:
        query = query.filter(Claim.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    claims = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedClaims(
        claims=claims,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific claim details"""

    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    # Check if user owns the claim or is admin/staff
    if (claim.user_id != current_user.id and 
        current_user.role not in ["admin", "staff"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this claim"
        )

    return claim


@router.put("/{claim_id}/approve", response_model=ClaimResponse)
async def approve_claim(
    claim_id: int,
    approval_data: ClaimApproval,
    current_user: User = Depends(get_admin_user),  # Admin/Staff only
    db: Session = Depends(get_db)
):
    """Approve claim (admin/staff only)"""

    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    if claim.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending claims can be approved"
        )

    # Update claim
    claim.status = "approved"
    claim.verified_by = current_user.id
    claim.verification_notes = approval_data.approval_notes
    claim.updated_at = datetime.utcnow()

    # Update found item status
    found_item = db.query(FoundItem).filter(FoundItem.id == claim.found_item_id).first()
    if found_item:
        found_item.status = "claimed"
        found_item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(claim)

    return claim


@router.put("/{claim_id}/reject", response_model=ClaimResponse)
async def reject_claim(
    claim_id: int,
    rejection_data: ClaimRejection,
    current_user: User = Depends(get_admin_user),  # Admin/Staff only
    db: Session = Depends(get_db)
):
    """Reject claim (admin/staff only)"""

    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    if claim.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending claims can be rejected"
        )

    # Update claim
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
    db: Session = Depends(get_db)
):
    """Get current user's claims"""

    query = db.query(Claim).filter(Claim.user_id == current_user.id)

    if status:
        query = query.filter(Claim.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    claims = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedClaims(
        claims=claims,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.delete("/{claim_id}", response_model=MessageResponse)
async def cancel_claim(
    claim_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel claim (claimant only, and only if pending)"""

    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    # Check ownership
    if claim.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this claim"
        )

    if claim.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending claims can be cancelled"
        )

    db.delete(claim)
    db.commit()

    return MessageResponse(message="Claim cancelled successfully", success=True)


@router.get("/pending/", response_model=PaginatedClaims)
async def get_pending_claims(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_admin_user),  # Admin/Staff only
    db: Session = Depends(get_db)
):
    """Get all pending claims for review (admin/staff only)"""

    query = db.query(Claim).filter(Claim.status == "pending")

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    claims = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedClaims(
        claims=claims,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.patch("/{claim_id}/complete", response_model=ClaimResponse)
async def complete_claim(
    claim_id: int,
    current_user: User = Depends(get_admin_user),  # Admin/Staff only
    db: Session = Depends(get_db)
):
    """Mark claim as completed after handover (admin/staff only)"""

    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    if claim.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved claims can be completed"
        )

    # Update claim and found item
    claim.status = "completed"
    claim.updated_at = datetime.utcnow()

    found_item = db.query(FoundItem).filter(FoundItem.id == claim.found_item_id).first()
    if found_item:
        found_item.status = "resolved"
        found_item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(claim)

    return claim
