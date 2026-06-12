from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.data.loader import get_listing_by_id, get_all_listings

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewSubmission(BaseModel):
    author: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="", max_length=100)
    rating: float = Field(..., ge=0.5, le=5.0)
    text: str = Field(..., min_length=5, max_length=2000)
    email: Optional[str] = Field(default=None, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@router.get("")
async def list_all_reviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    all_reviews = []
    for biz in get_all_listings():
        for review in biz.get("reviews", []):
            all_reviews.append({
                "businessId": biz.get("id", ""),
                "businessName": biz.get("name", ""),
                **review,
            })
    total = len(all_reviews)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "total": total,
        "page": page,
        "perPage": per_page,
        "reviews": all_reviews[start:end],
    }


@router.get("/business/{business_id}")
async def get_reviews_for_business(business_id: str):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    reviews = biz.get("reviews", [])
    return {
        "businessId": business_id,
        "businessName": biz.get("name", ""),
        "total": len(reviews),
        "reviews": reviews,
    }
