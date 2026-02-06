from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.data.beaches import BEACHES
from app.services import beach_day_store
from app.services.timeseries import get_beach_summary


def _rank(source: str) -> int:
    # Higher is better / more "real".
    return {"missing": 0, "imputed": 1, "window_avg": 2, "daily": 3}.get(source or "missing", 0)


_METRIC_FIELDS = [
    "sst_celsius",
    "turbidity_ndti",
    "chlorophyll",
    "no2_mol_m2",
    "air_quality",
    "wqi",
    "waste_risk_percent",
]


def _get_sources(row: Dict[str, Any]) -> Dict[str, str]:
    s = row.get("sources") or {}
    # Normalize missing keys.
    out: Dict[str, str] = {}
    for k in _METRIC_FIELDS:
        out[k] = str(s.get(k, "missing"))
    return out


def merge_if_improved(existing: Optional[Dict[str, Any]], incoming: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """Merge rule: only update a metric if its source rank improved.

    - New day (no existing) => write everything.
    - For last-N revise days: update only metrics whose `sources[field]` rank improves.
    - If ranks equal, keep existing value (even if numeric differs).
    """

    if existing is None:
        return incoming, True

    existing_sources = _get_sources(existing)
    incoming_sources = _get_sources(incoming)

    merged: Dict[str, Any] = {**existing}
    merged_sources: Dict[str, str] = {**existing_sources}
    changed = False

    for field in _METRIC_FIELDS:
        old_src = existing_sources.get(field, "missing")
        new_src = incoming_sources.get(field, "missing")

        if _rank(new_src) > _rank(old_src):
            merged[field] = incoming.get(field)
            merged_sources[field] = new_src
            changed = True

    merged["sources"] = merged_sources
    return merged, changed


@dataclass
class RefreshResult:
    beach_id: str
    as_of_day: str
    revise_days: int
    updated_docs: int
    created_docs: int


def refresh_beach(beach_id: str, *, as_of_day: date, days: int = 7, revise_days: int = 5) -> RefreshResult:
    summary = get_beach_summary(beach_id=beach_id, days=max(days, revise_days), end_day=as_of_day)
    series: List[Dict[str, Any]] = summary.get("series") or []

    # Only consider the tail for revision.
    tail = series[-revise_days:] if revise_days > 0 else []

    updated = 0
    created = 0

    for row in tail:
        day = row["date"]
        existing = beach_day_store.get_day(beach_id, day)
        merged, changed = merge_if_improved(existing, row)

        if existing is None:
            created += 1
            beach_day_store.upsert_day(beach_id, day, merged)
        elif changed:
            updated += 1
            beach_day_store.upsert_day(beach_id, day, merged)

    return RefreshResult(
        beach_id=beach_id,
        as_of_day=as_of_day.isoformat(),
        revise_days=revise_days,
        updated_docs=updated,
        created_docs=created,
    )


def refresh_all(*, as_of_day: date, days: int = 7, revise_days: int = 5) -> List[RefreshResult]:
    results: List[RefreshResult] = []
    for beach_id in BEACHES.keys():
        try:
            results.append(refresh_beach(beach_id, as_of_day=as_of_day, days=days, revise_days=revise_days))
        except Exception:
            # Keep going if one beach fails.
            continue
    return results
