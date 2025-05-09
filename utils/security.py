# app/utils/security.py
import jwt
from passlib.context import CryptContext
from config import settings
from schemas.user import User
from datetime import datetime, timedelta
from typing import Optional
import logging
 
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=300)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def verify_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            logger.error("Token payload missing 'sub' field")
            return None
        # Fetch user from database (simplified, assumes user exists)
        from repositories.user_repository import UserRepository
        user_data = await UserRepository.get_user_by_email(email)
        if not user_data:
            logger.error(f"No user found for email: {email}")
            return None
        return User(**user_data)
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return None


# async def verify_token(token: str):
#     try:
#         # Add your JWT secret key here
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_data = payload.get("sub")
#         if user_data is None:
#             logger.error("Token payload does not contain user data")
#             return None
        
#         # Convert payload to User object
#         return User(**user_data)
#     except jwt.ExpiredSignatureError:
#         logger.error("Token has expired")
#         return None
#     except jwt.JWTError as e:
#         logger.error(f"Failed to decode token: {str(e)}")
#         return None