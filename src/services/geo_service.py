import math
from typing import Any

from src.data.loader import get_all_listings
from src.models import business_to_summary

RASAULI_BOUNDS = {
    "north": 26.95,
    "south": 26.88,
    "east": 81.30,
    "west": 81.15,
}


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_in_rasauli_area(lat: float, lng: float) -> bool:
    b = RASAULI_BOUNDS
    return b["south"] <= lat <= b["north"] and b["west"] <= lng <= b["east"]


def get_rasauli_bounds() -> dict[str, float]:
    return dict(RASAULI_BOUNDS)


def get_businesses_in_bounds(
    north: float, south: float, east: float, west: float
) -> list[dict[str, Any]]:
    results = []
    for biz in get_all_listings():
        coords = biz.get("coordinates", {})
        lat = coords.get("lat")
        lng = coords.get("lng")
        if lat is None or lng is None:
            continue
        if south <= lat <= north and west <= lng <= east:
            results.append(biz)
    return [business_to_summary(b) for b in results]


def get_nearby_businesses(
    lat: float, lng: float, radius_km: float = 5.0, limit: int = 20
) -> list[dict[str, Any]]:
    radius_m = radius_km * 1000
    scored = []
    for biz in get_all_listings():
        coords = biz.get("coordinates", {})
        biz_lat = coords.get("lat")
        biz_lng = coords.get("lng")
        if biz_lat is None or biz_lng is None:
            continue
        distance = haversine(lat, lng, biz_lat, biz_lng)
        if distance <= radius_m:
            scored.append((distance, biz))
    scored.sort(key=lambda x: x[0])
    results = []
    for dist, biz in scored[:limit]:
        summary = business_to_summary(biz)
        summary["distance"] = round(dist, 1)
        summary["distanceKm"] = round(dist / 1000, 2)
        results.append(summary)
    return results


def validate_coordinates(lat: float, lng: float) -> dict[str, Any]:
    in_area = is_in_rasauli_area(lat, lng)
    nearest = None
    if not in_area:
        nearest_dist = float("inf")
        for biz in get_all_listings():
            coords = biz.get("coordinates", {})
            bl, bn = coords.get("lat"), coords.get("lng")
            if bl is not None and bn is not None:
                d = haversine(lat, lng, bl, bn)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest = {"name": biz.get("name"), "lat": bl, "lng": bn, "distance": round(d / 1000, 2)}
    return {
        "valid": in_area,
        "inRasauliArea": in_area,
        "bounds": RASAULI_BOUNDS,
        "nearestBusiness": nearest,
    }
