"""
Geographic utilities for beach-based analysis.

Bu dosya:
- Projede kullanılan TEK sahil listesini içerir
- Her sahil için coğrafi referans (lat/lon) tanımlar
- Earth Engine geometry ve buffer üretir

⚠️ Bu dosya:
- Dataset bilmez
- Hesaplama yapmaz
- Sadece "nerede?" sorusunu cevaplar
"""

import ee
from typing import Dict, List, Optional


# -------------------------------------------------------------------
# CANONICAL BEACH REGISTRY
# (Frontend ile birebir eşleşmelidir)
# -------------------------------------------------------------------

BEACHES: Dict[str, Dict] = {
    "belek": {
        "name": "Belek Sahili",
        "lat": 36.8627,
        "lon": 31.0556,
        "buffer_m": 3000,
    },
    "bogazkent": {
        "name": "Boğazkent Sahili",
        "lat": 36.8409,
        "lon": 31.0735,
        "buffer_m": 3000,
    },
    "kadriye": {
        "name": "Kadriye Sahili",
        "lat": 36.8611,
        "lon": 31.0239,
        "buffer_m": 3000,
    },
    "konyaalti": {
        "name": "Konyaaltı Plajı",
        "lat": 36.8606,
        "lon": 30.6371,
        "buffer_m": 3000,
    },
    "cirali": {
        "name": "Çıralı Plajı",
        "lat": 36.4153,
        "lon": 30.4812,
        "buffer_m": 3000,
    },
}


# -------------------------------------------------------------------
# BASIC ACCESSORS
# -------------------------------------------------------------------

def list_beaches() -> List[Dict]:
    """
    Frontend ve API için sahil listesini döner.
    """
    return [
        {
            "id": beach_id,
            "name": beach["name"],
            "lat": beach["lat"],
            "lon": beach["lon"],
        }
        for beach_id, beach in BEACHES.items()
    ]


def get_beach_config(beach_id: str) -> Dict:
    """
    Sahil konfigürasyonunu döner.
    """
    if beach_id not in BEACHES:
        raise ValueError(f"Unknown beach id: {beach_id}")

    return BEACHES[beach_id]


# -------------------------------------------------------------------
# EARTH ENGINE GEOMETRY HELPERS
# -------------------------------------------------------------------

def get_beach_point(beach_id: str) -> ee.Geometry.Point:
    """
    Sahil için Earth Engine Point geometry üretir.
    """
    beach = get_beach_config(beach_id)
    return ee.Geometry.Point([beach["lon"], beach["lat"]])



def get_beach_buffer(beach_id: str, buffer_m: Optional[int] = None) -> ee.Geometry:
    """
    Sahil noktası etrafında buffer alanı üretir.

    - buffer metre cinsindendir
    - eğer buffer_m verilmezse BEACHES içindeki varsayılan kullanılır
    """
    beach = get_beach_config(beach_id)
    point = get_beach_point(beach_id)

    radius = buffer_m if buffer_m is not None else beach["buffer_m"]
    return point.buffer(radius)
