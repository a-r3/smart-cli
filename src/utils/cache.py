"""Legacy cache compatibility layer for older tests."""

from __future__ import annotations

import hashlib
import json
import pickle
import sqlite3
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import redis
except ImportError:  # pragma: no cover - optional dependency
    redis = None

from .config import ConfigManager

REAL_DATETIME = datetime


class _AwaitableValue:
    """Value wrapper that can be used synchronously or awaited."""

    def __init__(self, value: Any):
        self.value = value

    def __await__(self):
        async def _coro():
            return self.value

        return _coro().__await__()

    def __eq__(self, other: Any) -> bool:
        return self.value == other

    def __bool__(self) -> bool:
        return bool(self.value)

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass
class _MemoryEntry:
    value: Any
    expires_at: Optional[datetime]


class MemoryCache:
    """Simple in-memory cache with TTL and LRU behavior."""

    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, _MemoryEntry] = {}
        self.access_order: OrderedDict[str, None] = OrderedDict()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a cache entry."""
        expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        self.cache[key] = _MemoryEntry(value=value, expires_at=expires_at)
        self._touch(key)
        self._evict_if_needed()

    def get(self, key: str) -> Any:
        """Retrieve a cache entry."""
        entry = self.cache.get(key)
        if not entry:
            return None
        if entry.expires_at and datetime.now() > entry.expires_at:
            self.delete(key)
            return None
        self._touch(key)
        return entry.value

    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        existed = key in self.cache
        self.cache.pop(key, None)
        self.access_order.pop(key, None)
        return existed

    def clear(self) -> None:
        """Clear all entries."""
        self.cache.clear()
        self.access_order.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Return memory cache statistics."""
        expired_entries = sum(
            1
            for entry in self.cache.values()
            if entry.expires_at and datetime.now() > entry.expires_at
        )
        return {
            "total_entries": len(self.cache),
            "max_size": self.max_size,
            "usage_percentage": (len(self.cache) / self.max_size * 100)
            if self.max_size
            else 0.0,
            "memory_usage_estimate": sum(
                len(repr(entry.value)) for entry in self.cache.values()
            ),
            "expired_entries": expired_entries,
        }

    def _touch(self, key: str) -> None:
        self.access_order.pop(key, None)
        self.access_order[key] = None

    def _evict_if_needed(self) -> None:
        while len(self.cache) > self.max_size:
            lru_key, _ = self.access_order.popitem(last=False)
            self.cache.pop(lru_key, None)


