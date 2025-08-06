from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

# ✅ CORRECT imports:
from app.models.found_item import FoundItem
from app.models.user import User
from app.schemas.found_item import (
    FoundItemCreate, FoundItemUpdate, FoundItemResponse, FoundItemPublic,
    PaginatedFoundItems
)
from app.schemas.base_schema import MessageResponse
from app.database import get_db
from app.api.deps import get_current_active_user, get_admin_user

router = APIRouter()
@router.post("/", response_model=FoundItemResponse, status_code=status.HTTP_201_CREATED)
async def create_found_item(
    item_data: FoundItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new found item entry"""

    new_item = FoundItem(
        title=item_data.title,
        description=item_data.description,
        category=item_data.category,
        location_found=item_data.location_found,
        date_found=item_data.date_found,
        current_location=item_data.current_location,
        handover_instructions=item_data.handover_instructions,
        user_id=current_user.id
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.get("/", response_model=PaginatedFoundItems)
async def get_found_items(
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
    """List all found items with search and filtering"""

    query = db.query(FoundItem)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                FoundItem.title.ilike(f"%{search}%"),
                FoundItem.description.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(FoundItem.category == category)

    if status:
        query = query.filter(FoundItem.status == status)

    if location:
        query = query.filter(
            or_(
                FoundItem.location_found.ilike(f"%{location}%"),
                FoundItem.current_location.ilike(f"%{location}%")
            )
        )

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(FoundItem.date_found >= from_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use ISO format."
            )

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(FoundItem.date_found <= to_date)
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

    return PaginatedFoundItems(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/{item_id}", response_model=FoundItemResponse)
async def get_found_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific found item details"""

    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Found item not found"
        )

    return item


@router.put("/{item_id}", response_model=FoundItemResponse)
async def update_found_item(
    item_id: int,
    item_update: FoundItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update found item details (owner only)"""

    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Found item not found"
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
async def delete_found_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete found item entry (owner only)"""

    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Found item not found"
        )

    # Check ownership (or admin)
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )

    db.delete(item)
    db.commit()

    return MessageResponse(message="Found item deleted successfully", success=True)


@router.get("/my-items/", response_model=PaginatedFoundItems)
async def get_my_found_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's found items"""

    query = db.query(FoundItem).filter(FoundItem.user_id == current_user.id)

    if status:
        query = query.filter(FoundItem.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedFoundItems(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.patch("/{item_id}/status", response_model=FoundItemResponse)
async def update_found_item_status(
    item_id: int,
    new_status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update found item status (owner only)"""

    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Found item not found"
        )

    # Check ownership (or admin)
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    # Validate status
    valid_statuses = ["available", "claimed", "resolved"]
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


@router.get("/available/", response_model=PaginatedFoundItems)
async def get_available_found_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get only available (unclaimed) found items"""

    query = db.query(FoundItem).filter(FoundItem.status == "available")

    if category:
        query = query.filter(FoundItem.category == category)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    # Calculate pagination info
    pages = (total + limit - 1) // limit

    return PaginatedFoundItems(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )
