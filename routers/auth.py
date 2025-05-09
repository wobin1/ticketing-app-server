from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import UserCreate, User, AuthResponse
from services.auth_service import authenticate_user, create_user
from utils.security import create_access_token

router = APIRouter()

@router.post("/login", response_model=AuthResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email, "role": user.role})
    return {"user": user, "token": access_token}

@router.post("/register", response_model=AuthResponse)
async def register(user: UserCreate):
    created_user = await create_user(user)
    access_token = create_access_token({"sub": created_user.email, "role": created_user.role})
    return {"user": created_user, "token": access_token}