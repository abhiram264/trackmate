from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Enum as SQLEnum, or_
from typing import Optional, List
from datetime import datetime

from app.models.found_item import FoundItem, ItemStatus  # Import the Enum
from app.models.user import User
from app.schemas.found_item import (
    FoundItemCreate,
    FoundItemUpdate,
    FoundItemResponse,
    PaginatedFoundItems
)
from app.schemas.base_schema import MessageResponse
from app.database import get_db
from app.api.deps import get_current_active_user, get_admin_user

router = APIRouter()


# Override the FoundItem.status column to store enum values (lowercase text)
FoundItem.__table__.columns["status"].type = SQLEnum(
    ItemStatus,
    name="itemstatus",
    native_enum=False,
    values_callable=lambda enum: [e.value for e in enum]
)


@router.post("/", response_model=FoundItemResponse, status_code=status.HTTP_201_CREATED)
async def create_found_item(
    item_data: FoundItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new found item"""
    new_item = FoundItem(
        title=item_data.title,
        description=item_data.description,
        category=item_data.category,
        location_found=item_data.location_found,
        date_found=item_data.date_found,
        current_location=item_data.current_location,
        handover_instructions=item_data.handover_instructions,
        user_id=current_user.id,
        # status defaults to ItemStatus.ACTIVE.value
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
    db: Session = Depends(get_db),
):
    """List all found items with filtering"""
    query = db.query(FoundItem)

    if search:
        query = query.filter(
            or_(
                FoundItem.title.ilike(f"%{search}%"),
                FoundItem.description.ilike(f"%{search}%"),
            )
        )
    if category:
        query = query.filter(FoundItem.category == category)
    if status:
        # Legacy support: convert "available" to "active"
        if status == "available":
            status = ItemStatus.ACTIVE.value
        if status not in {e.value for e in ItemStatus}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status}",
            )
        query = query.filter(FoundItem.status == status)
    if location:
        query = query.filter(
            or_(
                FoundItem.location_found.ilike(f"%{location}%"),
                FoundItem.current_location.ilike(f"%{location}%"),
            )
        )
    if date_from:
        try:
            d0 = datetime.fromisoformat(date_from)
            query = query.filter(FoundItem.date_found >= d0)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format; use ISO."
            )
    if date_to:
        try:
            d1 = datetime.fromisoformat(date_to)
            query = query.filter(FoundItem.date_found <= d1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format; use ISO."
            )

    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    pages = (total + limit - 1) // limit

    return PaginatedFoundItems(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages,
    )


@router.get("/{item_id}", response_model=FoundItemResponse)
async def get_found_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get specific found item details"""
    item = db.query(FoundItem).get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item


@router.put("/{item_id}", response_model=FoundItemResponse)
async def update_found_item(
    item_id: int,
    item_update: FoundItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update found item (owner or admin)"""
    item = db.query(FoundItem).get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    for k, v in item_update.dict(exclude_unset=True).items():
        setattr(item, k, v)
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_found_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete found item (owner or admin)"""
    item = db.query(FoundItem).get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    db.delete(item)
    db.commit()
    return MessageResponse(message="Deleted", success=True)


@router.get("/my-items/", response_model=PaginatedFoundItems)
async def get_my_found_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current user’s items"""
    query = db.query(FoundItem).filter(FoundItem.user_id == current_user.id)
    if status:
        if status == "available":
            status = ItemStatus.ACTIVE.value
        query = query.filter(FoundItem.status == status)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = (total + limit - 1) // limit
    return PaginatedFoundItems(
        items=items, total=total, page=page, per_page=limit, pages=pages
    )


@router.patch("/{item_id}/status", response_model=FoundItemResponse)
async def update_found_item_status(
    item_id: int,
    new_status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update status (owner or admin)"""
    item = db.query(FoundItem).get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Handle legacy “available”
    if new_status == "available":
        new_status = ItemStatus.ACTIVE.value

    if new_status not in {e.value for e in ItemStatus}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}"
        )

    item.status = new_status
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.get("/active/", response_model=PaginatedFoundItems)
async def get_active_found_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all active items"""
    query = db.query(FoundItem).filter(FoundItem.status == ItemStatus.ACTIVE.value)
    if category:
        query = query.filter(FoundItem.category == category)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = (total + limit - 1) // limit
    return PaginatedFoundItems(
        items=items, total=total, page=page, per_page=limit, pages=pages
    )


@router.get("/available/", response_model=PaginatedFoundItems)
async def get_available_found_items_legacy(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Legacy endpoint for “available”—redirects to /active/"""
    return await get_active_found_items(page, limit, category, current_user, db)
