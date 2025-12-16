from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from app.data.beaches import BEACHES
from app.services.summary_cache import CacheEntry, current_window, make_key, set as cache_set
from app.services.timeseries import get_beach_summary


def _sleep_seconds_until(target: datetime) -> float:
    now = datetime.now()
    delta = (target - now).total_seconds()
    return max(0.0, delta)


def _next_even_hour_boundary(now: Optional[datetime] = None) -> datetime:
    now = now or datetime.now()
    # Next boundary is the end of current 2-hour window.
    start, end = current_window(now)
    if end <= now:
        return end + timedelta(hours=2)
    return end


async def prewarm_loop(days: int = 7) -> None:
    # Run forever.
    while True:
        # Prewarm for current window immediately
        await prewarm_once(days=days)

        # Then sleep until next even-hour boundary and repeat.
        next_boundary = _next_even_hour_boundary()
        await asyncio.sleep(_sleep_seconds_until(next_boundary) + 0.05)


async def prewarm_once(days: int = 7) -> None:
    window_start, window_end = current_window()

    for beach_id in BEACHES.keys():
        try:
            value = get_beach_summary(beach_id=beach_id, days=days)
            entry = CacheEntry(
                value=value,
                window_start=window_start,
                window_end=window_end,
                generated_at=datetime.now(),
            )
            key = make_key("beach-summary", beach_id=beach_id, days=days, window_start=window_start)
            cache_set(key, entry)
        except Exception:
            # If one beach fails (no data / transient EE issue), don't stop the loop.
            continue
