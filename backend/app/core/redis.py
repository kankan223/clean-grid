"""
Redis client configuration for CleanGrid Backend
Used for caching, rate limiting, and session management
"""

import redis.asyncio as redis
from redis.asyncio import Redis
from typing import Optional, Any
import json

from app.core.config import settings

# Global Redis client
redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """
    Initialize Redis connection
    """
    global redis_client
    
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        retry_on_timeout=True,
    )
    
    return redis_client


async def get_redis() -> Redis:
    """
    Get Redis client (lazy initialization)
    """
    global redis_client
    
    if redis_client is None:
        redis_client = await init_redis()
    
    return redis_client


# Redis utility functions
async def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set cache value with TTL
    """
    try:
        client = await get_redis()
        serialized_value = json.dumps(value) if not isinstance(value, str) else value
        await client.setex(key, ttl, serialized_value)
        return True
    except Exception:
        return False


async def get_cache(key: str) -> Optional[Any]:
    """
    Get cache value
    """
    try:
        client = await get_redis()
        value = await client.get(key)
        
        if value is None:
            return None
        
        # Try to deserialize JSON, return as string if fails
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
            
    except Exception:
        return None


async def delete_cache(key: str) -> bool:
    """
    Delete cache key
    """
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception:
        return False


async def increment_counter(key: str, ttl: int = 60) -> int:
    """
    Increment counter with TTL
    Used for rate limiting
    """
    try:
        client = await get_redis()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        result = await pipe.execute()
        return result[0]
    except Exception:
        return 0


async def add_to_set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    Add value to Redis set
    Used for blacklists/whitelists
    """
    try:
        client = await get_redis()
        await client.sadd(key, value)
        
        if ttl:
            await client.expire(key, ttl)
            
        return True
    except Exception:
        return False


async def is_in_set(key: str, value: str) -> bool:
    """
    Check if value exists in Redis set
    """
    try:
        client = await get_redis()
        return bool(await client.sismember(key, value))
    except Exception:
        return False


async def remove_from_set(key: str, value: str) -> bool:
    """
    Remove value from Redis set
    """
    try:
        client = await get_redis()
        await client.srem(key, value)
        return True
    except Exception:
        return False
