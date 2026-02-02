from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import os

from app.data.beaches import BEACHES
from app.services.air_quality import get_air_quality_for_beach_in_range
from app.services.chlorophyll import get_chlorophyll_for_beach_in_range
from app.services.oisst import get_sst_for_beach_in_range
from app.services.turbidity import get_turbidity_for_beach_in_range
from app.services.wqi import calculate_wqi_from_components


def _day_window(d: date) -> tuple[str, str]:
    start = d.isoformat()
    end = (d + timedelta(days=1)).isoformat()
    return start, end


def _mean(values: List[Optional[float]]) -> Optional[float]:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


_LOOKBACK_DAYS = int(os.getenv("IMPUTE_LOOKBACK_DAYS", "5"))
_IMPUTE_ENABLED = os.getenv("IMPUTE_MISSING_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}


def _impute_with_lookback(current: Optional[float], prev_values: List[Optional[float]]) -> Optional[float]:
    if current is not None:
        return current
    if not _IMPUTE_ENABLED:
        return None
    lookback = [v for v in prev_values[-_LOOKBACK_DAYS:] if v is not None]
    if not lookback:
        return None
    return sum(lookback) / len(lookback)


def _range_start_for_lookback(day_start: str) -> str:
    # day_start is YYYY-MM-DD
    d = date.fromisoformat(day_start)
    return (d - timedelta(days=_LOOKBACK_DAYS - 1)).isoformat()


def get_beach_summary(beach_id: str, days: int = 7) -> Dict[str, Any]:
    if beach_id not in BEACHES:
        raise ValueError("Beach not found")

    if days < 1:
        raise ValueError("days must be >= 1")

    beach = BEACHES[beach_id]

    end_day = date.today()
    # Compute an extended window so each requested day can fall back to the
    # previous N days (default 5) even when the requested range starts recently.
    extended_days = days + (_LOOKBACK_DAYS if _IMPUTE_ENABLED else 0)
    start_day = end_day - timedelta(days=extended_days - 1)

    extended: List[Dict[str, Any]] = []

    # Keep rolling filled values for base metrics.
    filled_sst: List[Optional[float]] = []
    filled_turb: List[Optional[float]] = []
    filled_chl: List[Optional[float]] = []
    filled_no2: List[Optional[float]] = []

    for i in range(extended_days):
        d = start_day + timedelta(days=i)
        start_date, end_date = _day_window(d)

        lookback_start_date = _range_start_for_lookback(start_date) if _IMPUTE_ENABLED else start_date

        raw_sst = get_sst_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        raw_chl = get_chlorophyll_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)

        # Turbidity/NO2 are more likely to have daily gaps; if missing, try a
        # 5-day window ending on this day (matches "last 5 days average" ask).
        raw_turb = get_turbidity_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        if raw_turb is None and _IMPUTE_ENABLED:
            raw_turb = get_turbidity_for_beach_in_range(beach_id, start_date=lookback_start_date, end_date=end_date)

        air = get_air_quality_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        raw_no2 = air.get("no2")
        if raw_no2 is None and _IMPUTE_ENABLED:
            air5 = get_air_quality_for_beach_in_range(beach_id, start_date=lookback_start_date, end_date=end_date)
            raw_no2 = air5.get("no2")

        sst = _impute_with_lookback(raw_sst, filled_sst)
        turb = _impute_with_lookback(raw_turb, filled_turb)
        chl = _impute_with_lookback(raw_chl, filled_chl)
        no2 = _impute_with_lookback(raw_no2, filled_no2)

        filled_sst.append(sst)
        filled_turb.append(turb)
        filled_chl.append(chl)
        filled_no2.append(no2)

        # Derived metrics are computed from filled base metrics.
        air_quality = air.get("air_quality")
        if no2 is not None:
            air_quality = air.get("air_quality") or "unknown"
            # Re-classify using the filled no2 value for consistency.
            try:
                from app.services.air_quality import classify_no2  # local import to avoid cycles at import time

                air_quality = classify_no2(no2)
            except Exception:
                pass

        try:
            wqi_obj = calculate_wqi_from_components(sst=sst, chl=chl, turb=turb)
            wqi = wqi_obj.get("wqi")
        except Exception:
            wqi = None

        extended.append(
            {
                "date": d.isoformat(),
                "sst_celsius": None if sst is None else round(float(sst), 2),
                "turbidity_ndti": None if turb is None else round(float(turb), 4),
                "chlorophyll": None if chl is None else round(float(chl), 4),
                "no2_mol_m2": None if no2 is None else float(no2),
                "air_quality": air_quality,
                "wqi": None if wqi is None else float(wqi),
            }
        )

    # Keep only the requested range (last N days).
    series: List[Dict[str, Any]] = extended[-days:]

    averages = {
        "sst_celsius": (lambda v: None if v is None else round(v, 2))(_mean([r["sst_celsius"] for r in series])),
        "turbidity_ndti": (lambda v: None if v is None else round(v, 4))(_mean([r["turbidity_ndti"] for r in series])),
        "chlorophyll": (lambda v: None if v is None else round(v, 4))(_mean([r["chlorophyll"] for r in series])),
        "no2_mol_m2": _mean([r["no2_mol_m2"] for r in series]),
        "wqi": (lambda v: None if v is None else round(v, 1))(_mean([r["wqi"] for r in series])),
    }

    return {
        "beach": {
            "id": beach_id,
            "name": beach["name"],
            "lat": beach.get("lat"),
            "lon": beach.get("lon"),
        },
        "days": days,
        "series": series,
        "averages": averages,
    }
