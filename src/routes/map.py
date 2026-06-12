from fastapi import APIRouter, Query, HTTPException

from src.services.geo_service import (
    get_businesses_in_bounds,
    get_nearby_businesses,
    validate_coordinates,
    get_rasauli_bounds,
)
from src.config import settings

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/bounds")
async def businesses_in_bounds(
    north: float = Query(..., description="North latitude"),
    south: float = Query(..., description="South latitude"),
    east: float = Query(..., description="East longitude"),
    west: float = Query(..., description="West longitude"),
):
    if south > north:
        raise HTTPException(status_code=400, detail="south must be <= north")
    if west > east:
        raise HTTPException(status_code=400, detail="west must be <= east")
    results = get_businesses_in_bounds(north, south, east, west)
    return {
        "data": results,
        "bounds": {"north": north, "south": south, "east": east, "west": west},
        "total": len(results),
        "rasauliBounds": get_rasauli_bounds(),
    }


@router.get("/nearby")
async def nearby_businesses(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(5.0, description="Radius in kilometers"),
    limit: int = Query(20, ge=1, le=50),
):
    if radius <= 0 or radius > 100:
        raise HTTPException(status_code=400, detail="radius must be between 0.1 and 100 km")
    results = get_nearby_businesses(lat, lng, radius_km=radius, limit=limit)
    return {
        "data": results,
        "center": {"lat": lat, "lng": lng},
        "radiusKm": radius,
        "total": len(results),
    }


@router.get("/center")
async def map_center():
    return {
        "latitude": settings.map_lat,
        "longitude": settings.map_lng,
        "zoom": settings.map_zoom,
        "areaName": settings.area_name,
        "areaBounds": get_rasauli_bounds(),
    }


@router.get("/validate-coordinates")
async def check_coordinates(
    lat: float = Query(..., description="Latitude to validate"),
    lng: float = Query(..., description="Longitude to validate"),
):
    return validate_coordinates(lat, lng)
