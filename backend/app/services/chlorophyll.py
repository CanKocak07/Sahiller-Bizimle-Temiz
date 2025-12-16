import ee
from datetime import datetime, timedelta
from app.utils.geo import get_beach_buffer


def get_chlorophyll_for_beach_in_range(beach_id: str, start_date: str, end_date: str) -> float:
    geometry = get_beach_buffer(beach_id)

    collection = (
        ee.ImageCollection("COPERNICUS/S3/OLCI")
        .filterDate(start_date, end_date)
        .filterBounds(geometry)
        .select("Oa08_radiance")  # chlorophyll-related band
    )

    if collection.size().getInfo() == 0:
        return None

    image = collection.mean()

    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=300,
        maxPixels=1e9,
    )

    value = stats.get("Oa08_radiance")
    if value is None:
        return None

    return ee.Number(value).getInfo()


def get_chlorophyll_for_beach(beach_id: str, days: int = 7) -> float:
    """
    Returns mean chlorophyll-a concentration (mg/m^3)
    using Sentinel-3 OLCI data.
    """

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return get_chlorophyll_for_beach_in_range(
        beach_id,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )
