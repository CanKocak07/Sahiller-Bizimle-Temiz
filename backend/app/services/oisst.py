"""
NOAA OISST (Sea Surface Temperature) service.

Bu servis:
- NOAA OISST v2.1 dataset'ini kullanır
- Sahil bazlı deniz yüzeyi sıcaklığı hesaplar
"""

import ee
from datetime import date, timedelta
from app.utils.geo import get_beach_buffer


# Dataset ID
OISST_COLLECTION = "NOAA/CDR/OISST/V2_1"


def _get_date_range(days: int):
    """
    Bugünden geriye doğru tarih aralığı üretir.
    """
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def get_sst_for_beach(
    beach_id: str,
    days: int = 7,
) -> float:
    """
    Belirli bir sahil için ortalama deniz yüzeyi sıcaklığı (°C).

    Parametreler:
    - beach_id: sahil kimliği
    - days: kaç günlük ortalama (varsayılan 7)

    Dönen:
    - float (°C)
    """

    start_date, end_date = _get_date_range(days)

    geometry = get_beach_buffer(beach_id)

    collection = (
        ee.ImageCollection(OISST_COLLECTION)
        .filterDate(start_date, end_date)
        .select("sst")
    )

    # Zaman ortalaması
    mean_image = collection.mean()

    # Mekansal ortalama
    stats = mean_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=25000,  # OISST çözünürlüğü (~25 km)
        maxPixels=1e9,
    )

    # Kelvin → Celsius dönüşümü
    sst_raw = stats.get("sst")
    if sst_raw is None:
        raise ValueError("SST data not available for this beach")

    # NOAA OISST: SST = Celsius * 100
    sst_celsius = ee.Number(sst_raw).multiply(0.01)

    return sst_celsius.getInfo()

