import ee
from datetime import datetime, timedelta
from app.utils.geo import get_beach_buffer


def get_chlorophyll_for_beach(beach_id: str, days: int = 7) -> float:
    """
    Returns mean chlorophyll-a concentration (mg/m^3)
    using Sentinel-3 OLCI data.
    """

    geometry = get_beach_buffer(beach_id)

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    collection = (
        ee.ImageCollection("COPERNICUS/S3/OLCI")
        .filterDate(start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"))
        .filterBounds(geometry)
        .select("Oa08_radiance")  # chlorophyll-related band
    )

    image = collection.mean()

    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=300,
        maxPixels=1e9
    )

    value = stats.get("Oa08_radiance")

    if value is None:
        return None

    return ee.Number(value).getInfo()
