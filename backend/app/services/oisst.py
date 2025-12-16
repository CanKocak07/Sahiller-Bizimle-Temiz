"""
NOAA OISST (Sea Surface Temperature) service.

Bu servis:
- NOAA OISST v2.1 dataset'ini kullanır
- Sahil bazlı deniz yüzeyi sıcaklığı hesaplar
"""

import ee
from datetime import date, timedelta
from typing import Optional
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


def get_sst_for_beach_in_range(
    beach_id: str,
    start_date: str,
    end_date: str,
) -> Optional[float]:
    """Returns mean sea surface temperature (°C) for an explicit date range."""

    # OISST'in çözünürlüğü ~25km olduğu için 3km'lik buffer bazı sahillerde
    # (özellikle kıyı/dağ-karışımı piksellerde) "no valid pixels" döndürebilir.
    # SST için daha büyük bir buffer kullanıyoruz.
    geometry = get_beach_buffer(beach_id, buffer_m=30000)

    collection = (
        ee.ImageCollection(OISST_COLLECTION)
        .filterDate(start_date, end_date)
        .select("sst")
    )

    if collection.size().getInfo() == 0:
        return None

    mean_image = collection.mean()

    stats = mean_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=25000,  # OISST çözünürlüğü (~25 km)
        maxPixels=1e9,
    )

    try:
        stats_dict = stats.getInfo()
    except Exception:
        return None

    sst_raw = (stats_dict or {}).get("sst")
    if sst_raw is None:
        return None

    # NOAA OISST: SST = Celsius * 100
    return float(sst_raw) * 0.01


def get_sst_for_beach(
    beach_id: str,
    days: int = 7,
) -> Optional[float]:
    """
    Belirli bir sahil için ortalama deniz yüzeyi sıcaklığı (°C).

    Parametreler:
    - beach_id: sahil kimliği
    - days: kaç günlük ortalama (varsayılan 7)

    Dönen:
    - float (°C)
    """

    start_date, end_date = _get_date_range(days)
    return get_sst_for_beach_in_range(beach_id, start_date=start_date, end_date=end_date)

