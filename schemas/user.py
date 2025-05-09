from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_guest: bool
    role: str

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: User
    token: str