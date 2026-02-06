from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

from app.services.daily_refresh import refresh_all
from app.services.tr_time import next_tr_midnight_utc, tr_today


def _loop_enabled() -> bool:
    return os.getenv("DAILY_REFRESH_LOOP_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


async def daily_refresh_loop(days: int = 7, revise_days: int = 5) -> None:
    """Best-effort background loop.

    Note: Cloud Run instances can scale to zero; for guaranteed execution use
    Cloud Scheduler calling the admin refresh endpoint.
    """

    if not _loop_enabled():
        return

    while True:
        try:
            # Small delay after startup.
            await asyncio.sleep(0.5)

            # Refresh immediately once.
            refresh_all(as_of_day=tr_today(), days=days, revise_days=revise_days)

            # Sleep until next TR midnight.
            next_midnight = next_tr_midnight_utc(datetime.now(timezone.utc))
            sleep_s = max(0.0, (next_midnight - datetime.now(timezone.utc)).total_seconds())
            await asyncio.sleep(sleep_s + 0.25)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(2.0)
