from fastapi import APIRouter

from src.services.status_service import get_all_statuses, get_open_businesses
from src.data.loader import get_all_listings

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("")
async def all_statuses():
    return {
        "total": len(get_all_listings()),
        "statuses": get_all_statuses(),
    }


@router.get("/open")
async def open_businesses():
    open_biz = get_open_businesses()
    return {
        "total": len(open_biz),
        "businesses": open_biz,
    }
