"""
Core configuration and utilities for TrackMate

This module contains core functionality used throughout the TrackMate application:
- Application configuration and settings management
- Security utilities for password hashing and JWT token management
- Authentication helpers and token verification
- Permission management for role-based access control
- Database and environment configuration utilities

All security functions use industry-standard algorithms (bcrypt, JWT).
"""

from .config import settings
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)

__version__ = "1.0.0"
__author__ = "TrackMate Development Team"

# Core modules available
CORE_MODULES = {
    "config": "Application settings and environment configuration",
    "security": "Password hashing, JWT tokens, and authentication utilities"
}

# Security configuration info
SECURITY_INFO = {
    "password_algorithm": "bcrypt",
    "jwt_algorithm": "HS256",
    "token_type": "Bearer",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7
}

__all__ = [
    "settings",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "SECURITY_INFO",
    "CORE_MODULES",
]
