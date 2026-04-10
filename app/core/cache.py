# app/core/cache.py
"""
Transparent Redis cache layer.

Falls back silently to passthrough mode if Redis is unavailable or not configured.
Consumer code never changes — cache presence is an infrastructure detail.

Usage:
    from app.core.cache import cache

    data = cache.get("home:8:4:4")
    if data is None:
        data = compute_expensive_thing()
        cache.set("home:8:4:4", data, ttl=120)

    cache.delete("home:8:4:4")
    cache.delete_pattern("home:*")
"""
import json
import logging
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class _CacheManager:
    """
    Singleton cache manager backed by Redis.
    Initialises lazily on first use; disables itself permanently on connection failure.
    All public methods are safe to call regardless of Redis availability.
    """

    def __init__(self) -> None:
        self._client = None
        self._available: Optional[bool] = None  # None = not yet tried

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_client(self):
        if self._available is False:
            return None

        if self._client is not None:
            return self._client

        if not settings.REDIS_URL:
            self._available = False
            logger.info("Cache layer disabled (REDIS_URL not configured)")
            return None

        try:
            import redis

            client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=0.5,
                socket_connect_timeout=0.5,
            )
            client.ping()
            self._client = client
            self._available = True
            logger.info("Cache layer connected (Redis)")
            return client

        except ImportError:
            self._available = False
            logger.warning("redis package not installed — cache disabled")
            return None

        except Exception as exc:
            self._available = False
            logger.warning("Cache layer unavailable — operating in passthrough mode (%s)", exc)
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        client = self._get_client()
        if client is None:
            return None
        try:
            raw = client.get(key)
            return json.loads(raw) if raw is not None else None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass

    def delete(self, key: str) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            client.delete(key)
        except Exception:
            pass

    def delete_pattern(self, pattern: str) -> None:
        """Remove all keys matching a glob pattern (e.g. 'home:*')."""
        client = self._get_client()
        if client is None:
            return
        try:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
        except Exception:
            pass

    def is_healthy(self) -> bool:
        client = self._get_client()
        if client is None:
            return False
        try:
            return bool(client.ping())
        except Exception:
            return False


# Module-level singleton — import this everywhere
cache = _CacheManager()
