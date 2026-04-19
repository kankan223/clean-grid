"""
Configuration settings for CleanGrid AI Service
Uses Pydantic Settings for type-safe environment variables
"""

import os
from typing import Optional
from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


# Load .env file manually BEFORE creating settings class
def _load_env_file():
    """Load .env file manually to avoid JSON parsing issues with complex types"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    # Set in environment only if not already set
                    if not os.getenv(key):
                        os.environ[key] = value

# Load .env before defining settings class
_load_env_file()


class AISettings(BaseSettings):
    """
    AI Service settings
    All values are loaded from environment variables or .env file
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
    
    # Detection Classes - store as string from .env
    RELEVANT_CLASSES_STR: str = Field(
        default="bottle,cup,handbag,banana,can,backpack,suitcase,book,cell phone,remote,mouse,keyboard,wine glass",
        env="RELEVANT_CLASSES"
    )
    
    # File Upload Settings
    MAX_IMAGE_SIZE: int = Field(
        default=10485760,  # 10MB
        env="MAX_IMAGE_SIZE"
    )
    
    ALLOWED_EXTENSIONS_STR: str = Field(
        default="jpg,jpeg,png,webp",
        env="ALLOWED_EXTENSIONS"
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
    INFERENCE_IMAGE_SIZE_STR: str = Field(
        default="640,640",
        env="INFERENCE_IMAGE_SIZE"
    )
    
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=4,
        ge=1,
        le=16,
        env="MAX_CONCURRENT_REQUESTS"
    )
    
    # Model Download Settings
    AUTO_DOWNLOAD_MODEL_STR: str = Field(
        default="true",
        env="AUTO_DOWNLOAD_MODEL"
    )
    
    MODEL_DOWNLOAD_URL: str = Field(
        default="https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
        env="MODEL_DOWNLOAD_URL"
    )

    # Backend image access
    BACKEND_BASE_URL: str = Field(
        default="http://backend:8000",
        env="BACKEND_BASE_URL"
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
    
    # Severity Scoring Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for high severity"
    )
    HIGH_DETECTION_COUNT: int = Field(
        default=3,
        ge=1,
        description="Number of detections for high severity"
    )
    
    # Config
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields
    )
    
    @property
    def RELEVANT_CLASSES(self) -> set:
        """Parse RELEVANT_CLASSES from string format"""
        if isinstance(self.RELEVANT_CLASSES_STR, str):
            return set(item.strip() for item in self.RELEVANT_CLASSES_STR.split(',') if item.strip())
        return {"bottle", "cup", "handbag", "banana", "can", "backpack", "suitcase", "book", "cell phone", "remote", "mouse", "keyboard", "wine glass"}
    
    @property
    def ALLOWED_EXTENSIONS(self) -> list:
        """Parse ALLOWED_EXTENSIONS from string format"""
        if isinstance(self.ALLOWED_EXTENSIONS_STR, str):
            return [item.strip() for item in self.ALLOWED_EXTENSIONS_STR.split(',') if item.strip()]
        return ["jpg", "jpeg", "png", "webp"]
    
    @property
    def INFERENCE_IMAGE_SIZE(self) -> tuple:
        """Parse INFERENCE_IMAGE_SIZE from string format"""
        if isinstance(self.INFERENCE_IMAGE_SIZE_STR, str):
            try:
                parts = [int(item.strip()) for item in self.INFERENCE_IMAGE_SIZE_STR.split(',')]
                if len(parts) == 2:
                    return tuple(parts)
            except (ValueError, IndexError):
                pass
        return (640, 640)
    
    @property
    def AUTO_DOWNLOAD_MODEL(self) -> bool:
        """Parse AUTO_DOWNLOAD_MODEL from string format"""
        if isinstance(self.AUTO_DOWNLOAD_MODEL_STR, str):
            return self.AUTO_DOWNLOAD_MODEL_STR.lower() in ('true', '1', 'yes', 'on')
        return True


# Create settings instance - singleton pattern
_settings_instance = None

def get_settings() -> AISettings:
    """Get singleton settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AISettings()
    return _settings_instance

# For backward compatibility - create at module level
settings = AISettings()


