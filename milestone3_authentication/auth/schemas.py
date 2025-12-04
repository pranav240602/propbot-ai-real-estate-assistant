from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GuestCreate(BaseModel):
    pass  # No data needed for guest

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    is_guest: bool
    guest_id: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: Optional[str]
    is_guest: bool
    guest_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True