from app.services.oisst import get_sst_for_beach
from app.services.chlorophyll import get_chlorophyll_for_beach
from app.services.turbidity import get_turbidity_for_beach

def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(value, max_val))


def normalize_sst(sst: float) -> float:
    """
    Akdeniz referansı:
    18°C = çok iyi
    30°C = çok kötü
    """
    return clamp((sst - 18) / (30 - 18))


def normalize_chlorophyll(chl: float) -> float:
    """
    0–5 temiz
    20+ riskli
    """
    return clamp(chl / 20)


def normalize_turbidity(ndti: float) -> float:
    """
    NDTI: -1 → +1
    """
    return clamp((ndti + 1) / 2)


def calculate_wqi(beach_id: str, days: int = 7) -> dict:
    """
    Returns:
    {
        "wqi": float,
        "components": {...}
    }
    """

    sst = get_sst_for_beach(beach_id, days)
    chl = get_chlorophyll_for_beach(beach_id, days)
    turb = get_turbidity_for_beach(beach_id, days)

    if sst is None or chl is None or turb is None:
        raise ValueError("Insufficient data for WQI calculation")

    sst_n = normalize_sst(sst)
    chl_n = normalize_chlorophyll(chl)
    turb_n = normalize_turbidity(turb)

    pollution_index = (
        0.4 * turb_n +
        0.35 * chl_n +
        0.25 * sst_n
    )

    wqi = round(100 * (1 - pollution_index), 1)

    return {
        "wqi": wqi,
        "components": {
            "sst_celsius": round(sst, 2),
            "chlorophyll": round(chl, 2),
            "turbidity_ndti": round(turb, 4),
            "normalized": {
                "sst": round(sst_n, 3),
                "chlorophyll": round(chl_n, 3),
                "turbidity": round(turb_n, 3)
            }
        }
    }
