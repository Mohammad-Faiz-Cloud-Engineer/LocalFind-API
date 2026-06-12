import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
LISTINGS_PATH = DATA_DIR / "listings.json"

_listings_cache: list[dict[str, Any]] | None = None


def load_listings() -> list[dict[str, Any]]:
    global _listings_cache
    if _listings_cache is not None:
        return _listings_cache
    if not LISTINGS_PATH.exists():
        logger.warning("listings.json not found at %s", LISTINGS_PATH)
        _listings_cache = []
        return _listings_cache
    try:
        with open(LISTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _listings_cache = data
        logger.info("Loaded %d businesses from listings.json", len(data))
        return _listings_cache
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load listings: %s", e)
        _listings_cache = []
        return _listings_cache


def get_all_listings() -> list[dict[str, Any]]:
    return load_listings()


def get_listing_by_id(business_id: str) -> dict[str, Any] | None:
    for biz in load_listings():
        if biz.get("id") == business_id:
            return biz
    return None


def get_categories() -> dict[str, dict[str, str | int]]:
    counts: dict[str, int] = {}
    for biz in load_listings():
        slug = biz.get("categorySlug", "other")
        name = biz.get("category", slug)
        if slug not in counts:
            counts[slug] = {"name": name, "count": 0, "slug": slug}
        counts[slug]["count"] += 1
    return counts


def get_listings_by_category(slug: str) -> list[dict[str, Any]]:
    return [b for b in load_listings() if b.get("categorySlug") == slug]


def get_featured_listings() -> list[dict[str, Any]]:
    return [b for b in load_listings() if b.get("featured")]


def get_verified_listings() -> list[dict[str, Any]]:
    return [b for b in load_listings() if b.get("verified")]


def reload_listings() -> None:
    global _listings_cache
    _listings_cache = None
    load_listings()
