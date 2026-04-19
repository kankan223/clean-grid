"""
Authentication router - CleanGrid Phase 2
JWT-based authentication with refresh token rotation
"""

import asyncio
import hashlib
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

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User

logger = __import__('structlog').get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# JWT Configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
IS_PRODUCTION = settings.ENVIRONMENT == "production"
IS_SECURE_COOKIE = settings.ENVIRONMENT != "development"

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt with cost factor 12"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def hash_password(password: str) -> str:
    """Hash password using bcrypt with dynamic cost factor"""
    try:
        # Use lower rounds for development to speed up hashing
        from app.core.config import settings
        rounds = 4 if settings.ENVIRONMENT == "development" else 12
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise HTTPException(status_code=500, detail="Password processing failed")

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def invalidate_refresh_token(refresh_token: str):
    """Invalidate refresh token by adding to Redis blacklist"""
    try:
        redis_client = await get_redis()

        # Add to blacklist with TTL of remaining token validity
        await redis_client.setex(
            f"blacklist:{refresh_token}",
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,  # Convert days to seconds
            "invalidated"
        )
        logger.info(f"Refresh token invalidated: {refresh_token[:8]}...")
    except Exception as e:
        logger.error(f"Failed to invalidate refresh token: {e}")
        raise HTTPException(status_code=500, detail="Failed to invalidate refresh token")

async def is_refresh_token_blacklisted(refresh_token: str) -> bool:
    """Check if refresh token is blacklisted"""
    try:
        redis_client = await get_redis()
        result = await redis_client.get(f"blacklist:{refresh_token}")
        return result is not None
    except Exception as e:
        logger.error(f"Failed to check refresh token blacklist: {e}")
        raise HTTPException(status_code=500, detail="Token blacklist check failed")

@router.post("/register")
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register new user and issue JWT tokens"""
    
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == register_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = hash_password(register_data.password)
        user = User(
            email=register_data.email,
            password_hash=hashed_password,
            display_name=register_data.display_name,
            role="citizen"
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Create tokens for immediate login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create response
        response = JSONResponse(
            content={
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "display_name": user.display_name,
                    "role": user.role.value,
                    "total_points": user.total_points,
                    "badge_tier": user.badge_tier.value if user.badge_tier else None,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                }
            }
        )
        
        # Set secure HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            samesite="strict",
            secure=IS_SECURE_COOKIE,
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            samesite="strict",
            secure=IS_SECURE_COOKIE,
            path="/",
        )
        
        logger.info(f"User registered successfully: {user.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

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
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create response
        response = JSONResponse(
            content={
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "display_name": user.display_name,
                    "role": user.role.value,
                    "total_points": user.total_points,
                    "badge_tier": user.badge_tier.value if user.badge_tier else None,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                }
            }
        )
        
        # Set secure HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            samesite="strict",
            secure=IS_SECURE_COOKIE,
            path="/"
        )
        
        if login_data.remember_me:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                httponly=True,
                secure=IS_SECURE_COOKIE,
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
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    try:
        # Cookie-only refresh flow keeps refresh token in HttpOnly channel.
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
            token_type = payload.get("type")
            
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token"
                )

            if token_type != "refresh":
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
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            # Create response
            response = JSONResponse(
                content={
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
                secure=IS_SECURE_COOKIE,
                samesite="strict",
                path="/"
            )
            
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                httponly=True,
                secure=IS_SECURE_COOKIE,
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

async def verify_access_token(request: Request) -> str:
    """
    Verify access token from cookie and return user ID
    This is a dependency function for protected routes
    """
    
    try:
        # Get access token from cookie
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="No access token provided"
            )
        
        # Decode token
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
        
        return user_id
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Token verification failed"
        )

@router.get("/health")
async def health():
    return {"status": "auth router healthy"}
