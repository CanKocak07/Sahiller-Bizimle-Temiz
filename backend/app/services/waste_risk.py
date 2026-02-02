import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

import ee

from app.utils.geo import get_beach_buffer


# Main source: Sentinel-2 SR (10m), cloud-masked via SCL.
_S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

# Support source: Landsat 8/9 L2 (30m)
_L8_COLLECTION = "LANDSAT/LC08/C02/T1_L2"
_L9_COLLECTION = "LANDSAT/LC09/C02/T1_L2"

_FILL_GAPS_ENABLED = os.getenv("FILL_GAPS_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


def _parse_ymd(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def _fmt_ymd(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _date_range(days: int) -> Tuple[str, str]:
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _index_to_percent(idx: Optional[float]) -> Optional[float]:
    """Normalize an index in [-1..1] to [0..100]."""
    if idx is None:
        return None
    return 100.0 * _clamp01((float(idx) + 1.0) / 2.0)


def _mask_s2_sr(image: ee.Image) -> ee.Image:
    """Sentinel-2 SR cloud mask using SCL band."""
    scl = image.select("SCL")
    mask = (
        scl.neq(3)
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )
    return image.updateMask(mask)


def _landsat_sr(image: ee.Image) -> ee.Image:
    """Scale/offset Landsat Collection 2 Level-2 SR bands to reflectance."""
    optical = image.select(["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6"]).multiply(0.0000275).add(-0.2)
    return image.addBands(optical, overwrite=True)


def _mask_landsat_l2(image: ee.Image) -> ee.Image:
    """Mask Landsat L2 using QA_PIXEL bits (cloud, shadow, cirrus, snow)."""
    qa = image.select("QA_PIXEL")

    # Bits (USGS Collection 2):
    # 0 fill, 1 dilated cloud, 2 cirrus, 3 cloud, 4 cloud shadow, 5 snow
    dilated_cloud = qa.bitwiseAnd(1 << 1).neq(0)
    cirrus = qa.bitwiseAnd(1 << 2).neq(0)
    cloud = qa.bitwiseAnd(1 << 3).neq(0)
    cloud_shadow = qa.bitwiseAnd(1 << 4).neq(0)
    snow = qa.bitwiseAnd(1 << 5).neq(0)

    mask = dilated_cloud.Or(cirrus).Or(cloud).Or(cloud_shadow).Or(snow).Not()
    return image.updateMask(mask)


def _s2_indices_for_range(geometry: ee.Geometry, start_date: str, end_date: str) -> tuple[Optional[float], Optional[float]]:
    col = (
        ee.ImageCollection(_S2_COLLECTION)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
        .map(_mask_s2_sr)
        .select(["B8", "B4", "B3", "B11"])  # NIR, Red, Green, SWIR
    )

    if col.size().getInfo() == 0:
        return None, None

    img = col.median()
    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
    mndwi = img.normalizedDifference(["B3", "B11"]).rename("MNDWI")

    stats = ndvi.addBands(mndwi).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=20,
        maxPixels=1e9,
        bestEffort=True,
    ).getInfo()

    ndvi_v = stats.get("NDVI")
    mndwi_v = stats.get("MNDWI")

    return (None if ndvi_v is None else float(ndvi_v), None if mndwi_v is None else float(mndwi_v))


def _landsat_indices_for_range(geometry: ee.Geometry, start_date: str, end_date: str) -> tuple[Optional[float], Optional[float]]:
    col = (
        ee.ImageCollection(_L8_COLLECTION)
        .merge(ee.ImageCollection(_L9_COLLECTION))
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .map(_mask_landsat_l2)
        .map(_landsat_sr)
        .select(["SR_B5", "SR_B4", "SR_B3", "SR_B6"])  # NIR, Red, Green, SWIR1
    )

    if col.size().getInfo() == 0:
        return None, None

    img = col.median()
    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    mndwi = img.normalizedDifference(["SR_B3", "SR_B6"]).rename("MNDWI")

    stats = ndvi.addBands(mndwi).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=30,
        maxPixels=1e9,
        bestEffort=True,
    ).getInfo()

    ndvi_v = stats.get("NDVI")
    mndwi_v = stats.get("MNDWI")

    return (None if ndvi_v is None else float(ndvi_v), None if mndwi_v is None else float(mndwi_v))


def get_waste_risk_for_beach_in_range(beach_id: str, start_date: str, end_date: str) -> Optional[dict]:
    """Compute "Atık Birikme Riski" (0-100%) for a beach buffer in a date range.

    Pipeline (per spec):
      - Sentinel-2 SR (primary): NDVI + MNDWI computed from bands
      - Cloud masking: SCL
      - Reduce: mean over region
      - Normalize to 0..100
      - Risk = 0.5 * NDVI_risk + 0.5 * MNDWI_risk

    Falls back to Landsat 8/9 L2 if Sentinel-2 returns no usable pixels.
    """

    geometry = get_beach_buffer(beach_id)

    ndvi, mndwi = _s2_indices_for_range(geometry, start_date=start_date, end_date=end_date)
    source = "sentinel-2"

    if (ndvi is None or mndwi is None) and _FILL_GAPS_ENABLED:
        ndvi2, mndwi2 = _landsat_indices_for_range(geometry, start_date=start_date, end_date=end_date)
        if ndvi is None:
            ndvi = ndvi2
        if mndwi is None:
            mndwi = mndwi2
        if ndvi2 is not None or mndwi2 is not None:
            source = "landsat-8-9"

    # If masks removed all pixels, widen by ±1 day once (useful for daily windows).
    if (ndvi is None or mndwi is None) and _FILL_GAPS_ENABLED:
        try:
            start = _parse_ymd(start_date)
            end = _parse_ymd(end_date)
        except Exception:
            start = end = None

        if start is not None and end is not None and (end - start) <= timedelta(days=1):
            widened_start = _fmt_ymd(start - timedelta(days=1))
            widened_end = _fmt_ymd(end + timedelta(days=1))
            ndvi, mndwi = _s2_indices_for_range(geometry, start_date=widened_start, end_date=widened_end)
            source = "sentinel-2"

            if (ndvi is None or mndwi is None):
                ndvi2, mndwi2 = _landsat_indices_for_range(geometry, start_date=widened_start, end_date=widened_end)
                if ndvi is None:
                    ndvi = ndvi2
                if mndwi is None:
                    mndwi = mndwi2
                if ndvi2 is not None or mndwi2 is not None:
                    source = "landsat-8-9"

    ndvi_risk = _index_to_percent(ndvi)
    mndwi_risk = _index_to_percent(mndwi)

    if ndvi_risk is None and mndwi_risk is None:
        return None

    # If one component is missing, compute risk from the available one.
    if ndvi_risk is None:
        risk = mndwi_risk
    elif mndwi_risk is None:
        risk = ndvi_risk
    else:
        risk = 0.5 * ndvi_risk + 0.5 * mndwi_risk

    return {
        "waste_risk_percent": round(float(risk), 1) if risk is not None else None,
        "ndvi": None if ndvi is None else round(float(ndvi), 4),
        "mndwi": None if mndwi is None else round(float(mndwi), 4),
        "source": source,
    }


def get_waste_risk_for_beach(beach_id: str, days: int = 30) -> Optional[dict]:
    start_date, end_date = _date_range(days)
    return get_waste_risk_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)
