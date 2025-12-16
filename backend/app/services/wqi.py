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


def calculate_wqi_from_components(sst: float, chl: float, turb: float) -> dict:
    """Calculate WQI using whichever components are available.

    Accepts component values which may be None.
    Returns same shape as calculate_wqi(). Raises ValueError if no components.
    """

    parts: list[tuple[str, float, float]] = []  # (name, weight, normalized)

    if sst is not None:
        parts.append(("sst", 0.25, normalize_sst(sst)))
    if chl is not None:
        parts.append(("chlorophyll", 0.35, normalize_chlorophyll(chl)))
    if turb is not None:
        parts.append(("turbidity", 0.40, normalize_turbidity(turb)))

    if not parts:
        raise ValueError("Insufficient data for WQI calculation")

    weight_sum = sum(w for _, w, _ in parts)
    pollution_index = sum((w / weight_sum) * n for _, w, n in parts)

    wqi = round(100 * (1 - pollution_index), 1)

    return {
        "wqi": wqi,
        "components": {
            "sst_celsius": None if sst is None else round(sst, 2),
            "chlorophyll": None if chl is None else round(chl, 2),
            "turbidity_ndti": None if turb is None else round(turb, 4),
            "normalized": {
                "sst": None if sst is None else round(normalize_sst(sst), 3),
                "chlorophyll": None if chl is None else round(normalize_chlorophyll(chl), 3),
                "turbidity": None if turb is None else round(normalize_turbidity(turb), 3),
            },
            "weights": {
                name: round(w / weight_sum, 3) for name, w, _ in parts
            },
        },
    }


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

    return calculate_wqi_from_components(sst=sst, chl=chl, turb=turb)
