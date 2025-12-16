import ee
from datetime import datetime, timedelta
from typing import Optional
from app.utils.geo import get_beach_buffer


def classify_no2(no2_value: Optional[float]) -> str:
    if no2_value is None:
        return "unknown"

    if no2_value < 0.00003:
        return "good"
    elif no2_value < 0.00006:
        return "moderate"
    return "poor"


def get_air_quality_for_beach(beach_id: str, days: int = 7) -> dict:
    geometry = get_beach_buffer(beach_id, buffer_m=3000)

    end = datetime.utcnow()
    start = end - timedelta(days=days)

    collection = (
        ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
        .select("tropospheric_NO2_column_number_density")
        .filterDate(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        .filterBounds(geometry)
    )

    if collection.size().getInfo() == 0:
        return {
            "no2": None,
            "air_quality": "unknown"
        }

    image = collection.mean()

    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9
    )

    no2 = stats.get(
        "tropospheric_NO2_column_number_density"
    ).getInfo()

    return {
        "no2": no2,
        "air_quality": classify_no2(no2)
    }
