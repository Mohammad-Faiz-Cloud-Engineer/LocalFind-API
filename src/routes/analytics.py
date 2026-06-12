from fastapi import APIRouter, HTTPException, Query, Request

from src.services.analytics_service import (
    record_view,
    get_view_count,
    get_popular_businesses,
    get_stats,
)
from src.data.loader import get_listing_by_id

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/view/{business_id}")
async def track_view(business_id: str, request: Request):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    recorded = record_view(business_id, ip=ip, user_agent=ua)
    return {
        "success": recorded,
        "businessId": business_id,
        "businessName": biz.get("name", ""),
        "totalViews": get_view_count(business_id),
    }


@router.get("/view/{business_id}")
async def get_views(business_id: str):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    return {
        "businessId": business_id,
        "businessName": biz.get("name", ""),
        "views": get_view_count(business_id),
    }


@router.get("/popular")
async def popular_businesses(limit: int = Query(10, ge=1, le=50)):
    return {
        "total": limit,
        "businesses": get_popular_businesses(limit=limit),
    }


@router.get("/stats")
async def analytics_stats():
    return get_stats()
