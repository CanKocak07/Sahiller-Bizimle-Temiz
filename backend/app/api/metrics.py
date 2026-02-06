from fastapi import APIRouter, Query, HTTPException, Header
import json
import logging
import os
from app.services.oisst import get_sst_for_beach
from app.data.beaches import BEACHES
from app.services.chlorophyll import get_chlorophyll_for_beach
from app.services.turbidity import get_turbidity_for_beach
from app.services.wqi import calculate_wqi
from app.services.air_quality import get_air_quality_for_beach
from app.services.waste_risk import get_waste_risk_for_beach
from app.services.timeseries import get_beach_summary
from app.services.daily_refresh import refresh_beach
from app.services.tr_time import current_refresh_window, tr_today
from app.services import beach_day_store
from datetime import date, datetime, timedelta, timezone


router = APIRouter(
    prefix="/api/metrics",
    tags=["metrics"]
)

logger = logging.getLogger("uvicorn.error")


def _require_refresh_token(token: str | None) -> None:
    expected = (os.getenv("REFRESH_TOKEN") or "").strip()
    if not expected:
        raise HTTPException(status_code=501, detail="Refresh token not configured")
    if not token or token.strip() != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _assemble_series_from_store(beach_id: str, days: int, end_day: date) -> dict:
    if not beach_day_store.enabled():
        # Local/dev fallback: compute directly.
        refresh = current_refresh_window(datetime.now(timezone.utc))
        computed = get_beach_summary(beach_id=beach_id, days=days, end_day=end_day)
        computed["cache"] = {
            "snapshot_date": refresh.snapshot_date,
            "timezone": refresh.timezone,
            "next_refresh_at": refresh.next_refresh_at,
        }
        return computed

    # Build list of requested days.
    day_list = [(end_day - timedelta(days=(days - 1 - i))).isoformat() for i in range(days)]
    docs = beach_day_store.get_days(beach_id, day_list)

    # If anything is missing, compute on-demand and store the missing docs.
    if any(d is None for d in docs):
        computed = get_beach_summary(beach_id=beach_id, days=days, end_day=end_day)
        computed_series = computed.get("series") or []
        by_date = {r.get("date"): r for r in computed_series}
        for d in day_list:
            if beach_day_store.get_day(beach_id, d) is None:
                row = by_date.get(d)
                if row is not None:
                    beach_day_store.upsert_day(beach_id, d, row)
        docs = beach_day_store.get_days(beach_id, day_list)

    series = [d for d in docs if d is not None]

    # Compute averages.
    def _mean(xs):
        nums = [v for v in xs if isinstance(v, (int, float))]
        return None if not nums else sum(nums) / len(nums)

    averages = {
        "sst_celsius": (lambda v: None if v is None else round(v, 2))(_mean([r.get("sst_celsius") for r in series])),
        "turbidity_ndti": (lambda v: None if v is None else round(v, 4))(_mean([r.get("turbidity_ndti") for r in series])),
        "chlorophyll": (lambda v: None if v is None else round(v, 4))(_mean([r.get("chlorophyll") for r in series])),
        "no2_mol_m2": _mean([r.get("no2_mol_m2") for r in series]),
        "wqi": (lambda v: None if v is None else round(v, 1))(_mean([r.get("wqi") for r in series])),
        "waste_risk_percent": (lambda v: None if v is None else round(v, 1))(
            _mean([r.get("waste_risk_percent") for r in series])
        ),
    }

    refresh = current_refresh_window(datetime.now(timezone.utc))

    return {
        "beach": {
            "id": beach_id,
            "name": BEACHES[beach_id]["name"],
            "lat": BEACHES[beach_id].get("lat"),
            "lon": BEACHES[beach_id].get("lon"),
        },
        "days": days,
        "series": [
            {
                "date": r.get("date"),
                "sst_celsius": r.get("sst_celsius"),
                "turbidity_ndti": r.get("turbidity_ndti"),
                "chlorophyll": r.get("chlorophyll"),
                "no2_mol_m2": r.get("no2_mol_m2"),
                "air_quality": r.get("air_quality"),
                "wqi": r.get("wqi"),
                "waste_risk_percent": r.get("waste_risk_percent"),
                "sources": r.get("sources"),
            }
            for r in series
        ],
        "averages": averages,
        "cache": {
            "snapshot_date": refresh.snapshot_date,
            "timezone": refresh.timezone,
            "next_refresh_at": refresh.next_refresh_at,
        },
    }

