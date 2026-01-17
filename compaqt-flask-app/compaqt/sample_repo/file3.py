"""
Cache management module.

Provides an in-memory caching system with TTL support,
LRU eviction policy, and cache statistics tracking.
"""

import time
import threading
from typing import Any, Optional, Dict, Callable, TypeVar
from collections import OrderedDict
from dataclasses import dataclass


# Type variable for generic cache values
T = TypeVar('T')

# Default cache settings
DEFAULT_MAX_SIZE = 1000
DEFAULT_TTL = 300  # 5 minutes


@dataclass
class CacheEntry:
    """
    Represents a single cache entry.
    
    Attributes:
        key: Cache key
        value: Cached value
        created_at: Timestamp when entry was created
        expires_at: Timestamp when entry expires
        access_count: Number of times entry was accessed
    """
    key: str
    value: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return time.time() > self.expires_at
    
    def touch(self) -> None:
        """Update access count and timestamp."""
        self.access_count += 1


@dataclass
class CacheStats:
    """
    Cache statistics container.
    """
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expired": self.expired,
            "hit_rate": round(self.hit_rate * 100, 2)
        }


class LRUCache:
    """
    Thread-safe LRU cache with TTL support.
    
    This cache implementation uses an OrderedDict for
    O(1) access and LRU eviction. It supports:
    - Time-to-live (TTL) for entries
    - Maximum size limit with LRU eviction
    - Thread-safe operations
    - Statistics tracking
    """
    
    def __init__(
        self,
        max_size: int = DEFAULT_MAX_SIZE,
        default_ttl: int = DEFAULT_TTL
    ):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.misses += 1
                return None
            
            # Check expiration
            if entry.is_expired():
                self._remove(key)
                self._stats.expired += 1
                self._stats.misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._stats.hits += 1
            
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override
        """
        ttl = ttl if ttl is not None else self._default_ttl
        
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]
            
            # Evict if necessary
            while len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            # Create new entry
            now = time.time()
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=now + ttl
            )
            
            self._cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """
        Delete an entry from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if entry was found and deleted
        """
        with self._lock:
            return self._remove(key)
    
    def _remove(self, key: str) -> bool:
        """Internal method to remove an entry."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def _evict_oldest(self) -> None:
        """Evict the least recently used entry."""
        if self._cache:
            # First item is the oldest
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats.evictions += 1
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
    
    def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        """
        Get a value or compute and cache it if missing.
        
        Args:
            key: Cache key
            factory: Function to compute value if missing
            ttl: Optional TTL override
            
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        
        if value is not None:
            return value
        
        # Compute new value
        value = factory()
        self.set(key, value, ttl)
        
        return value
    
    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
    
    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove(key)
                self._stats.expired += 1
                removed += 1
        
        return removed
