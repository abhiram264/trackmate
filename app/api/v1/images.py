from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import json
from datetime import datetime
from PIL import Image as PILImage
import numpy as np

# ✅ CORRECT imports:
from app.models.image_model import Image
from app.models.lost_item import LostItem
from app.models.found_item import FoundItem
from app.models.user import User
from app.schemas.image_schema import (
    ImageUpload, ImageResponse, ImageSearchRequest, ImageSearchResult,
    SimilarImagesResponse
)
from app.schemas.base_schema import MessageResponse
from app.database import get_db
from app.api.deps import get_current_active_user

router = APIRouter()

# Rest of your endpoint code stays the same...


# Configuration
UPLOAD_DIRECTORY = "uploaded_images"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Initialize AI service (uncomment when you have it)
# ai_service = AIMatchingService()


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""

    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Check if it's actually an image
    try:
        img = PILImage.open(file.file)
        img.verify()
        file.file.seek(0)  # Reset file pointer
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )


def save_image_file(file: UploadFile) -> tuple[str, str]:
    """Save uploaded image file and return filename and path"""

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)

    return unique_filename, file_path


@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    item_id: int = Form(...),
    item_type: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload image for item (with item association)"""

    # Validate inputs
    if item_type not in ["lost", "found"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="item_type must be 'lost' or 'found'"
        )

    # Check if item exists and user owns it
    if item_type == "lost":
        item = db.query(LostItem).filter(LostItem.id == item_id).first()
    else:
        item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_type.title()} item not found"
        )

    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload image for this item"
        )

    # Validate file
    validate_image_file(file)

    # Save file
    filename, file_path = save_image_file(file)

    # Generate CLIP embedding (uncomment when AI service is ready)
    clip_embedding = None
    # try:
    #     embedding = ai_service.encode_image(file_path)
    #     clip_embedding = json.dumps(embedding.tolist())
    # except Exception as e:
    #     print(f"Failed to generate embedding: {e}")

    # Save to database
    new_image = Image(
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file.size,
        content_type=file.content_type,
        clip_embedding=clip_embedding,
        item_id=item_id,
        item_type=item_type,
        uploaded_by=current_user.id
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific image file"""

    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check if file exists
    if not os.path.exists(image.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on server"
        )

    # Return file response
    from fastapi.responses import FileResponse
    return FileResponse(
        path=image.file_path,
        media_type=image.content_type,
        filename=image.original_filename
    )


@router.post("/search-similar", response_model=SimilarImagesResponse)
async def search_similar_images(
    file: UploadFile = File(...),
    threshold: float = Form(0.7),
    limit: int = Form(10),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search for similar images using AI/ML"""

    # Validate file
    validate_image_file(file)

    # Save temporary file
    temp_filename, temp_path = save_image_file(file)

    try:
        # Generate embedding for search image (uncomment when AI service is ready)
        # search_embedding = ai_service.encode_image(temp_path)

        # Get all image embeddings from database
        images_with_embeddings = db.query(Image).filter(
            Image.clip_embedding.isnot(None)
        ).all()

        similar_images = []

        # For now, return empty results (uncomment when AI service is ready)
        # embeddings_db = []
        # for img in images_with_embeddings:
        #     try:
        #         embedding = np.array(json.loads(img.clip_embedding))
        #         embeddings_db.append((img.id, embedding))
        #     except Exception:
        #         continue
        # 
        # # Find similar images
        # similarities = ai_service.find_similar_images(
        #     temp_path, embeddings_db, top_k=limit
        # )
        # 
        # # Filter by threshold and prepare results
        # for img_id, similarity in similarities:
        #     if similarity >= threshold:
        #         img = db.query(Image).filter(Image.id == img_id).first()
        #         if img:
        #             similar_images.append(ImageSearchResult(
        #                 image_id=img.id,
        #                 item_id=img.item_id,
        #                 item_type=img.item_type,
        #                 similarity_score=similarity,
        #                 image_url=f"/images/{img.id}"
        #             ))

        search_time_ms = 50.0  # Placeholder

        return SimilarImagesResponse(
            results=similar_images,
            total_found=len(similar_images),
            search_time_ms=search_time_ms
        )

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.delete("/{image_id}", response_model=MessageResponse)
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete image (owner/admin only)"""

    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check ownership or admin
    if image.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this image"
        )

    # Delete file from disk
    if os.path.exists(image.file_path):
        os.remove(image.file_path)

    # Delete from database
    db.delete(image)
    db.commit()

    return MessageResponse(message="Image deleted successfully", success=True)


@router.get("/item/{item_id}/{item_type}", response_model=List[ImageResponse])
async def get_item_images(
    item_id: int,
    item_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all images for a specific item"""

    if item_type not in ["lost", "found"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="item_type must be 'lost' or 'found'"
        )

    # Check if item exists
    if item_type == "lost":
        item = db.query(LostItem).filter(LostItem.id == item_id).first()
    else:
        item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_type.title()} item not found"
        )

    # Get images
    images = db.query(Image).filter(
        Image.item_id == item_id,
        Image.item_type == item_type
    ).all()

    return images


@router.get("/", response_model=List[ImageResponse])
async def get_all_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    item_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all images with pagination (for admin/debugging)"""

    # Admin only for now
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    query = db.query(Image)

    if item_type:
        query = query.filter(Image.item_type == item_type)

    # Apply pagination
    offset = (page - 1) * limit
    images = query.offset(offset).limit(limit).all()

    return images
