"""
Redis caching utilities
"""
import logging
import json
import os
from typing import Optional, List, Dict
import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_EXPIRY = int(os.getenv("POSITION_CACHE_SECONDS", 30))

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Caching disabled.")
    redis_client = None


def get_cached_positions() -> Optional[List[Dict]]:
    """
    Get cached satellite positions.
    
    Returns:
        List of position dictionaries or None if not cached
    """
    if not redis_client:
        return None
    
    try:
        cached = redis_client.get("satellite_positions")
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached positions: {e}")
        return None


def set_cached_positions(positions: List[Dict]) -> bool:
    """
    Cache satellite positions.
    
    Args:
        positions: List of position dictionaries
        
    Returns:
        True if successfully cached
    """
    if not redis_client:
        return False
    
    try:
        redis_client.setex(
            "satellite_positions",
            CACHE_EXPIRY,
            json.dumps(positions)
        )
        return True
    except Exception as e:
        logger.error(f"Failed to cache positions: {e}")
        return False


def invalidate_cache():
    """Invalidate all cached data."""
    if not redis_client:
        return
    
    try:
        redis_client.delete("satellite_positions")
        logger.info("Cache invalidated")
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")


def cache_custom(key: str, value: any, expiry: int = 300) -> bool:
    """
    Cache custom data.
    
    Args:
        key: Cache key
        value: Value to cache (must be JSON serializable)
        expiry: Expiry time in seconds
        
    Returns:
        True if successfully cached
    """
    if not redis_client:
        return False
    
    try:
        redis_client.setex(key, expiry, json.dumps(value))
        return True
    except Exception as e:
        logger.error(f"Failed to cache {key}: {e}")
        return False


def get_cached(key: str) -> Optional[any]:
    """
    Get custom cached data.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None
    """
    if not redis_client:
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached {key}: {e}")
        return None


