from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from app.data.beaches import BEACHES
from app.services.air_quality import get_air_quality_for_beach_in_range
from app.services.chlorophyll import get_chlorophyll_for_beach_in_range
from app.services.crowdedness import get_crowdedness_percent
from app.services.oisst import get_sst_for_beach_in_range
from app.services.pollution import calculate_pollution_from_turbidity
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


def get_beach_summary(beach_id: str, days: int = 7) -> Dict[str, Any]:
    if beach_id not in BEACHES:
        raise ValueError("Beach not found")

    if days < 1:
        raise ValueError("days must be >= 1")

    beach = BEACHES[beach_id]

    end_day = date.today()
    start_day = end_day - timedelta(days=days - 1)

    series: List[Dict[str, Any]] = []

    for i in range(days):
        d = start_day + timedelta(days=i)
        start_date, end_date = _day_window(d)

        sst = get_sst_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        turb = get_turbidity_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        chl = get_chlorophyll_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)

        air = get_air_quality_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
        no2 = air.get("no2")
        air_quality = air.get("air_quality")

        try:
            wqi_obj = calculate_wqi_from_components(sst=sst, chl=chl, turb=turb)
            wqi = wqi_obj.get("wqi")
        except Exception:
            wqi = None

        pollution_percent = calculate_pollution_from_turbidity(turb)

        # Represent a typical daytime crowdedness (14:00) for the given day.
        crowdedness_percent: Optional[float]
        if sst is None:
            crowdedness_percent = None
        else:
            crowdedness_percent = get_crowdedness_percent(
                now=datetime(d.year, d.month, d.day, 14, 0, 0),
                sst_celsius=sst,
            )

        series.append(
            {
                "date": d.isoformat(),
                "sst_celsius": None if sst is None else round(float(sst), 2),
                "turbidity_ndti": None if turb is None else round(float(turb), 4),
                "pollution_percent": None if pollution_percent is None else round(float(pollution_percent), 1),
                "chlorophyll": None if chl is None else round(float(chl), 4),
                "no2_mol_m2": None if no2 is None else float(no2),
                "air_quality": air_quality,
                "wqi": None if wqi is None else float(wqi),
                "crowdedness_percent": None if crowdedness_percent is None else float(crowdedness_percent),
            }
        )

    averages = {
        "sst_celsius": (lambda v: None if v is None else round(v, 2))(_mean([r["sst_celsius"] for r in series])),
        "turbidity_ndti": (lambda v: None if v is None else round(v, 4))(_mean([r["turbidity_ndti"] for r in series])),
        "pollution_percent": (lambda v: None if v is None else round(v, 1))(_mean([r["pollution_percent"] for r in series])),
        "chlorophyll": (lambda v: None if v is None else round(v, 4))(_mean([r["chlorophyll"] for r in series])),
        "no2_mol_m2": _mean([r["no2_mol_m2"] for r in series]),
        "wqi": (lambda v: None if v is None else round(v, 1))(_mean([r["wqi"] for r in series])),
        "crowdedness_percent": (lambda v: None if v is None else round(v, 1))(_mean([r["crowdedness_percent"] for r in series])),
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
