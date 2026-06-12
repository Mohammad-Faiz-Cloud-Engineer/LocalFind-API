from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from src.data.loader import get_all_listings, get_listing_by_id

_view_counts: dict[str, int] = defaultdict(int)
_view_history: list[dict[str, Any]] = []


def record_view(business_id: str, ip: str | None = None, user_agent: str | None = None) -> bool:
    biz = get_listing_by_id(business_id)
    if not biz:
        return False
    _view_counts[business_id] += 1
    _view_history.append({
        "businessId": business_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "userAgent": user_agent,
    })
    if len(_view_history) > 10000:
        _view_history[:5000] = []
    return True


def get_view_count(business_id: str) -> int:
    return _view_counts.get(business_id, 0)


def get_popular_businesses(limit: int = 10) -> list[dict[str, Any]]:
    sorted_counts = sorted(_view_counts.items(), key=lambda x: -x[1])
    results = []
    for biz_id, count in sorted_counts[:limit]:
        biz = get_listing_by_id(biz_id)
        if biz:
            results.append({
                "id": biz_id,
                "name": biz.get("name", ""),
                "category": biz.get("category", ""),
                "views": count,
            })
    return results


def get_total_views() -> int:
    return sum(_view_counts.values())


def get_stats() -> dict[str, Any]:
    total_listings = len(get_all_listings())
    total_views = get_total_views()
    popular = get_popular_businesses(5)
    return {
        "totalListings": total_listings,
        "totalViews": total_views,
        "uniqueBusinessesViewed": len(_view_counts),
        "popular": popular,
    }


def reset_stats() -> None:
    _view_counts.clear()
    _view_history.clear()
