"""
Pydantic schemas for CLIP-enabled endpoints
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EmbeddingRequest(BaseModel):
    """Request to generate embeddings for an item"""
    item_id: int
    item_type: str  # "lost" or "found"
    force_regenerate: bool = False

class EmbeddingResponse(BaseModel):
    """Response from embedding generation"""
    item_id: int
    item_type: str
    success: bool
    embedding_model: str
    has_text_embedding: bool
    has_image_embedding: bool
    has_combined_embedding: bool
    processing_time: float
    error_message: Optional[str] = None

class SimilarityRequest(BaseModel):
    """Request for similarity matching"""
    query_item_id: int
    query_item_type: str  # "lost" or "found"
    target_item_type: Optional[str] = None  # Search in "lost", "found", or both
    similarity_threshold: float = 0.7
    max_results: int = 10
    include_location_boost: bool = True
    include_time_boost: bool = True

class SimilarityResult(BaseModel):
    """Individual similarity match result"""
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    item_type: str
    title: str
    description: str
    category: str
    location: str
    similarity_score: float
    confidence_level: float
    match_type: str
    matching_features: Optional[str] = None
    location_bonus: Optional[float] = None
    time_bonus: Optional[float] = None
    date_created: datetime
    image_count: int = 0

class SimilarityResponse(BaseModel):
    """Response from similarity search"""
    query_item_id: int
    query_item_type: str
    total_matches: int
    processing_time: float
    embedding_model: str
    algorithm_version: str
    matches: List[SimilarityResult]

class TextSearchRequest(BaseModel):
    """Semantic text search request"""
    query: str
    item_type: Optional[str] = None  # "lost", "found", or both
    category: Optional[str] = None
    similarity_threshold: float = 0.6
    max_results: int = 20

class ImageSearchRequest(BaseModel):
    """Visual image search - handled via file upload in endpoint"""
    item_type: Optional[str] = None
    category: Optional[str] = None
    similarity_threshold: float = 0.7
    max_results: int = 15

class MatchReviewRequest(BaseModel):
    """Request to review a similarity match"""
    match_id: int
    action: str  # "confirm", "dismiss", "needs_review"
    notes: Optional[str] = None

class MatchReviewResponse(BaseModel):
    """Response from match review"""
    match_id: int
    status: str
    reviewed_by: int
    review_notes: Optional[str] = None
    updated_at: datetime

class BatchEmbeddingRequest(BaseModel):
    """Request to generate embeddings for multiple items"""
    item_ids: List[int]
    item_type: str
    force_regenerate: bool = False

class BatchEmbeddingResponse(BaseModel):
    """Response from batch embedding generation"""
    total_items: int
    successful: int
    failed: int
    processing_time: float
    results: List[EmbeddingResponse]

class EmbeddingStatsResponse(BaseModel):
    """Statistics about embeddings in the system"""
    total_lost_items: int
    total_found_items: int
    lost_items_with_embeddings: int
    found_items_with_embeddings: int
    total_images: int
    images_with_embeddings: int
    embedding_model: str
    last_updated: datetime
