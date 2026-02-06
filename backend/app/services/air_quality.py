import ee
from datetime import datetime, timedelta
from typing import Optional
from app.utils.geo import get_beach_buffer

import os

# OFFL NO2 dataset availability can lag / end earlier than NRTI. For a site that
# refreshes daily, we default to using NRTI as a fallback when OFFL is missing.
_FILL_GAPS_ENABLED = os.getenv("FILL_GAPS_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}

_NO2_OFFL_COLLECTION = "COPERNICUS/S5P/OFFL/L3_NO2"
_NO2_NRTI_COLLECTION = "COPERNICUS/S5P/NRTI/L3_NO2"
_NO2_OFFL_BAND = "tropospheric_NO2_column_number_density"
# Earth Engine catalog example for NRTI uses NO2_column_number_density.
_NO2_NRTI_BAND = "NO2_column_number_density"


def _parse_ymd(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def _fmt_ymd(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _no2_mean_for_range(
    dataset_id: str,
    band: str,
    geometry: ee.Geometry,
    start_date: str,
    end_date: str,
) -> Optional[float]:
    collection = (
        ee.ImageCollection(dataset_id)
        .select(band)
        .filterDate(start_date, end_date)
        .filterBounds(geometry)
    )

    try:
        if collection.size().getInfo() == 0:
            return None
    except Exception:
        return None

    image = collection.mean()
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9,
    )

    try:
        v = stats.get(band).getInfo()
    except Exception:
        return None

    return None if v is None else float(v)


def classify_no2(no2_value: Optional[float]) -> str:
    if no2_value is None:
        return "unknown"

    if no2_value < 0.00003:
        return "good"
    elif no2_value < 0.00006:
        return "moderate"
    return "poor"


def get_air_quality_for_beach(beach_id: str, days: int = 7) -> dict:
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    return get_air_quality_for_beach_in_range(
        beach_id,
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
    )


def get_air_quality_for_beach_in_range(beach_id: str, start_date: str, end_date: str) -> dict:
    geometry = get_beach_buffer(beach_id, buffer_m=3000)

    # Try OFFL first (more stable), then NRTI (lower latency) if enabled.
    no2 = _no2_mean_for_range(_NO2_OFFL_COLLECTION, _NO2_OFFL_BAND, geometry, start_date, end_date)
    if no2 is None and _FILL_GAPS_ENABLED:
        no2 = _no2_mean_for_range(_NO2_NRTI_COLLECTION, _NO2_NRTI_BAND, geometry, start_date, end_date)

    # If still missing and we're on a narrow daily window, widen by ±1 day once.
    if no2 is None and _FILL_GAPS_ENABLED:
        try:
            start = _parse_ymd(start_date)
            end = _parse_ymd(end_date)
        except Exception:
            start = end = None

        if start is not None and end is not None and (end - start) <= timedelta(days=1):
            widened_start = _fmt_ymd(start - timedelta(days=1))
            widened_end = _fmt_ymd(end + timedelta(days=1))
            no2 = _no2_mean_for_range(_NO2_NRTI_COLLECTION, _NO2_NRTI_BAND, geometry, widened_start, widened_end)
            if no2 is None:
                no2 = _no2_mean_for_range(_NO2_OFFL_COLLECTION, _NO2_OFFL_BAND, geometry, widened_start, widened_end)

    return {
        "no2": no2,
        "air_quality": classify_no2(no2)
    }
