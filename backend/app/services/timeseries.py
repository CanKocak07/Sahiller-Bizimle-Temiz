from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import os

from app.data.beaches import BEACHES
from app.services.air_quality import get_air_quality_for_beach_in_range
from app.services.chlorophyll import get_chlorophyll_for_beach_in_range
from app.services.oisst import get_sst_for_beach_in_range
from app.services.turbidity import get_turbidity_for_beach_in_range
from app.services.waste_risk import get_waste_risk_for_beach_in_range
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


def get_beach_summary(beach_id: str, days: int = 7, end_day: Optional[date] = None) -> Dict[str, Any]:
    if beach_id not in BEACHES:
        raise ValueError("Beach not found")

    if days < 1:
        raise ValueError("days must be >= 1")

    beach = BEACHES[beach_id]

    # Anchor the time series to a specific day (defaults to local machine day).
    # This enables stable daily snapshots (e.g., "as-of TR midnight") regardless of
    # process restarts.
    end_day = end_day or date.today()
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
    filled_waste_risk: List[Optional[float]] = []

    for i in range(extended_days):
        d = start_day + timedelta(days=i)
        start_date, end_date = _day_window(d)

        lookback_start_date = _range_start_for_lookback(start_date) if _IMPUTE_ENABLED else start_date

        raw_sst = get_sst_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        raw_chl = get_chlorophyll_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)

        sst_source = "daily" if raw_sst is not None else None
        chl_source = "daily" if raw_chl is not None else None

        # Turbidity/NO2 are more likely to have daily gaps; if missing, try a
        # 5-day window ending on this day (matches "last 5 days average" ask).
        raw_turb = get_turbidity_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        turb_source = "daily" if raw_turb is not None else None
        if raw_turb is None and _IMPUTE_ENABLED:
            raw_turb = get_turbidity_for_beach_in_range(beach_id, start_date=lookback_start_date, end_date=end_date)
            if raw_turb is not None:
                turb_source = "window_avg"

        # Waste risk is derived from Sentinel-2 (and optional Landsat fallback); daily gaps are expected.
        raw_waste_obj = get_waste_risk_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        raw_waste = None if raw_waste_obj is None else raw_waste_obj.get("waste_risk_percent")
        waste_source = "daily" if raw_waste is not None else None
        if raw_waste is None and _IMPUTE_ENABLED:
            raw_waste_obj = get_waste_risk_for_beach_in_range(beach_id, start_date=lookback_start_date, end_date=end_date)
            raw_waste = None if raw_waste_obj is None else raw_waste_obj.get("waste_risk_percent")
            if raw_waste is not None:
                waste_source = "window_avg"

        air = get_air_quality_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        raw_no2 = air.get("no2")
        no2_source = "daily" if raw_no2 is not None else None
        if raw_no2 is None and _IMPUTE_ENABLED:
            air5 = get_air_quality_for_beach_in_range(beach_id, start_date=lookback_start_date, end_date=end_date)
            raw_no2 = air5.get("no2")
            if raw_no2 is not None:
                no2_source = "window_avg"

        sst = _impute_with_lookback(raw_sst, filled_sst)
        turb = _impute_with_lookback(raw_turb, filled_turb)
        chl = _impute_with_lookback(raw_chl, filled_chl)
        no2 = _impute_with_lookback(raw_no2, filled_no2)
        waste_risk = _impute_with_lookback(raw_waste, filled_waste_risk)

        # If we ended up filling a missing daily/window value, mark it as imputed.
        if sst_source is None and sst is not None:
            sst_source = "imputed"
        if chl_source is None and chl is not None:
            chl_source = "imputed"
        if turb_source is None and turb is not None:
            turb_source = "imputed"
        if no2_source is None and no2 is not None:
            no2_source = "imputed"
        if waste_source is None and waste_risk is not None:
            waste_source = "imputed"

        sst_source = sst_source or "missing"
        chl_source = chl_source or "missing"
        turb_source = turb_source or "missing"
        no2_source = no2_source or "missing"
        waste_source = waste_source or "missing"

        filled_sst.append(sst)
        filled_turb.append(turb)
        filled_chl.append(chl)
        filled_no2.append(no2)
        filled_waste_risk.append(waste_risk)

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

        # WQI quality follows the least reliable component.
        def _rank(src: str) -> int:
            return {"missing": 0, "imputed": 1, "window_avg": 2, "daily": 3}.get(src, 0)

        wqi_source = "missing"
        if wqi is not None:
            min_rank = min(_rank(sst_source), _rank(chl_source), _rank(turb_source))
            wqi_source = {3: "daily", 2: "window_avg", 1: "imputed", 0: "missing"}.get(min_rank, "missing")

        extended.append(
            {
                "date": d.isoformat(),
                "sst_celsius": None if sst is None else round(float(sst), 2),
                "turbidity_ndti": None if turb is None else round(float(turb), 4),
                "chlorophyll": None if chl is None else round(float(chl), 4),
                "no2_mol_m2": None if no2 is None else float(no2),
                "air_quality": air_quality,
                "wqi": None if wqi is None else float(wqi),
                "waste_risk_percent": None if waste_risk is None else float(waste_risk),
                "sources": {
                    "sst_celsius": sst_source,
                    "turbidity_ndti": turb_source,
                    "chlorophyll": chl_source,
                    "no2_mol_m2": no2_source,
                    "air_quality": no2_source,
                    "waste_risk_percent": waste_source,
                    "wqi": wqi_source,
                },
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
        "waste_risk_percent": (lambda v: None if v is None else round(v, 1))(_mean([r["waste_risk_percent"] for r in series])),
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
