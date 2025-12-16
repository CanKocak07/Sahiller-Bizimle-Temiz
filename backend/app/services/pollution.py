def calculate_pollution_from_turbidity(turbidity: float) -> float:
    """
    Converts turbidity index (-1 to +1 approx) into pollution percentage (0–100)
    """
    if turbidity is None:
        return None

    # Normalize to 0–1
    norm = (turbidity + 1) / 2
    norm = max(0.0, min(1.0, norm))  # clamp

    # Convert to percentage
    pollution_percent = norm * 100
    return pollution_percent