@router.get("/sst")
def get_sst(
    beach_id: str = Query(..., description="Beach identifier (e.g. konyaalti)"),
    days: int = Query(7, ge=1, le=30)
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    beach = BEACHES[beach_id]
    sst = get_sst_for_beach(beach_id, days=days)

    if sst is None:
        return {
            "metric": "sea_surface_temperature",
            "unit": "celsius",
            "days": days,
            "data": {
                "id": beach_id,
                "name": beach["name"],
                "sst_celsius": None,
                "status": "no_data",
            },
        }

    return {
        "metric": "sea_surface_temperature",
        "unit": "celsius",
        "days": days,
        "data": {
            "id": beach_id,
            "name": beach["name"],
            "sst_celsius": round(sst, 2)
        }
    }

@router.get("/sst/all")
def get_sst_all(days: int = Query(7, ge=1, le=30)):
    results = []

    for beach_id, beach in BEACHES.items():
        sst = get_sst_for_beach(beach_id, days=days)

        results.append({
            "id": beach_id,
            "name": beach["name"],
            "sst_celsius": None if sst is None else round(sst, 2)
        })

    return {
        "metric": "sea_surface_temperature",
        "unit": "celsius",
        "days": days,
        "count": len(results),
        "data": results
    }


@router.get("/chlorophyll")
def get_chlorophyll(
    beach_id: str = Query(..., description="Beach identifier (e.g. konyaalti)"),
    days: int = Query(7, ge=1, le=30)
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    beach = BEACHES[beach_id]
    value = get_chlorophyll_for_beach(beach_id, days=days)

    if value is None:
        raise HTTPException(status_code=204, detail="No data available")

    return {
        "metric": "chlorophyll_a",
        "unit": "relative_index",
        "days": days,
        "data": {
            "id": beach_id,
            "name": beach["name"],
            "chlorophyll": round(value, 4)
        }
    }

@router.get("/turbidity")
def get_turbidity(
    beach_id: str = Query(...),
    days: int = Query(7, ge=1, le=30)
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    beach = BEACHES[beach_id]
    turbidity = get_turbidity_for_beach(beach_id, days)
    if turbidity is None:
        return {"metric":"turbidity","unit":"relative_index","days":days,
                "data":{"id":beach_id,"name":beach["name"],"turbidity":None,"status":"no_data"}}


    return {
        "metric": "turbidity",
        "unit": "relative_index",
        "days": days,
        "data": {
            "id": beach_id,
            "name": beach["name"],
            "turbidity": round(turbidity, 4)
        }
    }


@router.get("/wqi")
def get_wqi(
    beach_id: str,
    days: int = 7
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    try:
        result = calculate_wqi(beach_id, days)
    except Exception:
        return {
            "metric": "water_quality_index",
            "scale": "0-100",
            "days": days,
            "data": {
                "id": beach_id,
                "name": BEACHES[beach_id]["name"],
                "wqi": None,
                "status": "no_data",
            },
        }

    return {
        "metric": "water_quality_index",
        "scale": "0-100",
        "days": days,
        "data": {
            "id": beach_id,
            "name": BEACHES[beach_id]["name"],
            **result
        }
    }


@router.get("/air-quality")
def get_air_quality(beach_id: str, days: int = 7):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    result = get_air_quality_for_beach(beach_id, days=days)

    return {
        "metric": "air_quality",
        "source": "Sentinel-5P (NO2)",
        "days": days,
        "data": {
            "id": beach_id,
            "name": BEACHES[beach_id]["name"],
            "no2_mol_m2": result["no2"],
            "air_quality": result["air_quality"]
        }
    }


@router.get("/waste-risk")
def get_waste_risk(
    beach_id: str = Query(..., description="Beach identifier (e.g. konyaalti)"),
    days: int = Query(30, ge=1, le=90),
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    result = get_waste_risk_for_beach(beach_id, days=days)
    if result is None:
        return {
            "metric": "waste_accumulation_risk",
            "unit": "percent",
            "days": days,
            "data": {
                "id": beach_id,
                "name": BEACHES[beach_id]["name"],
                "waste_risk_percent": None,
                "status": "no_data",
            },
        }

    return {
        "metric": "waste_accumulation_risk",
        "unit": "percent",
        "days": days,
        "data": {
            "id": beach_id,
            "name": BEACHES[beach_id]["name"],
            **result,
        },
    }


@router.get("/beach-summary")
def beach_summary(
    beach_id: str = Query(..., description="Beach identifier (e.g. konyaalti)"),
    days: int = Query(7, ge=1, le=30),
    debug: bool = Query(False, description="If true, logs computed metrics to server console"),
    refresh: bool = Query(
        False,
        description="If true, recomputes and revises last days before serving (expensive). Prefer /admin/refresh.",
    ),
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    try:
        end_day = tr_today()

        # By default, serve the stored daily snapshot series. Missing days are
        # computed on-demand inside _assemble_series_from_store.
        #
        # IMPORTANT: We intentionally do not revise on every request; revisions
        # should be triggered by a daily scheduler calling /admin/refresh.
        if refresh:
            refresh_beach(beach_id, as_of_day=end_day, days=days, revise_days=5)

        value = _assemble_series_from_store(beach_id, days=days, end_day=end_day)
        if debug:
            logger.info(
                "[debug] beach-summary served from daily store beach_id=%s days=%s\n%s",
                beach_id,
                days,
                json.dumps(value, ensure_ascii=False, indent=2),
            )
        return value
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/refresh")
def admin_refresh(
    x_refresh_token: str | None = Header(None, alias="X-Refresh-Token"),
    days: int = Query(7, ge=1, le=30),
    revise_days: int = Query(5, ge=0, le=30),
):
    _require_refresh_token(x_refresh_token)

    as_of = tr_today()
    results = []
    for beach_id in BEACHES.keys():
        try:
            r = refresh_beach(beach_id, as_of_day=as_of, days=days, revise_days=revise_days)
            results.append(
                {
                    "beach_id": r.beach_id,
                    "as_of_day": r.as_of_day,
                    "revise_days": r.revise_days,
                    "created": r.created_docs,
                    "updated": r.updated_docs,
                }
            )
        except Exception:
            continue

    return {
        "ok": True,
        "as_of_day": as_of.isoformat(),
        "days": days,
        "revise_days": revise_days,
        "results": results,
    }
