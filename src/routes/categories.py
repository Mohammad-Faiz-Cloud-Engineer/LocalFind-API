from fastapi import APIRouter, HTTPException, Query

from src.data.loader import get_categories, get_listings_by_category
from src.models import business_to_summary

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
async def list_categories():
    cats = get_categories()
    return {
        "total": len(cats),
        "categories": sorted(cats.values(), key=lambda x: -x["count"]),
    }


@router.get("/{category_slug}")
async def get_category_listings(
    category_slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
):
    biz_list = get_listings_by_category(category_slug)
    if not biz_list:
        raise HTTPException(status_code=404, detail=f"Category '{category_slug}' not found")
    total = len(biz_list)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "category": biz_list[0].get("category", category_slug),
        "slug": category_slug,
        "total": total,
        "page": page,
        "perPage": per_page,
        "data": [business_to_summary(b) for b in biz_list[start:end]],
    }
