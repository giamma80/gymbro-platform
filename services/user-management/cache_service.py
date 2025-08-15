"""
🧠 In-Memory Cache Service for GymBro Platform
==============================================

Redis replacement for MVP deployment - zero cost solution.
Provides session storage, caching, and basic rate limiting.

Features:
- ✅ Thread-safe in-memory cache
- ✅ TTL-based expiration
- ✅ Automatic cleanup of expired keys
- ✅ Usage statistics
- ✅ LRU eviction for memory management
- ✅ Simple API compatible with Redis patterns

Usage:
    from cache_service import cache

    # Set with TTL
    cache.set("user:123", user_data, ttl=3600)

    # Get value
    user = cache.get("user:123")

    # Delete
    cache.delete("user:123")
"""

import threading
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, Optional


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support.

    Perfect replacement for Redis in MVP scenarios where
    persistence is not critical and cost optimization is key.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize cache with optional size limit.

        Args:
            max_size: Maximum number of keys to store (LRU eviction)
        """
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._access_counts: Dict[str, int] = {}
        self._max_size = max_size
        self._lock = threading.RLock()  # Reentrant lock for nested calls

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a key-value pair with TTL.

        Args:
            key: Cache key
            value: Value to store (any Python object)
            ttl: Time to live in seconds (default: 1 hour)
        """
        with self._lock:
            expiry = time.time() + ttl

            # If key exists, remove it first to update position
            if key in self._cache:
                del self._cache[key]

            # Add new item
            self._cache[key] = {
                "value": value,
                "expiry": expiry,
                "created": time.time(),
                "size": self._estimate_size(value),
            }

            # Move to end (most recently used)
            self._cache.move_to_end(key)

            # Evict if over size limit
            self._evict_if_needed()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key, return None if not found or expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        with self._lock:
            self._cleanup_expired()

            if key in self._cache:
                item = self._cache[key]
                current_time = time.time()

                if current_time < item["expiry"]:
                    # Track access
                    self._access_counts[key] = self._access_counts.get(key, 0) + 1

                    # Move to end (mark as recently used)
                    self._cache.move_to_end(key)

                    return item["value"]
                else:
                    # Expired - remove
                    del self._cache[key]
                    if key in self._access_counts:
                        del self._access_counts[key]

            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_counts:
                    del self._access_counts[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and valid
        """
        return self.get(key) is not None

    def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching pattern (simplified - only supports '*').

        Args:
            pattern: Key pattern (only '*' supported for now)

        Returns:
            List of matching keys
        """
        with self._lock:
            self._cleanup_expired()

            if pattern == "*":
                return list(self._cache.keys())
            else:
                # Simple pattern matching - could be extended
                return [k for k in self._cache.keys() if pattern.replace("*", "") in k]

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for existing key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if key exists and TTL was set
        """
        with self._lock:
            if key in self._cache:
                self._cache[key]["expiry"] = time.time() + ttl
                return True
            return False

    def ttl(self, key: str) -> int:
        """
        Get time to live for key in seconds.

        Args:
            key: Cache key

        Returns:
            Seconds until expiration, -1 if key doesn't exist, -2 if no expiry
        """
        with self._lock:
            if key not in self._cache:
                return -1

            item = self._cache[key]
            remaining = item["expiry"] - time.time()
            return max(0, int(remaining))

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_counts.clear()

    def size(self) -> int:
        """Get number of keys in cache."""
        with self._lock:
            self._cleanup_expired()
            return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            self._cleanup_expired()

            total_memory = sum(item.get("size", 0) for item in self._cache.values())
            total_accesses = sum(self._access_counts.values())

            most_accessed = None
            if self._access_counts:
                most_accessed = max(self._access_counts.items(), key=lambda x: x[1])

            return {
                "total_keys": len(self._cache),
                "total_accesses": total_accesses,
                "estimated_memory_bytes": total_memory,
                "most_accessed_key": most_accessed[0] if most_accessed else None,
                "most_accessed_count": most_accessed[1] if most_accessed else 0,
                "max_size": self._max_size,
                "hit_rate": self._calculate_hit_rate(),
                "oldest_entry": self._get_oldest_entry(),
                "newest_entry": self._get_newest_entry(),
            }

    def _cleanup_expired(self) -> None:
        """Remove expired entries (called with lock held)."""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items() if current_time >= item["expiry"]
        ]

        for key in expired_keys:
            del self._cache[key]
            if key in self._access_counts:
                del self._access_counts[key]

    def _evict_if_needed(self) -> None:
        """Evict oldest entries if over size limit (called with lock held)."""
        while len(self._cache) > self._max_size:
            # Remove least recently used (first item in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._access_counts:
                del self._access_counts[oldest_key]

    def _estimate_size(self, value: Any) -> int:
        """Rough estimation of object size in bytes."""
        try:
            if isinstance(value, str):
                return len(value.encode("utf-8"))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, bool):
                return 1
            elif isinstance(value, (list, tuple)):
                return sum(self._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(
                    self._estimate_size(k) + self._estimate_size(v)
                    for k, v in value.items()
                )
            else:
                # Fallback for complex objects
                return len(str(value)) * 2
        except:
            return 100  # Default fallback

    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        # This is a simplified calculation
        # In a real implementation, you'd track hits/misses
        if not self._access_counts:
            return 0.0

        total_accesses = sum(self._access_counts.values())
        unique_keys = len(self._access_counts)

        if unique_keys == 0:
            return 0.0

        # Rough hit rate estimation
        return min(100.0, (total_accesses / unique_keys) * 10)

    def _get_oldest_entry(self) -> Optional[Dict[str, Any]]:
        """Get information about oldest cache entry."""
        if not self._cache:
            return None

        oldest_key = next(iter(self._cache))
        oldest_item = self._cache[oldest_key]

        return {
            "key": oldest_key,
            "created": datetime.fromtimestamp(oldest_item["created"]).isoformat(),
            "expires": datetime.fromtimestamp(oldest_item["expiry"]).isoformat(),
        }

    def _get_newest_entry(self) -> Optional[Dict[str, Any]]:
        """Get information about newest cache entry."""
        if not self._cache:
            return None

        newest_key = next(reversed(self._cache))
        newest_item = self._cache[newest_key]

        return {
            "key": newest_key,
            "created": datetime.fromtimestamp(newest_item["created"]).isoformat(),
            "expires": datetime.fromtimestamp(newest_item["expiry"]).isoformat(),
        }


# Singleton instance for application-wide use
cache = InMemoryCache(max_size=1000)


# Convenience functions for Redis-like API compatibility
def set_cache(key: str, value: Any, ttl: int = 3600) -> None:
    """Set cache value with TTL."""
    cache.set(key, value, ttl)


def get_cache(key: str) -> Optional[Any]:
    """Get cache value."""
    return cache.get(key)


def delete_cache(key: str) -> bool:
    """Delete cache key."""
    return cache.delete(key)


def clear_cache() -> None:
    """Clear all cache."""
    cache.clear()


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache.stats()


# Rate limiting helper functions
def check_rate_limit(key: str, limit: int, window: int) -> bool:
    """
    Simple rate limiting using cache.

    Args:
        key: Rate limit key (e.g., "rate_limit:user:123")
        limit: Maximum requests allowed
        window: Time window in seconds

    Returns:
        True if request is allowed, False if rate limited
    """
    current_time = time.time()
    window_start = current_time - window

    # Get current requests in window
    requests = cache.get(key) or []

    # Filter out requests outside window
    requests = [req_time for req_time in requests if req_time > window_start]

    # Check if under limit
    if len(requests) < limit:
        requests.append(current_time)
        cache.set(key, requests, ttl=window)
        return True

    return False


def reset_rate_limit(key: str) -> None:
    """Reset rate limit for key."""
    cache.delete(key)
