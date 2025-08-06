"""
Core configuration settings for TrackMate
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App info
    app_name: str = "TrackMate API"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered lost and found tracking system"
    debug: bool = True
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite:///./trackmate.db"
    
    # Security - STRONG SECRET KEY GENERATED
    secret_key: str = "TrackMate_SuperSecure_Key_2025_Change_This_In_Production_xyz789abc123def456"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # File Upload - Use string instead of List for .env compatibility
    upload_directory: str = "uploaded_images"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions_str: str = ".jpg,.jpeg,.png,.webp"
    
    # AI/ML
    clip_model: str = "clip-ViT-B-32"
    text_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.7
    
    # Email (for notifications) - Leave empty for now
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    # CORS - Use string instead of List for .env compatibility
    allowed_origins_str: str = "*"
    
    # Convert string fields to lists
    @property
    def allowed_extensions(self) -> List[str]:
        """Convert comma-separated string to list"""
        return [ext.strip() for ext in self.allowed_extensions_str.split(',')]
    
    @property 
    def allowed_origins(self) -> List[str]:
        """Convert comma-separated string to list"""
        if self.allowed_origins_str == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_str.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_directory, exist_ok=True)
