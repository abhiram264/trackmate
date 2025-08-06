 
"""
Core configuration settings for TrackMate
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # App info
    app_name: str = "TrackMate API"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered lost and found tracking system"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./trackmate.db"

    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # File Upload
    upload_directory: str = "uploaded_images"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".webp"]

    # AI/ML
    clip_model: str = "clip-ViT-B-32"
    text_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.7

    # Email (for notifications)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None

    # CORS
    allowed_origins: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_directory, exist_ok=True)
