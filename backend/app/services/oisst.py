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
) -> float | None:
    """
    Belirli bir sahil için ortalama deniz yüzeyi sıcaklığı (°C).

    Parametreler:
    - beach_id: sahil kimliği
    - days: kaç günlük ortalama (varsayılan 7)

    Dönen:
    - float (°C)
    """

    start_date, end_date = _get_date_range(days)

    # OISST'in çözünürlüğü ~25km olduğu için 3km'lik buffer bazı sahillerde
    # (özellikle kıyı/dağ-karışımı piksellerde) "no valid pixels" döndürebilir.
    # SST için daha büyük bir buffer kullanıyoruz.
    geometry = get_beach_buffer(beach_id, buffer_m=30000)

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

    # Earth Engine objesini Python değerine indirip null kontrolü yapıyoruz.
    try:
        stats_dict = stats.getInfo()
    except Exception:
        # EE bazen geçici hatalar atabilir; caller tarafı no_data olarak ele alabilir.
        return None

    sst_raw = (stats_dict or {}).get("sst")
    if sst_raw is None:
        return None

    # NOAA OISST: SST = Celsius * 100
    return float(sst_raw) * 0.01