class SQLiteCache:
    """SQLite-backed cache for larger or persistent entries."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    expires_at TEXT,
                    access_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a serialized cache value."""
        try:
            serialized = pickle.dumps(value)
        except Exception:
            return

        expires_at = (
            (datetime.now() + timedelta(seconds=ttl)).isoformat()
            if ttl
            else (datetime.now() + timedelta(days=365)).isoformat()
        )
        now = datetime.now().isoformat()
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO cache(key, value, expires_at, access_count, created_at, updated_at)
                VALUES (?, ?, ?, 0, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at
                """,
                (key, serialized, expires_at, now, now),
            )

    def get(self, key: str) -> Any:
        """Retrieve and deserialize a cached value."""
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT value, expires_at, access_count FROM cache WHERE key = ?",
                (key,),
            ).fetchone()
            if not row:
                return None

            value_blob, expires_at, access_count = row
            if expires_at and datetime.now() > REAL_DATETIME.fromisoformat(expires_at):
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None

            conn.execute(
                "UPDATE cache SET access_count = ?, updated_at = ? WHERE key = ?",
                (access_count + 1, datetime.now().isoformat(), key),
            )

        try:
            return pickle.loads(value_blob)
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        """Delete a value by key."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            return cursor.rowcount > 0

    def clear_expired(self) -> int:
        """Delete expired entries and return the number cleared."""
        now = datetime.now().isoformat()
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now,),
            )
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """Return SQLite cache statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            total_entries = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            total_size = conn.execute(
                "SELECT COALESCE(SUM(LENGTH(value)), 0) FROM cache"
            ).fetchone()[0]
            average_access = conn.execute(
                "SELECT COALESCE(AVG(access_count), 0) FROM cache"
            ).fetchone()[0]
            expired_entries = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (datetime.now().isoformat(),),
            ).fetchone()[0]
            top_accessed = conn.execute(
                "SELECT key, access_count FROM cache ORDER BY access_count DESC LIMIT 5"
            ).fetchall()

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "average_access_count": average_access,
            "expired_entries": expired_entries,
            "top_accessed_keys": top_accessed,
        }


class FastSQLiteCache:
    """In-memory SQLite-compatible fallback used for fast default paths."""

    def __init__(self):
        self._store: Dict[str, _MemoryEntry] = {}

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        try:
            pickle.dumps(value)
        except Exception:
            return
        expires_at = datetime.now() + timedelta(seconds=ttl or 365 * 24 * 3600)
        self._store[key] = _MemoryEntry(value=value, expires_at=expires_at)

    def get(self, key: str) -> Any:
        entry = self._store.get(key)
        if not entry:
            return None
        if entry.expires_at and datetime.now() > entry.expires_at:
            self.delete(key)
            return None
        return entry.value

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear_expired(self) -> int:
        expired_keys = [
            key
            for key, entry in self._store.items()
            if entry.expires_at and datetime.now() > entry.expires_at
        ]
        for key in expired_keys:
            self._store.pop(key, None)
        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        total_size = sum(len(repr(entry.value)) for entry in self._store.values())
        return {
            "total_entries": len(self._store),
            "total_size_bytes": total_size,
            "average_access_count": 0,
            "expired_entries": 0,
            "top_accessed_keys": [],
        }


class HybridCache:
    """Hybrid cache with memory, SQLite, and optional Redis layers."""

    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
        self.memory_cache = MemoryCache(
            max_size=self.config.get_config("memory_cache_size", 10000),
            default_ttl=self.config.get_config("cache_ttl", 3600),
        )
        self.sqlite_cache: Optional[SQLiteCache | FastSQLiteCache] = None
        if self.config.get_config("persistent_cache_enabled", False):
            cache_dir = Path(tempfile.gettempdir()) / "smart_cli_cache"
            self.sqlite_cache = SQLiteCache(cache_dir / "hybrid_cache.db")
        else:
            self.sqlite_cache = FastSQLiteCache()
        self.redis_client = self._initialize_redis()

    def _initialize_redis(self):  # pragma: no cover - exercised via mocks
        redis_url = self.config.get_config("redis_url")
        if not redis_url or redis is None:
            return None
        try:
            client = redis.from_url(redis_url)
            client.ping()
            return client
        except Exception:
            return None

    def _generate_cache_key(self, key: str, namespace: str = "default") -> str:
        """Build namespaced cache keys, hashing overly long ones."""
        raw_key = f"{namespace}:{key}"
        if len(raw_key) <= 250:
            return raw_key
        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return f"{namespace}:{digest}"

    def set(
        self, key: str, value: Any, namespace: str = "default", ttl: Optional[int] = None
    ) -> _AwaitableValue:
        """Set a value across cache layers."""
        namespaced_key = self._generate_cache_key(key, namespace)
        self.memory_cache.set(namespaced_key, value, ttl=ttl)
        if self.sqlite_cache:
            self.sqlite_cache.set(namespaced_key, value, ttl=ttl)
        if self.redis_client:
            try:  # pragma: no cover - exercised via mocks
                self.redis_client.setex(
                    namespaced_key,
                    ttl or self.memory_cache.default_ttl,
                    pickle.dumps(value),
                )
            except Exception:
                pass
        return _AwaitableValue(None)

    def get(self, key: str, namespace: str = "default") -> _AwaitableValue:
        """Get a value from the fastest available cache layer."""
        namespaced_key = self._generate_cache_key(key, namespace)

        memory_value = self.memory_cache.get(namespaced_key)
        if memory_value is not None:
            return _AwaitableValue(memory_value)

        if self.redis_client:
            try:  # pragma: no cover - exercised via mocks
                payload = self.redis_client.get(namespaced_key)
                if payload is not None:
                    value = pickle.loads(payload)
                    self.memory_cache.set(namespaced_key, value)
                    return _AwaitableValue(value)
            except Exception:
                pass

        if self.sqlite_cache:
            sqlite_value = self.sqlite_cache.get(namespaced_key)
            if sqlite_value is not None:
                self.memory_cache.set(namespaced_key, sqlite_value)
                return _AwaitableValue(sqlite_value)

        return _AwaitableValue(None)

    def delete(self, key: str, namespace: str = "default") -> _AwaitableValue:
        """Delete a value from all layers."""
        namespaced_key = self._generate_cache_key(key, namespace)
        deleted = self.memory_cache.delete(namespaced_key)
        if self.sqlite_cache:
            deleted = self.sqlite_cache.delete(namespaced_key) or deleted
        if self.redis_client:
            try:  # pragma: no cover - exercised via mocks
                deleted = bool(self.redis_client.delete(namespaced_key)) or deleted
            except Exception:
                pass
        return _AwaitableValue(deleted)

    def cleanup_expired_contexts(self) -> _AwaitableValue:
        """Clean up expired entries across layers."""
        sqlite_count = self.sqlite_cache.clear_expired() if self.sqlite_cache else 0
        redis_count = 0
        return _AwaitableValue({"sqlite": sqlite_count, "redis": redis_count})

    def get_stats(self) -> Dict[str, Any]:
        """Return per-layer cache statistics."""
        redis_stats = {"available": bool(self.redis_client)}
        if self.redis_client:
            try:  # pragma: no cover - exercised via mocks
                redis_stats.update(self.redis_client.info())
            except Exception:
                redis_stats["available"] = False

        return {
            "memory": self.memory_cache.get_stats(),
            "sqlite": self.sqlite_cache.get_stats() if self.sqlite_cache else {"enabled": False},
            "redis": redis_stats,
        }


def create_cache(config: Optional[ConfigManager] = None) -> HybridCache:
    """Factory for the compatibility cache."""
    return HybridCache(config=config)
