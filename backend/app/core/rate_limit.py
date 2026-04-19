"""
Rate limiting configuration for CleanGrid Backend.
Uses slowapi with Redis-backed storage so limits are shared across workers.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    headers_enabled=True,
    default_limits=[],
)