from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from threading import Lock
from typing import Any, Dict, Optional, Tuple


_DEFAULT_WINDOW_DAYS = 5
_EPOCH = datetime(1970, 1, 1)


def _window_days() -> int:
    """Cache window size in days.

    Defaults to 5 days to reduce Earth Engine load. Can be overridden via
    CACHE_WINDOW_DAYS.
    """

    raw = os.getenv("CACHE_WINDOW_DAYS", str(_DEFAULT_WINDOW_DAYS)).strip()
    try:
        return max(1, int(raw))
    except Exception:
        return _DEFAULT_WINDOW_DAYS


def _floor_to_window_start(dt: datetime) -> datetime:
    """Align to the start of the current N-day window.

    Uses UTC wall-clock (naive datetime treated as UTC) to avoid DST edge cases.
    """

    window_days = _window_days()
    total_days = (dt - _EPOCH).days
    start_days = total_days - (total_days % window_days)
    start = _EPOCH + timedelta(days=start_days)
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


@dataclass
class CacheEntry:
    value: Any
    window_start: datetime
    window_end: datetime
    generated_at: datetime


_cache: Dict[str, CacheEntry] = {}
_lock = Lock()


def make_key(prefix: str, beach_id: str, days: int, window_start: datetime) -> str:
    return f"{prefix}:{beach_id}:{days}:{window_start.isoformat()}"


def current_window(now: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    now = now or datetime.utcnow()
    start = _floor_to_window_start(now)
    end = start + timedelta(days=_window_days())
    return start, end


def get(key: str, window_start: datetime) -> Optional[CacheEntry]:
    with _lock:
        entry = _cache.get(key)
        if not entry:
            return None
        if entry.window_start != window_start:
            return None
        return entry


def set(key: str, entry: CacheEntry) -> None:
    with _lock:
        _cache[key] = entry


def clear() -> None:
    with _lock:
        _cache.clear()
