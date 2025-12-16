from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, Optional, Tuple


def _floor_to_even_hour(dt: datetime) -> datetime:
    # Align to the most recent even hour boundary in local server time.
    hour = dt.hour - (dt.hour % 2)
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0)


def _next_even_hour(dt: datetime) -> datetime:
    start = _floor_to_even_hour(dt)
    if start == dt.replace(minute=0, second=0, microsecond=0) and dt.hour % 2 == 0:
        # Already exactly on an even hour boundary.
        return start + timedelta(hours=2)
    return start + timedelta(hours=2)


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
    now = now or datetime.now()
    start = _floor_to_even_hour(now)
    end = start + timedelta(hours=2)
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
