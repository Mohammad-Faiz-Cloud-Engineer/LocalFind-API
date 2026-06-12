import re
from datetime import datetime, timezone
from typing import Any

from src.data.loader import get_all_listings
from src.models import business_to_summary
from src.utils.search_aliases import expand_search_query
from src.utils.text_normalizer import matches_search_term
from src.utils.time_utils import get_business_status, IST_OFFSET


COMMAND_MAP = {
    "open": {"field": "isOpen", "label": "Open Now"},
    "closed": {"field": "isOpen", "value": False, "label": "Closed Now"},
    "new": {"field": "isNew", "label": "New Businesses"},
    "featured": {"field": "featured", "value": True, "label": "Featured"},
    "verified": {"field": "verified", "value": True, "label": "Verified"},
    "lgbtq+": {"field": "lgbtqFriendly", "value": True, "label": "LGBTQ+ Friendly"},
    "lgbtq": {"field": "lgbtqFriendly", "value": True, "label": "LGBTQ+ Friendly"},
    "women-owned": {"field": "womenOwned", "value": True, "label": "Women Owned"},
    "women": {"field": "womenOwned", "value": True, "label": "Women Owned"},
}


def parse_special_command(query: str) -> dict | None:
    if not query or not isinstance(query, str):
        return None
    q = query.strip().lower()
    if len(q) > 200:
        return None
    if not q.startswith("/"):
        return None
    if len(q) < 2:
        return None
    parts = q.split(maxsplit=1)
    cmd_part = parts[0][1:]
    search_part = parts[1].strip()[:100] if len(parts) > 1 else None
    if not re.match(r"^[a-z0-9\-+]+$", cmd_part):
        return None
    if len(cmd_part) > 20:
        return None
    cmd_info = COMMAND_MAP.get(cmd_part)
    if not cmd_info:
        return None
    return {
        "property": cmd_info["field"],
        "value": cmd_info.get("value", True),
        "label": cmd_info["label"],
        "searchQuery": search_part,
    }


def apply_special_command_filter(listings: list[dict], cmd: dict) -> list[dict]:
    prop = cmd["property"]
    value = cmd["value"]
    if prop == "isNew":
        ist_now = datetime.now(timezone.utc) + IST_OFFSET
        return [
            b for b in listings
            if is_business_new(b, ist_now)
        ]
    elif prop == "isOpen":
        wanted_open = value
        results = []
        for b in listings:
            status = get_business_status(b)
            if status.get("isOpen") is wanted_open:
                results.append(b)
        return results
    else:
        return [b for b in listings if b.get(prop) == value]


def is_business_new(business: dict, now=None) -> bool:
    if now is None:
        now = datetime.now(timezone.utc) + IST_OFFSET
    added = business.get("addedDate")
    if not added:
        return False
    try:
        added_date = datetime.strptime(added, "%Y-%m-%d")
        delta = now - added_date.replace(tzinfo=now.tzinfo) if now.tzinfo else now - added_date
        return delta.days < 7
    except (ValueError, TypeError):
        return False


def find_malls_with_matching_tenants(search_terms: list[str]) -> list[dict]:
    if not search_terms:
        return []
    listings = get_all_listings()
    matching_ids = set()
    for biz in listings:
        name = (biz.get("name") or "").lower()
        category = (biz.get("category") or "").lower()
        tags = [t.lower() for t in biz.get("tags", [])]
        for term in search_terms:
            if term in name or term in category or any(term in t for t in tags):
                matching_ids.add(biz["id"])
                break
    mall_results = []
    seen_ids = set()
    for mall in listings:
        tenants = mall.get("tenants", [])
        if not tenants or not isinstance(tenants, list):
            continue
        if any(tid in matching_ids for tid in tenants):
            if mall.get("id") and mall["id"] not in seen_ids:
                seen_ids.add(mall["id"])
                mall_results.append(mall)
    return mall_results


