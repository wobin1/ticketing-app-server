# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.user import User
from utils.security import verify_token
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    logger.info("Verifying token from Authorization header for user")
    user = await verify_token(token)
    if not user:
        logger.error("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"Authenticated user: {user.email}")
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    logger.info(f"Checking admin role for user: {current_user.email}")
    if current_user.role != "admin":
        logger.error(f"User {current_user.email} is not an admin")
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user