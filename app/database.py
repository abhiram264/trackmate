"""
Database configuration and setup for TrackMate
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session
from typing import Generator
import os

# Import your models to ensure they're registered
from app.models import *

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trackmate.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Only for SQLite
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database on startup
def init_db():
    """Initialize database with tables"""
    create_tables()
