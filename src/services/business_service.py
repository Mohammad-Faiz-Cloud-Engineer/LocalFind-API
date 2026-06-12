import math
from datetime import datetime, timezone
from typing import Any

from src.config import settings
from src.data.loader import (
    get_all_listings,
    get_listing_by_id,
)
from src.models import business_to_summary, normalize_business
from src.services.search_service import calculate_relevance, expand_search_query, parse_special_command, apply_special_command_filter, is_business_new, find_malls_with_matching_tenants
from src.utils.time_utils import get_business_status, IST_OFFSET


def get_listings(
    category: str | None = None,
    featured: bool | None = None,
    verified: bool | None = None,
    search: str | None = None,
    location: str | None = None,
    page: int = 1,
    per_page: int | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    status_filter: str | None = None,
    is_new: bool | None = None,
    lgbtq_friendly: bool | None = None,
    women_owned: bool | None = None,
) -> dict[str, Any]:
    if per_page is None:
        per_page = settings.items_per_page
    per_page = min(per_page, settings.items_per_page * settings.max_pages)
    listings = get_all_listings()
    if category:
        listings = [b for b in listings if b.get("categorySlug") == category.lower()]
    if featured is not None:
        listings = [b for b in listings if b.get("featured") == featured]
    if verified is not None:
        listings = [b for b in listings if b.get("verified") == verified]
    if lgbtq_friendly is not None:
        listings = [b for b in listings if b.get("lgbtqFriendly") == lgbtq_friendly]
    if women_owned is not None:
        listings = [b for b in listings if b.get("womenOwned") == women_owned]
    if location:
        loc_lower = location.strip().lower()
        listings = [b for b in listings if loc_lower in (b.get("address") or "").lower()]
    if status_filter == "open":
        listings = [b for b in listings if get_business_status(b).get("isOpen") is True]
    elif status_filter == "closed":
        listings = [b for b in listings if get_business_status(b).get("isOpen") is False]
    if is_new:
        ist_now = datetime.now(timezone.utc) + IST_OFFSET
        listings = [b for b in listings if is_business_new(b, ist_now)]
    if search:
        cmd = parse_special_command(search)
        if cmd:
            listings = apply_special_command_filter(listings, cmd)
            search_for = cmd.get("searchQuery")
            if search_for:
                expanded, _ = expand_search_query(search_for)
                search_terms = expanded.lower().split()
                scored = []
                for biz in listings:
                    score = calculate_relevance(biz, search_terms, search_for)
                    if score > 0:
                        scored.append((score, biz))
                mall_tenants = find_malls_with_matching_tenants(search_terms)
                existing_ids = {b.get("id") for _, b in scored}
                for mall in mall_tenants:
                    if mall.get("id") and mall["id"] not in existing_ids:
                        scored.append((50, mall))
                        existing_ids.add(mall["id"])
                scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
                listings = [b for _, b in scored]
        else:
            expanded, _ = expand_search_query(search)
            search_terms = expanded.lower().split()
            scored = []
            for biz in listings:
                score = calculate_relevance(biz, search_terms, search)
                if score > 0:
                    scored.append((score, biz))
            mall_tenants = find_malls_with_matching_tenants(search_terms)
            existing_ids = {b.get("id") for _, b in scored}
            for mall in mall_tenants:
                if mall.get("id") and mall["id"] not in existing_ids:
                    scored.append((50, mall))
                    existing_ids.add(mall["id"])
            scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
            listings = [b for _, b in scored]
    if sort_by:
        reverse = sort_order.lower() == "desc"
        if sort_by == "name":
            listings.sort(key=lambda b: (b.get("name") or "").lower(), reverse=reverse)
        elif sort_by == "rating":
            listings.sort(key=lambda b: b.get("rating") or 0, reverse=reverse)
        elif sort_by == "reviewCount":
            listings.sort(key=lambda b: b.get("reviewCount") or 0, reverse=reverse)
        elif sort_by == "addedDate":
            listings.sort(key=lambda b: b.get("addedDate") or "", reverse=reverse)
    else:
        listings.sort(key=lambda b: (not b.get("featured"), b.get("name") or ""))
    total = len(listings)
    total_pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    page_data = listings[start:end]
    return {
        "data": [business_to_summary(b) for b in page_data],
        "total": total,
        "page": page,
        "perPage": per_page,
        "totalPages": total_pages,
    }


def get_business_detail(business_id: str) -> dict[str, Any] | None:
    biz = get_listing_by_id(business_id)
    if not biz:
        return None
    detail = normalize_business(biz)
    coords = biz.get("coordinates", {})
    lat, lng = coords.get("lat"), coords.get("lng")
    detail["mapLinks"] = {}
    detail["mapLinks"]["googleMaps"] = biz.get("mapLink", "")
    if lat is not None and lng is not None:
        detail["mapLinks"]["openStreetMap"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=16"
        if not biz.get("mapLink"):
            detail["mapLinks"]["googleMaps"] = f"https://www.google.com/maps?q={lat},{lng}"
    upi_ids = biz.get("upiIds", [])
    upi_id = biz.get("upiId", "")
    upi_name = biz.get("upiName", "") or biz.get("name", "")
    all_upis = list(upi_ids) if upi_ids else ([upi_id] if upi_id else [])
    detail["upiLinks"] = []
    for uid in all_upis:
        if uid:
            detail["upiLinks"].append({
                "upiId": uid,
                "name": upi_name,
                "deepLink": f"upi://pay?pa={uid}&pn={upi_name}&cu=INR",
            })
    return detail


def get_related_businesses(business_id: str, limit: int = 4) -> list[dict[str, Any]]:
    biz = get_listing_by_id(business_id)
    if not biz:
        return []
    category = biz.get("categorySlug", "")
    related = [b for b in get_all_listings() if b.get("id") != business_id and b.get("categorySlug") == category]
    return [business_to_summary(b) for b in related[:limit]]


def get_business_reviews(business_id: str) -> list[dict[str, Any]]:
    biz = get_listing_by_id(business_id)
    if not biz:
        return []
    return biz.get("reviews", [])
