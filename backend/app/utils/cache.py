"""
Redis-backed cache. Every helper degrades to a no-op when Redis is unreachable,
so the API keeps working (more slowly) without it.
"""
import json
import logging
import os
from typing import Any, Optional

import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_EXPIRY = int(os.getenv("POSITION_CACHE_SECONDS", "30"))
POSITIONS_KEY = "satellite_positions"

try:
    redis_client: Optional[redis.Redis] = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as exc:  # noqa: BLE001 - any connection problem means "no cache"
    logger.warning("Redis unavailable (%s); caching disabled", exc)
    redis_client = None


def get_cached(key: str) -> Optional[Any]:
    if redis_client is None:
        return None
    try:
        raw = redis_client.get(key)
        return json.loads(raw) if raw else None
    except Exception as exc:  # noqa: BLE001
        logger.error("Cache read failed for %s: %s", key, exc)
        return None


def cache_custom(key: str, value: Any, expiry: int = 300) -> bool:
    if redis_client is None:
        return False
    try:
        redis_client.setex(key, expiry, json.dumps(value))
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Cache write failed for %s: %s", key, exc)
        return False


def get_cached_positions() -> Optional[list[dict]]:
    return get_cached(POSITIONS_KEY)


def set_cached_positions(positions: list[dict]) -> bool:
    return cache_custom(POSITIONS_KEY, positions, CACHE_EXPIRY)


def invalidate_cache() -> None:
    if redis_client is None:
        return
    try:
        redis_client.delete(POSITIONS_KEY)
        logger.info("Position cache invalidated")
    except Exception as exc:  # noqa: BLE001
        logger.error("Cache invalidation failed: %s", exc)
