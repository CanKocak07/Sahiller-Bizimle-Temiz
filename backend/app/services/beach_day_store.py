from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from google.cloud import firestore


def _enabled() -> bool:
    return os.getenv("FIRESTORE_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}


def enabled() -> bool:
    return _enabled()


def _collection_name() -> str:
    return os.getenv("FIRESTORE_COLLECTION", "beach_day_metrics").strip() or "beach_day_metrics"


def _project() -> Optional[str]:
    p = os.getenv("EE_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    return p.strip() if isinstance(p, str) and p.strip() else None


_client: Optional[firestore.Client] = None


def _get_client() -> firestore.Client:
    global _client
    if _client is not None:
        return _client

    project = _project()
    _client = firestore.Client(project=project) if project else firestore.Client()
    return _client


def _doc_id(beach_id: str, day: str) -> str:
    return f"{beach_id}:{day}"


def get_day(beach_id: str, day: str) -> Optional[Dict[str, Any]]:
    if not _enabled():
        return None

    doc = _get_client().collection(_collection_name()).document(_doc_id(beach_id, day)).get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    # Ensure required keys exist.
    data.setdefault("beach_id", beach_id)
    data.setdefault("date", day)
    return data


def upsert_day(beach_id: str, day: str, payload: Dict[str, Any]) -> None:
    if not _enabled():
        return

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    doc_ref = _get_client().collection(_collection_name()).document(_doc_id(beach_id, day))
    doc_ref.set(
        {
            **payload,
            "beach_id": beach_id,
            "date": day,
            "updated_at": now,
        },
        merge=True,
    )


def get_days(beach_id: str, days: Iterable[str]) -> List[Optional[Dict[str, Any]]]:
    return [get_day(beach_id, d) for d in days]
