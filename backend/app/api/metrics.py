from fastapi import APIRouter, Query, HTTPException
import json
import logging
from app.services.oisst import get_sst_for_beach
from app.data.beaches import BEACHES
from app.services.chlorophyll import get_chlorophyll_for_beach
from app.services.turbidity import get_turbidity_for_beach
from app.services.wqi import calculate_wqi
from app.services.air_quality import get_air_quality_for_beach
from app.services.waste_risk import get_waste_risk_for_beach
from app.services.timeseries import get_beach_summary
from app.services.summary_cache import CacheEntry, current_window, make_key, get as cache_get, set as cache_set
from datetime import datetime


router = APIRouter(
    prefix="/api/metrics",
    tags=["metrics"]
)

logger = logging.getLogger("uvicorn.error")

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
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    window_start, window_end = current_window()
    key = make_key("beach-summary", beach_id=beach_id, days=days, window_start=window_start)

    cached = cache_get(key, window_start)
    if cached is not None:
        value = cached.value
        value["cache"] = {
            "window_start": cached.window_start.isoformat(),
            "window_end": cached.window_end.isoformat(),
            "generated_at": cached.generated_at.isoformat(),
            "hit": True,
        }
        if debug:
            logger.info(
                "[debug] beach-summary cache HIT beach_id=%s days=%s window_start=%s\n%s",
                beach_id,
                days,
                cached.window_start.isoformat(),
                json.dumps(value, ensure_ascii=False, indent=2),
            )
        return value

    try:
        value = get_beach_summary(beach_id=beach_id, days=days)
        value["cache"] = {
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "hit": False,
        }

        if debug:
            logger.info(
                "[debug] beach-summary cache MISS beach_id=%s days=%s window_start=%s\n%s",
                beach_id,
                days,
                window_start.isoformat(),
                json.dumps(value, ensure_ascii=False, indent=2),
            )

        entry = CacheEntry(
            value=value,
            window_start=window_start,
            window_end=window_end,
            generated_at=datetime.utcnow(),
        )
        cache_set(key, entry)
        return value
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
