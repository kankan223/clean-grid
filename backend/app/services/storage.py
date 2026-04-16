"""
Storage service - CleanGrid Phase 1
File upload handling with local filesystem storage
"""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import Optional
import structlog

logger = structlog.get_logger()


# Upload directory
UPLOAD_DIR = "/app/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS


async def save_upload_file(file) -> str:
    """
    Save uploaded file to local storage
    
    Args:
        file: Uploaded file object
        
    Returns:
        URL path for saved file
    """
    try:
        # Validate file
        if not is_allowed_file(file.filename):
            raise ValueError(f"File type not allowed: {file.filename}")
        
        # Generate unique filename
        ext = get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save file
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Return URL path (in production, this would be a CDN URL)
        file_url = f"/uploads/{unique_filename}"
        
        logger.info(
            "File saved successfully",
            filename=unique_filename,
            size_bytes=len(content)
        )
        
        return file_url
        
    except Exception as e:
        logger.error("Failed to save file", error=str(e))
        raise


def get_upload_dir() -> str:
    """Get upload directory path"""
    return UPLOAD_DIR
