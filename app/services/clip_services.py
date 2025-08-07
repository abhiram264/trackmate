"""
CLIP Service for handling embeddings and similarity matching
"""

import torch
import clip
import numpy as np
from PIL import Image as PILImage
import io
import json
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.models.lost_item import LostItem
from app.models.found_item import FoundItem
from app.models.image_model import Image
from app.models.similarity_match import SimilarityMatch
from app.core.config import settings

logger = logging.getLogger(__name__)

class CLIPService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.preprocess = None
        self.model_name = settings.clip_model or "ViT-B/32"
        self._load_model()

    def _load_model(self):
        """Load CLIP model"""
        try:
            self.model, self.preprocess = clip.load(self.model_name, device=self.device)
            logger.info(f"CLIP model {self.model_name} loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise

    async def encode_text(self, text: str) -> List[float]:
        """Encode text to embedding"""
        try:
            # Tokenize and encode
            text_tokens = clip.tokenize([text]).to(self.device)

            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            # Convert to list
            embedding = text_features.cpu().numpy()[0].tolist()
            return embedding

        except Exception as e:
            logger.error(f"Text encoding failed: {e}")
            raise

    async def encode_image_bytes(self, image_bytes: bytes) -> List[float]:
        """Encode image from bytes to embedding"""
        try:
            # Load image
            image = PILImage.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Preprocess and encode
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            # Convert to list
            embedding = image_features.cpu().numpy()[0].tolist()
            return embedding

        except Exception as e:
            logger.error(f"Image encoding failed: {e}")
            raise

    async def encode_image_file(self, file_path: str) -> List[float]:
        """Encode image from file path"""
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            return await self.encode_image_bytes(image_bytes)
        except Exception as e:
            logger.error(f"Failed to encode image file {file_path}: {e}")
            raise

    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            a = np.array(embedding1)
            b = np.array(embedding2)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    async def generate_item_embeddings(
        self, 
        item: Any, 
        item_type: str, 
        db: Session,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Generate all embeddings for an item"""

        try:
            # Check if embeddings already exist
            if not force_regenerate and item.combined_embedding:
                return {
                    "success": True,
                    "model": self.model_name,
                    "has_text": bool(item.description_embedding),
                    "has_image": bool(item.image_embedding),
                    "has_combined": bool(item.combined_embedding),
                    "message": "Embeddings already exist"
                }

            # Generate text embedding
            text_embedding = await self.encode_text(item.description)
            item.description_embedding = json.dumps(text_embedding)

            # Generate image embeddings if images exist
            images = db.query(Image).filter(
                Image.item_id == item.id,
                Image.item_type == item_type
            ).all()

            image_embeddings = []
            if images:
                for img in images:
                    try:
                        img_embedding = await self.encode_image_file(img.file_path)
                        image_embeddings.append(img_embedding)

                        # Store individual image embedding
                        img.image_embedding = json.dumps(img_embedding)
                        img.embedding_status = "processed"
                        img.embedding_model = self.model_name

                    except Exception as e:
                        logger.error(f"Failed to process image {img.id}: {e}")
                        img.embedding_status = "failed"
                        img.processing_error = str(e)

                # Average image embeddings if multiple
                if image_embeddings:
                    avg_image_embedding = np.mean(image_embeddings, axis=0).tolist()
                    item.image_embedding = json.dumps(avg_image_embedding)
                    item.has_images = True

            # Generate combined embedding
            if item.image_embedding:
                # Weighted combination of text and image
                text_weight = 0.4
                image_weight = 0.6

                combined = (
                    np.array(text_embedding) * text_weight + 
                    np.array(json.loads(item.image_embedding)) * image_weight
                )
                combined = combined / np.linalg.norm(combined)  # Normalize
                item.combined_embedding = json.dumps(combined.tolist())
            else:
                # Use text embedding as combined
                item.combined_embedding = item.description_embedding

            # Update metadata
            item.embedding_model = self.model_name
            item.embedding_version = "1.0"
            item.updated_at = datetime.now()

            db.commit()

            return {
                "success": True,
                "model": self.model_name,
                "has_text": True,
                "has_image": bool(item.image_embedding),
                "has_combined": True
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to generate embeddings for {item_type} item {item.id}: {e}")
            return {
                "success": False,
                "model": self.model_name,
                "has_text": False,
                "has_image": False,
                "has_combined": False,
                "error": str(e)
            }

    async def find_similar_items(
        self,
        query_item: Any,
        query_type: str,
        db: Session,
        target_type: Optional[str] = None,
        threshold: float = 0.7,
        max_results: int = 10,
        include_location_boost: bool = True,
        include_time_boost: bool = True
    ) -> List[Dict[str, Any]]:
        """Find similar items using embeddings"""

        if not query_item.combined_embedding:
            raise ValueError("Query item has no embeddings")

        query_embedding = json.loads(query_item.combined_embedding)
        matches = []

        # Define target tables
        target_tables = []
        if target_type == "lost" or (target_type is None and query_type == "found"):
            target_tables.append((LostItem, "lost"))
        if target_type == "found" or (target_type is None and query_type == "lost"):
            target_tables.append((FoundItem, "found"))

        for table_class, table_type in target_tables:
            # Get items with embeddings
            items = db.query(table_class).filter(
                table_class.combined_embedding.isnot(None),
                table_class.status == "active"
            ).all()

            for item in items:
                # Skip self
                if item.id == query_item.id and table_type == query_type:
                    continue

                try:
                    item_embedding = json.loads(item.combined_embedding)
                    similarity = self.cosine_similarity(query_embedding, item_embedding)

                    if similarity >= threshold:
                        # Calculate bonuses
                        location_bonus = 1.0
                        time_bonus = 1.0

                        if include_location_boost:
                            location_bonus = self._calculate_location_bonus(query_item, item)

                        if include_time_boost:
                            time_bonus = self._calculate_time_bonus(item)

                        final_score = similarity * location_bonus * time_bonus

                        # Count images
                        image_count = db.query(Image).filter(
                            Image.item_id == item.id,
                            Image.item_type == table_type
                        ).count()

                        matches.append({
                            "item_id": item.id,
                            "item_type": table_type,
                            "title": item.title,
                            "description": item.description,
                            "category": item.category,
                            "location": getattr(item, 'location_lost', getattr(item, 'location_found', '')),
                            "similarity_score": similarity,
                            "confidence_level": final_score,
                            "match_type": "combined_similarity",
                            "location_bonus": location_bonus if include_location_boost else None,
                            "time_bonus": time_bonus if include_time_boost else None,
                            "date_created": item.created_at,
                            "image_count": image_count
                        })

                except Exception as e:
                    logger.error(f"Error processing item {item.id}: {e}")
                    continue

        # Sort by final score and return top results
        matches.sort(key=lambda x: x["confidence_level"], reverse=True)
        return matches[:max_results]

    def _calculate_location_bonus(self, item1: Any, item2: Any) -> float:
        """Calculate location-based similarity bonus"""
        try:
            loc1 = getattr(item1, 'location_lost', getattr(item1, 'location_found', '')).lower()
            loc2 = getattr(item2, 'location_lost', getattr(item2, 'location_found', '')).lower()

            if loc1 == loc2:
                return 1.2  # Same location
            elif any(word in loc2 for word in loc1.split()) or any(word in loc1 for word in loc2.split()):
                return 1.1  # Similar location
            else:
                return 1.0  # Different location
        except:
            return 1.0

    def _calculate_time_bonus(self, item: Any) -> float:
        """Calculate time-based relevance bonus"""
        try:
            days_old = (datetime.now() - item.created_at).days
            if days_old <= 1:
                return 1.2  # Very recent
            elif days_old <= 7:
                return 1.1  # Recent
            elif days_old <= 30:
                return 1.0  # Normal
            else:
                return 0.9  # Older
        except:
            return 1.0

    async def search_by_text_embedding(
        self,
        query_embedding: List[float],
        db: Session,
        item_type: Optional[str] = None,
        category: Optional[str] = None,
        threshold: float = 0.6,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search items by text embedding"""

        matches = []
        tables = []

        if item_type == "lost" or item_type is None:
            tables.append((LostItem, "lost"))
        if item_type == "found" or item_type is None:
            tables.append((FoundItem, "found"))

        for table_class, table_type in tables:
            query_obj = db.query(table_class).filter(
                table_class.combined_embedding.isnot(None),
                table_class.status == "active"
            )

            if category:
                query_obj = query_obj.filter(table_class.category == category)

            items = query_obj.all()

            for item in items:
                try:
                    item_embedding = json.loads(item.combined_embedding)
                    similarity = self.cosine_similarity(query_embedding, item_embedding)

                    if similarity >= threshold:
                        matches.append({
                            "item_id": item.id,
                            "item_type": table_type,
                            "title": item.title,
                            "description": item.description,
                            "category": item.category,
                            "location": getattr(item, 'location_lost', getattr(item, 'location_found', '')),
                            "similarity_score": similarity,
                            "confidence_level": similarity,
                            "match_type": "text_similarity",
                            "date_created": item.created_at,
                            "image_count": 0
                        })

                except Exception as e:
                    logger.error(f"Error in text search for item {item.id}: {e}")
                    continue

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:max_results]

    async def search_by_image_embedding(
        self,
        query_embedding: List[float],
        db: Session,
        item_type: Optional[str] = None,
        category: Optional[str] = None,
        threshold: float = 0.7,
        max_results: int = 15
    ) -> List[Dict[str, Any]]:
        """Search items by image embedding"""

        # Similar implementation to text search but focusing on image embeddings
        matches = []
        tables = []

        if item_type == "lost" or item_type is None:
            tables.append((LostItem, "lost"))
        if item_type == "found" or item_type is None:
            tables.append((FoundItem, "found"))

        for table_class, table_type in tables:
            query_obj = db.query(table_class).filter(
                table_class.image_embedding.isnot(None),  # Items with images
                table_class.status == "active"
            )

            if category:
                query_obj = query_obj.filter(table_class.category == category)

            items = query_obj.all()

            for item in items:
                try:
                    item_embedding = json.loads(item.image_embedding)
                    similarity = self.cosine_similarity(query_embedding, item_embedding)

                    if similarity >= threshold:
                        image_count = db.query(Image).filter(
                            Image.item_id == item.id,
                            Image.item_type == table_type
                        ).count()

                        matches.append({
                            "item_id": item.id,
                            "item_type": table_type,
                            "title": item.title,
                            "description": item.description,
                            "category": item.category,
                            "location": getattr(item, 'location_lost', getattr(item, 'location_found', '')),
                            "similarity_score": similarity,
                            "confidence_level": similarity,
                            "match_type": "image_similarity",
                            "date_created": item.created_at,
                            "image_count": image_count
                        })

                except Exception as e:
                    logger.error(f"Error in image search for item {item.id}: {e}")
                    continue

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:max_results]
