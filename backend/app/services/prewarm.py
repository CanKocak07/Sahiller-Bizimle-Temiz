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
        try:
            # Give the server a brief moment after startup/reload.
            await asyncio.sleep(0.5)

            # Prewarm for current window immediately.
            await prewarm_once(days=days)

            # Then sleep until next even-hour boundary and repeat.
            next_boundary = _next_even_hour_boundary()
            await asyncio.sleep(_sleep_seconds_until(next_boundary) + 0.05)
        except asyncio.CancelledError:
            # Graceful shutdown.
            raise
        except Exception:
            # Don't let background loop die.
            await asyncio.sleep(1.0)


async def prewarm_once(days: int = 7) -> None:
    window_start, window_end = current_window()

    for beach_id in BEACHES.keys():
        try:
            # Earth Engine calls are blocking; run them in a worker thread so we
            # don't block the asyncio loop (which would cause proxy connect timeouts).
            value = await asyncio.to_thread(get_beach_summary, beach_id=beach_id, days=days)
            entry = CacheEntry(
                value=value,
                window_start=window_start,
                window_end=window_end,
                generated_at=datetime.now(),
            )
            key = make_key("beach-summary", beach_id=beach_id, days=days, window_start=window_start)
            cache_set(key, entry)
            # Small yield to keep event loop responsive even if thread returns quickly.
            await asyncio.sleep(0)
        except Exception:
            # If one beach fails (no data / transient EE issue), don't stop the loop.
            continue
