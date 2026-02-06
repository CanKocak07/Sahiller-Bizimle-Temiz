from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


_TR_TZ = ZoneInfo("Europe/Istanbul")


def tr_today(now_utc: datetime | None = None) -> date:
    now = now_utc.astimezone(_TR_TZ) if now_utc else datetime.now(_TR_TZ)
    return now.date()


def next_tr_midnight_utc(now_utc: datetime | None = None) -> datetime:
    now = now_utc.astimezone(timezone.utc) if now_utc else datetime.now(timezone.utc)
    now_tr = now.astimezone(_TR_TZ)
    tomorrow_tr = (now_tr.date() + timedelta(days=1))
    midnight_tr = datetime.combine(tomorrow_tr, time(0, 0, 0), tzinfo=_TR_TZ)
    return midnight_tr.astimezone(timezone.utc)


@dataclass(frozen=True)
class RefreshWindow:
    timezone: str
    snapshot_date: str  # YYYY-MM-DD (TR)
    next_refresh_at: str  # ISO UTC


def current_refresh_window(now_utc: datetime | None = None) -> RefreshWindow:
    today = tr_today(now_utc)
    next_midnight = next_tr_midnight_utc(now_utc)
    return RefreshWindow(
        timezone="Europe/Istanbul",
        snapshot_date=today.isoformat(),
        next_refresh_at=next_midnight.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    )
