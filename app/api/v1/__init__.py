"""
TrackMate API v1 - Module initialization

This module contains all the API endpoints for TrackMate v1:
- Authentication
- Lost items
- Found items
- Claims
- Images
- CLIP AI
"""

from . import auth
from . import lost_items
from . import found_items
from . import claims
from . import images
from . import clip

__version__ = "1.0.0"
__author__ = "TrackMate Development Team"

# Endpoint counts by module
ENDPOINT_COUNTS = {
    "auth": 6,
    "lost_items": 8,
    "found_items": 8,
    "claims": 7,
    "images": 4,
    "clip": 9,
}

TOTAL_ENDPOINTS = sum(ENDPOINT_COUNTS.values())  # 42

__all__ = [
    "auth",
    "lost_items",
    "found_items",
    "claims",
    "images",
    "clip",
]
