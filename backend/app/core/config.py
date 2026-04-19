"""
Configuration settings for CleanGrid Backend
Uses Pydantic Settings for type-safe environment variables
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings
    All values are loaded from environment variables
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    # Application
    APP_NAME: str = "CleanGrid Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cleangrid:cleangrid@localhost:5433/cleangrid",
        validation_alias="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    # Security
    JWT_SECRET_KEY: str = Field(
        ...,
        min_length=32,
        validation_alias="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Default Admin Credentials
    DEFAULT_ADMIN_EMAIL: str = Field(
        default="admin@cleangrid.io",
        validation_alias="DEFAULT_ADMIN_EMAIL"
    )
    DEFAULT_ADMIN_PASSWORD: str = Field(
        default="CleanGrid@2024",
        validation_alias="DEFAULT_ADMIN_PASSWORD"
    )
    
    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="",
        validation_alias="ALLOWED_ORIGINS"
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        validation_alias="CORS_ORIGINS"
    )
    
    # External APIs
    AI_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        validation_alias="AI_SERVICE_URL"
    )
    BACKEND_PUBLIC_URL: str = Field(
        default="http://localhost:8000",
        validation_alias="BACKEND_PUBLIC_URL"
    )
    ORS_API_KEY: Optional[str] = Field(
        default=None,
        validation_alias="ORS_API_KEY"
    )
    
    # Cloudflare R2 Storage
    R2_ENDPOINT_URL: Optional[str] = Field(
        default=None,
        validation_alias="R2_ENDPOINT_URL"
    )
    R2_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        validation_alias="R2_ACCESS_KEY_ID"
    )
    R2_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        validation_alias="R2_SECRET_ACCESS_KEY"
    )
    R2_BUCKET_NAME: Optional[str] = Field(
        default=None,
        validation_alias="R2_BUCKET_NAME"
    )
    
    # Geocoding
    NOMINATIM_BASE_URL: str = Field(
        default="https://nominatim.openstreetmap.org/reverse",
        validation_alias="NOMINATIM_BASE_URL"
    )
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png", 
        "image/webp"
    ]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
# Create settings instance
settings = Settings()  # pyright: ignore[reportCallIssue]
