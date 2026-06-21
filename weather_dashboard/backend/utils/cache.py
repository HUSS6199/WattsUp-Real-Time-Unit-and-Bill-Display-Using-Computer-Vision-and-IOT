"""Caching utilities for Weather Dashboard."""

from datetime import datetime, timedelta
from typing import Any, Optional
import json

# Simple in-memory cache
_cache = {}


def get_cached(key: str) -> Optional[Any]:
    """
    Get value from cache if not expired.
    
    Args:
        key: Cache key
    
    Returns:
        Cached value or None if expired/not found
    """
    if key not in _cache:
        return None
    
    cached_item = _cache[key]
    
    # Check if expired
    if datetime.now() > cached_item['expires_at']:
        del _cache[key]
        return None
    
    return cached_item['value']


def set_cached(key: str, value: Any, ttl: int) -> None:
    """
    Set value in cache with TTL.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time-to-live in seconds
    """
    _cache[key] = {
        'value': value,
        'expires_at': datetime.now() + timedelta(seconds=ttl)
    }


def delete_cached(key: str) -> None:
    """
    Delete value from cache.
    
    Args:
        key: Cache key
    """
    if key in _cache:
        del _cache[key]


def clear_cache() -> None:
    """
    Clear all cache.
    """
    global _cache
    _cache = {}


def get_cache_stats() -> dict:
    """
    Get cache statistics.
    
    Returns:
        Dict with cache stats
    """
    total = len(_cache)
    expired = sum(1 for item in _cache.values() if datetime.now() > item['expires_at'])
    active = total - expired
    
    # Clean up expired items
    for key in list(_cache.keys()):
        if datetime.now() > _cache[key]['expires_at']:
            del _cache[key]
    
    return {
        'total_keys': total,
        'active_keys': active,
        'expired_keys': expired
    }
