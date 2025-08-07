"""
API endpoints for CLIP-powered similarity matching
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import time
from datetime import datetime, timedelta

from app.database import get_db
from app.models.lost_item import LostItem
from app.models.found_item import FoundItem  
from app.models.image_model import Image
from app.models.similarity_match import SimilarityMatch
from app.schemas.clip_schemas import *
from app.api.deps import get_current_active_user, get_admin_user
from app.services.clip_services import CLIPService
from app.core.config import settings

router = APIRouter()

# Initialize CLIP service
clip_service = CLIPService()

@router.post("/embeddings/generate", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Generate CLIP embeddings for a lost/found item"""

    start_time = time.time()

    try:
        # Get the item
        if request.item_type == "lost":
            item = db.query(LostItem).filter(LostItem.id == request.item_id).first()
        else:
            item = db.query(FoundItem).filter(FoundItem.id == request.item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Check if user owns item or is admin
        if item.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")

        # Generate embeddings
        result = await clip_service.generate_item_embeddings(
            item, request.item_type, db, force_regenerate=request.force_regenerate
        )

        processing_time = time.time() - start_time

        return EmbeddingResponse(
            item_id=request.item_id,
            item_type=request.item_type,
            success=result["success"],
            embedding_model=result["model"],
            has_text_embedding=result["has_text"],
            has_image_embedding=result["has_image"],
            has_combined_embedding=result["has_combined"],
            processing_time=processing_time,
            error_message=result.get("error")
        )

    except Exception as e:
        processing_time = time.time() - start_time
        return EmbeddingResponse(
            item_id=request.item_id,
            item_type=request.item_type,
            success=False,
            embedding_model="",
            has_text_embedding=False,
            has_image_embedding=False,
            has_combined_embedding=False,
            processing_time=processing_time,
            error_message=str(e)
        )

@router.post("/similarity/find", response_model=SimilarityResponse)
async def find_similar_items(
    request: SimilarityRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Find similar items using CLIP embeddings"""

    start_time = time.time()

    # Get query item
    if request.query_item_type == "lost":
        query_item = db.query(LostItem).filter(LostItem.id == request.query_item_id).first()
    else:
        query_item = db.query(FoundItem).filter(FoundItem.id == request.query_item_id).first()

    if not query_item:
        raise HTTPException(status_code=404, detail="Query item not found")

    # Find similar items
    matches = await clip_service.find_similar_items(
        query_item,
        request.query_item_type,
        db,
        target_type=request.target_item_type,
        threshold=request.similarity_threshold,
        max_results=request.max_results,
        include_location_boost=request.include_location_boost,
        include_time_boost=request.include_time_boost
    )

    processing_time = time.time() - start_time

    return SimilarityResponse(
        query_item_id=request.query_item_id,
        query_item_type=request.query_item_type,
        total_matches=len(matches),
        processing_time=processing_time,
        embedding_model=settings.clip_model,
        algorithm_version="1.0",
        matches=matches
    )

@router.post("/search/text", response_model=SimilarityResponse)
async def semantic_text_search(
    request: TextSearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Semantic search using text query"""

    start_time = time.time()

    # Generate embedding for search query
    query_embedding = await clip_service.encode_text(request.query)

    # Search items
    matches = await clip_service.search_by_text_embedding(
        query_embedding,
        db,
        item_type=request.item_type,
        category=request.category,
        threshold=request.similarity_threshold,
        max_results=request.max_results
    )

    processing_time = time.time() - start_time

    return SimilarityResponse(
        query_item_id=0,  # No specific item
        query_item_type="text_search",
        total_matches=len(matches),
        processing_time=processing_time,
        embedding_model=settings.clip_model,
        algorithm_version="1.0",
        matches=matches
    )

@router.post("/search/image", response_model=SimilarityResponse)
async def visual_image_search(
    file: UploadFile = File(...),
    item_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    similarity_threshold: float = Query(0.7),
    max_results: int = Query(15),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Visual search using uploaded image"""

    start_time = time.time()

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read and encode image
    image_data = await file.read()
    query_embedding = await clip_service.encode_image_bytes(image_data)

    # Search items
    matches = await clip_service.search_by_image_embedding(
        query_embedding,
        db,
        item_type=item_type,
        category=category,
        threshold=similarity_threshold,
        max_results=max_results
    )

    processing_time = time.time() - start_time

    return SimilarityResponse(
        query_item_id=0,
        query_item_type="image_search",
        total_matches=len(matches),
        processing_time=processing_time,
        embedding_model=settings.clip_model,
        algorithm_version="1.0",
        matches=matches
    )

@router.get("/matches/pending", response_model=List[SimilarityResult])
async def get_pending_matches(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user),
    limit: int = Query(50, le=100)
):
    """Get pending similarity matches for admin review"""

    matches = db.query(SimilarityMatch).filter(
        SimilarityMatch.status == "pending"
    ).order_by(
        SimilarityMatch.similarity_score.desc()
    ).limit(limit).all()

    return [await clip_service.format_match_result(match, db) for match in matches]

@router.put("/matches/{match_id}/review", response_model=MatchReviewResponse)
async def review_similarity_match(
    match_id: int,
    request: MatchReviewRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Review and update a similarity match"""

    match = db.query(SimilarityMatch).filter(SimilarityMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Update match status
    if request.action == "confirm":
        match.status = "confirmed"
    elif request.action == "dismiss":
        match.status = "dismissed"
    else:
        match.status = "reviewed"

    match.reviewed_by = current_user.id
    match.review_notes = request.notes
    match.updated_at = datetime.now()

    db.commit()
    db.refresh(match)

    return MatchReviewResponse(
        match_id=match_id,
        status=match.status,
        reviewed_by=current_user.id,
        review_notes=request.notes,
        updated_at=match.updated_at
    )

@router.post("/embeddings/batch", response_model=BatchEmbeddingResponse)
async def generate_batch_embeddings(
    request: BatchEmbeddingRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Generate embeddings for multiple items (admin only)"""

    start_time = time.time()
    results = []
    successful = 0
    failed = 0

    for item_id in request.item_ids:
        try:
            embed_request = EmbeddingRequest(
                item_id=item_id,
                item_type=request.item_type,
                force_regenerate=request.force_regenerate
            )

            result = await generate_embeddings(embed_request, db, current_user)
            results.append(result)

            if result.success:
                successful += 1
            else:
                failed += 1

        except Exception as e:
            failed += 1
            results.append(EmbeddingResponse(
                item_id=item_id,
                item_type=request.item_type,
                success=False,
                embedding_model="",
                has_text_embedding=False,
                has_image_embedding=False,
                has_combined_embedding=False,
                processing_time=0,
                error_message=str(e)
            ))

    processing_time = time.time() - start_time

    return BatchEmbeddingResponse(
        total_items=len(request.item_ids),
        successful=successful,
        failed=failed,
        processing_time=processing_time,
        results=results
    )

@router.get("/embeddings/stats", response_model=EmbeddingStatsResponse)
async def get_embedding_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get statistics about embeddings in the system"""

    lost_total = db.query(LostItem).count()
    found_total = db.query(FoundItem).count()

    lost_with_embeddings = db.query(LostItem).filter(
        LostItem.combined_embedding.isnot(None)
    ).count()

    found_with_embeddings = db.query(FoundItem).filter(
        FoundItem.combined_embedding.isnot(None)
    ).count()

    images_total = db.query(Image).count()
    images_with_embeddings = db.query(Image).filter(
        Image.image_embedding.isnot(None)
    ).count()

    return EmbeddingStatsResponse(
        total_lost_items=lost_total,
        total_found_items=found_total,
        lost_items_with_embeddings=lost_with_embeddings,
        found_items_with_embeddings=found_with_embeddings,
        total_images=images_total,
        images_with_embeddings=images_with_embeddings,
        embedding_model=settings.clip_model,
        last_updated=datetime.now()
    )

@router.delete("/embeddings/cleanup")
async def cleanup_old_embeddings(
    older_than_days: int = Query(30, description="Remove embeddings older than X days"),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Clean up old embeddings (admin only)"""

    cutoff_date = datetime.now() - timedelta(days=older_than_days)

    # Update items to remove old embeddings
    lost_updated = db.query(LostItem).filter(
        LostItem.updated_at < cutoff_date,
        LostItem.combined_embedding.isnot(None)
    ).update({
        "description_embedding": None,
        "image_embedding": None,
        "combined_embedding": None,
        "embedding_model": None,
        "embedding_version": None
    })

    found_updated = db.query(FoundItem).filter(
        FoundItem.updated_at < cutoff_date,
        FoundItem.combined_embedding.isnot(None)
    ).update({
        "description_embedding": None,
        "image_embedding": None, 
        "combined_embedding": None,
        "embedding_model": None,
        "embedding_version": None
    })

    db.commit()

    return {
        "message": f"Cleaned up embeddings older than {older_than_days} days",
        "lost_items_updated": lost_updated,
        "found_items_updated": found_updated
    }
