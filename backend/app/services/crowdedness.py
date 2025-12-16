from datetime import datetime
from typing import Optional

def _sst_factor(sst_celsius: Optional[float]) -> float:
    if sst_celsius is None:
        return 1.0  # veri yoksa etkileme

    if sst_celsius >= 24:
        return 1.0
    elif 20 <= sst_celsius < 24:
        return 0.9
    elif 16 <= sst_celsius < 20:
        return 0.75
    else:
        return 0.5

def _base_by_hour(hour: int) -> float:
    if 6 <= hour < 10:
        return 0.30
    elif 10 <= hour < 14:
        return 0.60
    elif 14 <= hour < 19:
        return 0.90
    elif 19 <= hour < 22:
        return 0.50
    else:
        return 0.10


def _day_factor(weekday: int) -> float:
    # 0 = Monday, 6 = Sunday
    if weekday >= 5:
        return 1.2  # weekend
    return 0.8      # weekday


def _season_factor(month: int) -> float:
    if month in [6, 7, 8]:
        return 1.2  # summer
    elif month in [12, 1, 2]:
        return 0.6  # winter
    return 0.9      # spring / autumn


def get_crowdedness_percent(
    now: Optional[datetime] = None,
    sst_celsius: Optional[float] = None
) -> float:
    if now is None:
        now = datetime.now()

    base = _base_by_hour(now.hour)
    base *= _day_factor(now.weekday())
    base *= _season_factor(now.month)
    base *= _sst_factor(sst_celsius)

    base = max(0.0, min(1.0, base))
    return round(base * 100, 1)
