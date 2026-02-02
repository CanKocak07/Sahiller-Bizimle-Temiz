from app.services.oisst import get_sst_for_beach
from app.services.chlorophyll import get_chlorophyll_for_beach
from app.services.turbidity import get_turbidity_for_beach

def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(value, max_val))


def normalize_linear(value: float, good: float, bad: float) -> float:
    """Map a value to [0..1] where 0=good, 1=bad, then clamp."""
    if bad == good:
        return 0.0
    return clamp((value - good) / (bad - good))


def normalize_sst(sst: float) -> float:
    """
    Akdeniz referansı:
    20°C = çok iyi
    30°C = çok kötü
    """
    # Calibrated to avoid over-penalizing typical seasonal sea temperatures.
    return normalize_linear(sst, good=20.0, bad=30.0)


def normalize_chlorophyll(chl: float) -> float:
    """
    0–2 temiz
    250+ riskli
    """
    # Calibrated so moderate chlorophyll doesn't immediately tank WQI.
    # NOTE: In this dataset chlorophyll values can be very large (>> 20).
    # Using a higher "bad" threshold avoids saturating at 1.0 for most days.
    return normalize_linear(chl, good=2.0, bad=250.0)


def normalize_turbidity(ndti: float) -> float:
    """
    NDTI: lower is better
    """
    # Calibrated around typical coastal NDTI ranges so small negatives are treated as clean.
    return normalize_linear(ndti, good=-0.05, bad=0.40)


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
