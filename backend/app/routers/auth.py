"""
Authentication router - CleanGrid Phase 2
JWT-based authentication with refresh token rotation
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, redis_client
from app.models.user import User

logger = __import__('structlog').get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt with cost factor 12"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost factor 12"""
    try:
        # Generate salt with cost factor 12
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise HTTPException(status_code=500, detail="Password processing failed")

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    """Create secure refresh token"""
    return secrets.token_urlsafe(32)

async def invalidate_refresh_token(refresh_token: str):
    """Invalidate refresh token by adding to Redis blacklist"""
    try:
        # Add to blacklist with TTL of remaining token validity
        await redis_client.setex(
            f"blacklist:{refresh_token}",
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,  # Convert days to seconds
            "invalidated"
        )
        logger.info(f"Refresh token invalidated: {refresh_token[:8]}...")
    except Exception as e:
        logger.error(f"Failed to invalidate refresh token: {e}")

async def is_refresh_token_blacklisted(refresh_token: str) -> bool:
    """Check if refresh token is blacklisted"""
    try:
        result = await redis_client.get(f"blacklist:{refresh_token}")
        return result is not None
    except Exception as e:
        logger.error(f"Failed to check refresh token blacklist: {e}")
        return False  # Fail open - allow request if Redis fails

@router.post("/login")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and issue JWT tokens"""
    
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token()
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create response
        response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        )
        
        # Set secure HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=True,  # Set to False for localhost, True in production
            samesite="strict",
            path="/"
        )
        
        if login_data.remember_me:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                httponly=True,
                secure=True,  # Set to False for localhost, True in production
                samesite="strict",
                path="/"
            )
        
        logger.info(f"User logged in: {user.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication service unavailable"
        )

@router.post("/refresh")
async def refresh_token(
    request: Request,
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    try:
        # Get refresh token from cookie or request body
        refresh_token = refresh_data.refresh_token
        if not refresh_token:
            refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="Refresh token required"
            )
        
        # Check if refresh token is blacklisted
        if await is_refresh_token_blacklisted(refresh_token):
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        # Find user by refresh token (in real implementation, this would be stored in DB)
        # For now, we'll decode the old token to get user info
        try:
            # This is a simplified approach - in production, store refresh tokens in DB
            payload = jwt.decode(
                refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token"
                )
            
            # Get user from database
            result = await db.execute(
                select(User).where(User.id == int(user_id))
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="User not found"
                )
            
            # Invalidate old refresh token
            await invalidate_refresh_token(refresh_token)
            
            # Create new tokens
            new_access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            new_refresh_token = create_refresh_token()
            
            # Create response
            response = JSONResponse(
                content={
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                    "token_type": "bearer",
                    "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
                }
            )
            
            # Set new cookies
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                httponly=True,
                secure=True,
                samesite="strict",
                path="/"
            )
            
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                httponly=True,
                secure=True,
                samesite="strict",
                path="/"
            )
            
            logger.info(f"Token refreshed for user: {user.email}")
            return response
            
        except JWTError as e:
            logger.error(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Token refresh service unavailable"
        )

@router.post("/logout")
async def logout(request: Request):
    """Logout user and invalidate tokens"""
    
    try:
        # Get refresh token from cookies
        refresh_token = request.cookies.get("refresh_token")
        
        if refresh_token:
            # Invalidate refresh token
            await invalidate_refresh_token(refresh_token)
        
        # Create response that clears cookies
        response = JSONResponse(
            content={"message": "Logged out successfully"}
        )
        
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        
        logger.info("User logged out")
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Logout service unavailable"
        )

@router.get("/health")
async def health():
    return {"status": "auth router healthy"}
