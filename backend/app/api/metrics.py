from fastapi import APIRouter, Query, HTTPException
from app.services.oisst import get_sst_for_beach
from app.data.beaches import BEACHES
from app.services.chlorophyll import get_chlorophyll_for_beach
from app.services.turbidity import get_turbidity_for_beach
from app.services.wqi import calculate_wqi
from app.services.pollution import calculate_pollution_from_turbidity
from app.services.crowdedness import get_crowdedness_percent


router = APIRouter(
    prefix="/api/metrics",
    tags=["metrics"]
)

@router.get("/sst")
def get_sst(
    beach_id: str = Query(..., description="Beach identifier (e.g. konyaalti)"),
    days: int = Query(7, ge=1, le=30)
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    beach = BEACHES[beach_id]
    sst = get_sst_for_beach(beach_id, days=days)

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
            "sst_celsius": round(sst, 2)
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

    result = calculate_wqi(beach_id, days)

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


@router.get("/pollution")
def get_pollution(
    beach_id: str = Query(...),
    days: int = Query(7, ge=1, le=30)
):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    beach = BEACHES[beach_id]

    turbidity = get_turbidity_for_beach(beach_id, days=days)
    pollution = calculate_pollution_from_turbidity(turbidity)

    if pollution is None:
        raise HTTPException(status_code=204, detail="No turbidity data")

    return {
        "metric": "pollution",
        "unit": "percent",
        "days": days,
        "data": {
            "id": beach_id,
            "name": beach["name"],
            "pollution_percent": round(pollution, 1)
        }
    }

@router.get("/crowdedness")
def get_crowdedness(beach_id: str, days: int = 7):
    if beach_id not in BEACHES:
        raise HTTPException(status_code=404, detail="Beach not found")

    sst = get_sst_for_beach(beach_id, days=days)
    crowdedness = get_crowdedness_percent(sst_celsius=sst)

    return {
        "metric": "crowdedness",
        "unit": "percent",
        "data": {
            "id": beach_id,
            "name": BEACHES[beach_id]["name"],
            "crowdedness_percent": crowdedness,
            "sst_celsius": round(sst, 2)
        }
    }
