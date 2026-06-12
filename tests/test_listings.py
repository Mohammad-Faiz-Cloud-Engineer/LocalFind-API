import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.loader import load_listings, get_all_listings, get_listing_by_id, get_categories


def test_load_listings():
    listings = load_listings()
    assert isinstance(listings, list)
    assert len(listings) > 0


def test_get_all_listings():
    listings = get_all_listings()
    assert len(listings) >= 35


def test_get_listing_by_id():
    biz = get_listing_by_id("aman-garments")
    assert biz is not None
    assert biz["name"] == "Aman Garments"
    assert biz["categorySlug"] == "fashion"


def test_get_listing_by_id_not_found():
    biz = get_listing_by_id("nonexistent-business")
    assert biz is None


def test_get_categories():
    cats = get_categories()
    assert len(cats) > 0
    for slug, info in cats.items():
        assert "name" in info
        assert "count" in info
        assert info["count"] > 0


def test_business_fields():
    biz = get_listing_by_id("aman-garments")
    required = ["id", "name", "category", "categorySlug", "coordinates", "hours", "tags"]
    for field in required:
        assert field in biz, f"Missing field: {field}"
    assert "lat" in biz["coordinates"]
    assert "lng" in biz["coordinates"]


def test_business_is_business_summary():
    from src.models import business_to_summary
    biz = get_listing_by_id("aman-garments")
    summary = business_to_summary(biz)
    assert "id" in summary
    assert "name" in summary
    assert "category" in summary
    assert "coordinates" in summary
    assert "phone" in summary


def test_business_normalize():
    from src.models import normalize_business
    biz = get_listing_by_id("aman-garments")
    norm = normalize_business(biz)
    assert "hours" in norm
    assert "mon" in norm["hours"]
    assert "reviews" in norm
    assert "upiIds" in norm
    assert "phoneSecondary" in norm


if __name__ == "__main__":
    test_load_listings()
    test_get_all_listings()
    test_get_listing_by_id()
    test_get_listing_by_id_not_found()
    test_get_categories()
    test_business_fields()
    test_business_is_business_summary()
    test_business_normalize()
    print("All listing tests passed!")
