from typing import Any

from src.data.loader import get_all_listings, get_listing_by_id
from src.utils.time_utils import get_business_status, get_ist_time


def get_status_for_business(business_id: str) -> dict[str, Any] | None:
    biz = get_listing_by_id(business_id)
    if not biz:
        return None
    return _compute_status_response(biz)


def _compute_status_response(biz: dict[str, Any]) -> dict[str, Any]:
    status = get_business_status(biz)
    ist = get_ist_time()
    day_hours = biz.get("hours", {}).get(ist["day"])
    today_hours = None
    if day_hours:
        today_hours = {
            "open": day_hours.get("open", ""),
            "close": day_hours.get("close", ""),
        }
    return {
        "businessId": biz.get("id", ""),
        "businessName": biz.get("name", ""),
        **status,
        "currentTime": f"{ist['hours']:02d}:{ist['minutes']:02d}",
        "todayHours": today_hours,
    }


def get_all_statuses() -> list[dict[str, Any]]:
    return [_compute_status_response(biz) for biz in get_all_listings()]


def get_open_businesses() -> list[dict[str, Any]]:
    open_list = []
    for biz in get_all_listings():
        resp = _compute_status_response(biz)
        if resp.get("isOpen"):
            resp["category"] = biz.get("category", "")
            resp["categorySlug"] = biz.get("categorySlug", "")
            open_list.append(resp)
    return open_list
