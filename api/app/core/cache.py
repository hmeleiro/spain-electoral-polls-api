from collections import OrderedDict
from collections.abc import Callable, Hashable
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
from threading import RLock
from time import monotonic
from typing import Any

from app.core.config import get_settings

CacheKey = tuple[str, tuple[tuple[str, Hashable], ...]]
MISSING = object()


@dataclass
class CacheEntry:
    expires_at: float
    value: Any


class TTLCache:
    def __init__(self, *, ttl_seconds: int, max_entries: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: OrderedDict[CacheKey, CacheEntry] = OrderedDict()
        self._lock = RLock()

    def get(self, key: CacheKey) -> Any:
        now = monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return MISSING
            if entry.expires_at <= now:
                self._entries.pop(key, None)
                return MISSING
            self._entries.move_to_end(key)
            return deepcopy(entry.value)

    def set(self, key: CacheKey, value: Any) -> None:
        if self.max_entries <= 0 or self.ttl_seconds <= 0:
            return
        entry = CacheEntry(expires_at=monotonic() + self.ttl_seconds, value=deepcopy(value))
        with self._lock:
            self._entries[key] = entry
            self._entries.move_to_end(key)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


def _normalize_value(value: Any) -> Hashable:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list | tuple | set | frozenset):
        return tuple(sorted({_normalize_value(item) for item in value}))
    if isinstance(value, dict):
        return tuple(sorted((str(key), _normalize_value(item)) for key, item in value.items()))
    return value


def make_cache_key(namespace: str, filters: dict[str, Any]) -> CacheKey:
    normalized_filters = tuple(sorted((key, _normalize_value(value)) for key, value in filters.items()))
    return namespace, normalized_filters


settings = get_settings()
response_cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds, max_entries=settings.cache_max_entries)


def clear_response_cache() -> None:
    response_cache.clear()


def cached_call[T](namespace: str, filters: dict[str, Any], loader: Callable[[], T]) -> T:
    if not get_settings().cache_enabled:
        return loader()

    key = make_cache_key(namespace, filters)
    cached_value = response_cache.get(key)
    if cached_value is not MISSING:
        return cached_value

    value = loader()
    response_cache.set(key, value)
    return deepcopy(value)
