from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

# ❌ WRONG imports (causing the error):
# from models import LostItem, User
# from schemas import (...)

# ✅ CORRECT imports for your project structure:
from app.models.lost_item import LostItem
from app.models.user import User
from app.schemas.lost_item import (
    LostItemCreate, LostItemUpdate, LostItemResponse, LostItemPublic,
    PaginatedLostItems
)
from app.schemas.base_schema import MessageResponse
from app.database import get_db
from app.api.deps import get_current_active_user, get_admin_user

router = APIRouter()

@router.post("/", response_model=LostItemResponse, status_code=status.HTTP_201_CREATED)
async def create_lost_item(
    item_data: LostItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new lost item entry"""

    new_item = LostItem(
        title=item_data.title,
        description=item_data.description,
        category=item_data.category,
        location_lost=item_data.location_lost,
        date_lost=item_data.date_lost,
        contact_info=item_data.contact_info,
        reward_offered=item_data.reward_offered,
        user_id=current_user.id
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.get("/", response_model=PaginatedLostItems)
async def get_lost_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all lost items with search and filtering"""

    query = db.query(LostItem)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                LostItem.title.ilike(f"%{search}%"),
                LostItem.description.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(LostItem.category == category)

    if status:
        query = query.filter(LostItem.status == status)

    if location:
        query = query.filter(LostItem.location_lost.ilike(f"%{location}%"))

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(LostItem.date_lost >= from_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use ISO format."
            )

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(LostItem.date_lost <= to_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use ISO format."
            )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedLostItems(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/{item_id}", response_model=LostItemResponse)
async def get_lost_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific lost item details"""

    item = db.query(LostItem).filter(LostItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost item not found"
        )

    return item


@router.put("/{item_id}", response_model=LostItemResponse)
async def update_lost_item(
    item_id: int,
    item_update: LostItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update lost item details (owner only)"""

    item = db.query(LostItem).filter(LostItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost item not found"
        )

    # Check ownership (or admin)
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    # Update fields if provided
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_lost_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete lost item entry (owner only)"""

    item = db.query(LostItem).filter(LostItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost item not found"
        )

    # Check ownership (or admin)
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )

    db.delete(item)
    db.commit()

    return MessageResponse(message="Lost item deleted successfully", success=True)


@router.get("/my-items/", response_model=PaginatedLostItems)
async def get_my_lost_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's lost items"""

    query = db.query(LostItem).filter(LostItem.user_id == current_user.id)

    if status:
        query = query.filter(LostItem.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedLostItems(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.patch("/{item_id}/status", response_model=LostItemResponse)
async def update_lost_item_status(
    item_id: int,
    new_status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update lost item status (owner only)"""

    item = db.query(LostItem).filter(LostItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost item not found"
        )

    # Check ownership (or admin)
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    # Validate status
    valid_statuses = ["active", "claimed", "resolved", "expired"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    item.status = new_status
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)

    return item
