"""
Service layer implementations for TrackMate

This module encapsulates all business logic and external integrations:
- CLIPService: AI-powered embedding generation and similarity matching
- (Future services can be added here, e.g., NotificationService, EmailService)
"""

from .clip_services import CLIPService

__version__ = "1.0.0"
__author__ = "TrackMate Development Team"

__all__ = [
    "CLIPService",
]
