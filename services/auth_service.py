from fastapi import HTTPException, status
from repositories.user_repository import UserRepository
from utils.security import verify_password, hash_password
from schemas.user import User, UserCreate
from utils.password_generator import generate_random_password
from services.email_service import send_account_creation_email

async def authenticate_user(email: str, password: str) -> User | None:
    user = await UserRepository.get_user_by_email(email)
    if user and verify_password(password, user["password"]):
        return User(
            id=user["id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            is_guest=user["is_guest"],
            role=user["role"]
        )
    return None

async def create_user(user: UserCreate, is_guest: bool = False) -> User:
    existing_user = await UserRepository.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password = user.password if not is_guest else generate_random_password()
    hashed_password = hash_password(password)
    
    user_id = await UserRepository.create_user({
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "password": hashed_password,
        "is_guest": is_guest,
        "role": "user"
    })
    
    created_user = await UserRepository.get_user_by_email(user.email)
    if is_guest:
        await send_account_creation_email(user.email, password)
    
    return User(
        id=created_user["id"],
        email=created_user["email"],
        first_name=created_user["first_name"],
        last_name=created_user["last_name"],
        is_guest=created_user["is_guest"],
        role=created_user["role"]
    )