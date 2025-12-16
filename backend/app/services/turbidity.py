import ee
from datetime import datetime, timedelta
from app.utils.geo import get_beach_buffer


S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"


def _date_range(days: int):
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _mask_s2_sr(image: ee.Image) -> ee.Image:
    """
    Sentinel-2 SR cloud mask (SCL based).
    Removes:
      - 3: Cloud shadow
      - 8: Cloud medium probability
      - 9: Cloud high probability
      - 10: Thin cirrus
      - 11: Snow/ice
    Keeps others.
    """
    scl = image.select("SCL")
    mask = (
        scl.neq(3)
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )
    return image.updateMask(mask)


def _water_mask_mndwi(image: ee.Image, threshold: float = 0.0) -> ee.Image:
    """
    Water mask using MNDWI:
      MNDWI = (Green - SWIR1) / (Green + SWIR1)
      Green = B3, SWIR1 = B11
    """
    mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
    water = mndwi.gt(threshold)
    return image.updateMask(water)


def get_turbidity_for_beach(beach_id: str, days: int = 14):
    """
    Returns mean turbidity proxy (NDTI) for a beach buffer.

    Output:
      - float in approx [-1, 1] (relative index)
      - None if no valid pixels found in the time window

    Notes:
      - Coastal zones can easily return None due to masking and land-water mixing.
      - This is expected; handle None in API (return no_data instead of 500).
    """
    geometry = get_beach_buffer(beach_id)
    start_date, end_date = _date_range(days)

    col = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        # keep it a bit loose; SCL mask already helps
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 50))
        .map(_mask_s2_sr)
        .map(lambda img: _water_mask_mndwi(img, threshold=0.0))
        .select(["B4", "B3"])  # Red, Green
    )

    # If collection empty, return None safely
    size = col.size()
    if size.getInfo() == 0:
        return None

    img = col.median()

    # NDTI = (Red - Green) / (Red + Green)
    ndti = img.normalizedDifference(["B4", "B3"]).rename("NDTI")

    stats = ndti.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=20,
        maxPixels=1e9,
        bestEffort=True,
    ).getInfo()

    value = stats.get("NDTI")
    if value is None:
        return None

    return float(value)