def calculate_relevance(
    business: dict,
    search_terms: list[str],
    original_query: str,
) -> int:
    if not business or not isinstance(business, dict):
        return 0
    if not search_terms:
        return 0
    if not original_query:
        return 0
    name = (business.get("name") or "").lower()
    description = (business.get("description") or "").lower()
    category = (business.get("category") or "").lower()
    category_slug = (business.get("categorySlug") or "").lower()
    tags = [(t or "").lower() for t in business.get("tags", [])]
    biz_id = (business.get("id") or "").lower()
    query_lower = original_query.strip().lower()
    score = 0
    has_match = False

    if biz_id == query_lower:
        score += 1000
        has_match = True
    if name == query_lower:
        score += 1000
        has_match = True
    if name.startswith(query_lower):
        score += 500
        has_match = True
    if query_lower in name:
        score += 300
        has_match = True
    if category == query_lower or category_slug == query_lower:
        score += 200
        has_match = True
    if query_lower in category or query_lower in category_slug:
        score += 150
        has_match = True
    for tag in tags:
        if tag == query_lower:
            score += 100
            has_match = True
        elif query_lower in tag:
            score += 50
            has_match = True
    if query_lower in description:
        score += 10
        has_match = True

    for term in search_terms:
        term = term.strip().lower()
        if not term:
            continue
        if term in name:
            score += 15
            has_match = True
        if name.startswith(term):
            score += 8
            has_match = True
        if term in tags:
            score += 10
            has_match = True
        if term in category or term in category_slug:
            score += 6
            has_match = True
        if term in description:
            score += 3
            has_match = True
        if term in biz_id:
            score += 12
            has_match = True
        if matches_search_term(business.get("address"), term):
            score += 2
            has_match = True

    if has_match:
        if business.get("featured"):
            score += 5
        if business.get("verified"):
            score += 5
        try:
            rating = float(business.get("rating") or 0)
            if 0 <= rating <= 5:
                score += int(rating * 2)
        except (ValueError, TypeError):
            pass

    return score


def score_and_rank_listings(
    listings: list[dict],
    search_terms: list[str],
    original_query: str,
) -> list[dict]:
    """Score, filter, add mall tenants, and sort listings by relevance."""
    scored: list[tuple[int, dict]] = []
    if search_terms:
        for biz in listings:
            score = calculate_relevance(biz, search_terms, original_query)
            if score > 0:
                scored.append((score, biz))
    else:
        for biz in listings:
            score = 0
            if biz.get("featured"):
                score += 1
            if biz.get("verified"):
                score += 1
            scored.append((score, biz))
    mall_tenants = find_malls_with_matching_tenants(search_terms) if search_terms else []
    existing_ids = {b.get("id") for _, b in scored}
    for mall in mall_tenants:
        if mall.get("id") and mall["id"] not in existing_ids:
            scored.append((50, mall))
            existing_ids.add(mall["id"])
    scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
    return [b for _, b in scored]


def search_businesses(
    query: str,
    page: int = 1,
    per_page: int = 20,
    status_filter: str | None = None,
    is_new: bool | None = None,
    lgbtq_friendly: bool | None = None,
    women_owned: bool | None = None,
) -> dict[str, Any]:
    cmd = parse_special_command(query)
    expanded_query, matched_alias = expand_search_query(query)
    search_terms = expanded_query.lower().split()
    listings = get_all_listings()
    if cmd:
        listings = apply_special_command_filter(listings, cmd)
        if cmd.get("searchQuery"):
            sq, _ = expand_search_query(cmd["searchQuery"])
            search_terms = sq.lower().split()
        else:
            search_terms = []
    if status_filter == "open":
        listings = [b for b in listings if get_business_status(b).get("isOpen") is True]
    elif status_filter == "closed":
        listings = [b for b in listings if get_business_status(b).get("isOpen") is False]
    if is_new:
        ist_now = datetime.now(timezone.utc) + IST_OFFSET
        listings = [b for b in listings if is_business_new(b, ist_now)]
    if lgbtq_friendly is not None:
        listings = [b for b in listings if b.get("lgbtqFriendly") == lgbtq_friendly]
    if women_owned is not None:
        listings = [b for b in listings if b.get("womenOwned") == women_owned]
    ranked = score_and_rank_listings(listings, search_terms, query)
    results = [business_to_summary(b) for b in ranked]
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    cmd_label = cmd["label"] if cmd else None
    return {
        "query": query,
        "expandedQuery": expanded_query if expanded_query != query else None,
        "matchedAlias": matched_alias,
        "activeCommand": cmd_label,
        "results": results[start:end],
        "total": total,
        "page": page,
        "perPage": per_page,
    }
