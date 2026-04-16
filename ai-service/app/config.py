"""
Configuration settings for CleanGrid AI Service
Uses Pydantic Settings for type-safe environment variables
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """
    AI Service settings
    All values are loaded from environment variables
    """
    
    # Model Configuration
    YOLO_MODEL_PATH: str = Field(
        default="yolov8n.pt",
        env="YOLO_MODEL_PATH"
    )
    YOLO_CONFIDENCE_THRESHOLD: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        env="YOLO_CONFIDENCE_THRESHOLD"
    )
    
    # Detection Classes
    RELEVANT_CLASSES: set = Field(
        default={"bottle", "cup", "bag", "banana", "can", "backpack", "suitcase"}
    )
    
    # File Upload Settings
    MAX_IMAGE_SIZE: int = Field(
        default=10485760,  # 10MB
        env="MAX_IMAGE_SIZE"
    )
    ALLOWED_EXTENSIONS: list = Field(
        default=["jpg", "jpeg", "png", "webp"]
    )
    
    # Service Configuration
    AI_SERVICE_PORT: int = Field(
        default=8001,
        env="AI_SERVICE_PORT"
    )
    AI_SERVICE_HOST: str = Field(
        default="0.0.0.0",
        env="AI_SERVICE_HOST"
    )
    
    # Performance Settings
    INFERENCE_IMAGE_SIZE: tuple = Field(
        default=(640, 640)
    )
    
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=4,
        ge=1,
        le=16,
        env="MAX_CONCURRENT_REQUESTS"
    )
    
    # Model Download Settings
    AUTO_DOWNLOAD_MODEL: bool = Field(
        default=True,
        env="AUTO_DOWNLOAD_MODEL"
    )
    MODEL_DOWNLOAD_URL: str = Field(
        default="https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
        env="MODEL_DOWNLOAD_URL"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        env="LOG_LEVEL"
    )
    
    # Debug
    DEBUG: bool = Field(
        default=False,
        env="DEBUG"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = AISettings()
