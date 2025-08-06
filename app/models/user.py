from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"
    STAFF = "staff"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True, max_length=100)
    student_id: str = Field(nullable=False, unique=True, max_length=50)
    full_name: str = Field(nullable=False, max_length=100)
    hashed_password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True)
    
    # Add these missing fields:
    phone: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default=None)
