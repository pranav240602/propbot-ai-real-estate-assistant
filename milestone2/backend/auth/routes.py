from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from database.db import get_db
from auth import models, schemas, utils

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = utils.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_guest=False,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = utils.create_access_token(
        data={"user_id": new_user.id, "email": new_user.email, "is_guest": False}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "is_guest": False,
        "guest_id": None
    }

@router.post("/login", response_model=schemas.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    
    # Find user
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = utils.create_access_token(
        data={"user_id": db_user.id, "email": db_user.email, "is_guest": False}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "is_guest": False,
        "guest_id": None
    }

@router.post("/guest", response_model=schemas.Token)
def create_guest_user(db: Session = Depends(get_db)):
    """Create a guest user (no email/password required)"""
    
    # Generate unique guest ID
    guest_id = str(uuid.uuid4())
    
    # Guest expires in 30 days
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    # Create guest user
    guest_user = models.User(
        guest_id=guest_id,
        is_guest=True,
        is_active=True,
        expires_at=expires_at
    )
    
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)
    
    # Create access token
    access_token = utils.create_access_token(
        data={"user_id": guest_user.id, "guest_id": guest_id, "is_guest": True}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": guest_user.id,
        "is_guest": True,
        "guest_id": guest_id
    }

@router.get("/verify")
def verify_token(token: str):
    """Verify if a token is valid"""
    payload = utils.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return {"valid": True, "payload": payload}