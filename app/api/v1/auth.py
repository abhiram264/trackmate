from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated

# ✅ CORRECT imports:
from app.database import get_db
from app.models.user import User
from app.models.student_registry import StudentRegistry
from app.schemas.user import (
    UserSignup, UserLogin, UserUpdate, UserResponse, 
    TokenResponse, RefreshTokenRequest
)
from app.schemas.base_schema import MessageResponse
from app.core.security import (
    verify_password, get_password_hash, 
    create_access_token, create_refresh_token, verify_token
)
from app.core.config import settings
from app.api.deps import get_current_active_user, get_admin_user

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user with student email verification"""

    # Normalize inputs to avoid mismatches
    user_email = user_data.email.strip().lower()
    user_student_id = user_data.student_id.strip()

    # Check if user already exists (using normalized email)
    existing_user = db.query(User).filter(User.email == user_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Verify student is in registry with normalized data
    student = db.query(StudentRegistry).filter(
        StudentRegistry.email == user_email,
        StudentRegistry.student_id == user_student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student not found in registry. Please contact admin."
        )
    
    # Create new user with normalized email/student_id
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_email,
        student_id=user_student_id,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens"""

    login_email = user_credentials.email.strip().lower()

    user = db.query(User).filter(User.email == login_email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user
    )



@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh JWT access token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    # Update fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """User logout (token blacklisting would be implemented here)"""
    # In a production app, you'd blacklist the token
    # For now, just return success message
    return MessageResponse(message="Successfully logged out", success=True)
