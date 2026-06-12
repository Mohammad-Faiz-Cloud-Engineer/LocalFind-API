import re
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query

from src.services.business_service import (
    get_listings,
    get_business_detail,
    get_related_businesses,
    get_business_reviews,
)
from src.services.status_service import get_status_for_business
from src.utils.time_utils import convert_to_12_hour
from src.data.loader import get_listing_by_id

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get("")
async def list_all_listings(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    featured: Optional[bool] = Query(None, description="Filter featured only"),
    verified: Optional[bool] = Query(None, description="Filter verified only"),
    search: Optional[str] = Query(None, description="Search query (supports /command syntax)"),
    location: Optional[str] = Query(None, description="Filter by address text (case-insensitive)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(6, ge=1, le=50, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Sort field: name, rating, reviewCount, addedDate"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    status: Optional[str] = Query(None, description="Filter by real-time status: open or closed"),
    is_new: Optional[bool] = Query(None, description="Filter new businesses (added within 7 days)"),
    lgbtq_friendly: Optional[bool] = Query(None, description="Filter LGBTQ+ friendly"),
    women_owned: Optional[bool] = Query(None, description="Filter women-owned"),
):
    return get_listings(
        category=category,
        featured=featured,
        verified=verified,
        search=search,
        location=location,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        status_filter=status,
        is_new=is_new,
        lgbtq_friendly=lgbtq_friendly,
        women_owned=women_owned,
    )


@router.get("/{business_id}")
async def get_business(business_id: str):
    detail = get_business_detail(business_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    return detail


@router.get("/{business_id}/related")
async def get_related(business_id: str, limit: int = Query(4, ge=1, le=20)):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    return get_related_businesses(business_id, limit=limit)


@router.get("/{business_id}/status")
async def get_business_status_route(business_id: str):
    status = get_status_for_business(business_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    return status


@router.get("/{business_id}/reviews")
async def get_business_reviews_route(business_id: str):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    reviews = get_business_reviews(business_id)
    return {
        "businessId": business_id,
        "businessName": biz.get("name", ""),
        "total": len(reviews),
        "reviews": reviews,
    }


@router.get("/{business_id}/map-link")
async def get_business_map_link(business_id: str):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    coords = biz.get("coordinates", {})
    lat, lng = coords.get("lat"), coords.get("lng")
    links = {
        "googleMaps": biz.get("mapLink", ""),
        "openStreetMap": "",
        "coordinates": {"lat": lat, "lng": lng},
    }
    if lat is not None and lng is not None:
        links["openStreetMap"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=16"
    return {
        "businessId": business_id,
        "businessName": biz.get("name", ""),
        **links,
    }


@router.get("/{business_id}/upi-link")
async def get_business_upi_link(business_id: str):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    upi_ids = biz.get("upiIds", [])
    upi_id = biz.get("upiId", "")
    upi_name = biz.get("upiName", "") or biz.get("name", "")
    all_upis = list(upi_ids) if upi_ids else ([upi_id] if upi_id else [])
    pay_links = []
    for uid in all_upis:
        if uid:
            pay_links.append({
                "upiId": uid,
                "name": upi_name,
                "deepLink": f"upi://pay?pa={uid}&pn={upi_name}&cu=INR",
            })
    return {
        "businessId": business_id,
        "businessName": biz.get("name", ""),
        "totalUPIs": len(pay_links),
        "payLinks": pay_links,
    }


@router.get("/{business_id}/appointment-message")
async def get_appointment_message(
    business_id: str,
    time: str = Query("10:00", description="Appointment time in HH:MM format"),
):
    biz = get_listing_by_id(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    category = (biz.get("category") or "").lower()
    biz_name = biz.get("name", "")
    time_12h = convert_to_12_hour(time)
    if any(kw in category for kw in ["hospital", "clinic", "healthcare", "pharmacy"]):
        message = f"Hello, I would like to book an appointment for {time_12h}. My name is [Your Name]. Please let me know if the slot is available."
    elif any(kw in category for kw in ["salon", "spa", "beauty"]):
        message = f"Hi, I'd like to book a {time_12h} appointment for your services. My name is [Your Name]. Thank you!"
    elif any(kw in category for kw in ["gym", "fitness"]):
        message = f"Hello! I'm interested in visiting at {time_12h}. My name is [Your Name]. Please let me know if this works."
    elif any(kw in category for kw in ["restaurant", "cafe", "food"]):
        message = f"Hi, I'd like to make a reservation for {time_12h} for [number] people. My name is [Your Name]. Thanks!"
    elif any(kw in category for kw in ["education", "school", "college"]):
        message = f"Hello, I would like to schedule a meeting/visit at {time_12h}. My name is [Your Name]. Please let me know."
    elif any(kw in category for kw in ["service", "csc", "government"]):
        message = f"Hi, I need to visit for services around {time_12h}. My name is [Your Name]. Is this a good time?"
    else:
        message = f"Hello, I would like to schedule a visit/appointment at {time_12h}. My name is [Your Name]. Please let me know."
    contacts = []
    phone = biz.get("phone", "")
    whatsapp = biz.get("whatsapp", "")
    if phone:
        contacts.append({"type": "phone", "number": phone, "name": biz.get("phoneName", "")})
    if whatsapp and whatsapp != phone:
        contacts.append({"type": "whatsapp", "number": whatsapp, "name": biz.get("whatsappName", "")})
    wa_number = re.sub(r"[^\d]", "", whatsapp) if whatsapp else ""
    wa_link = f"https://wa.me/{wa_number}?text={quote(message)}" if wa_number else None
    return {
        "businessId": business_id,
        "businessName": biz_name,
        "time": time,
        "timeFormatted": time_12h,
        "message": message,
        "whatsappDeepLink": wa_link,
        "contacts": contacts,
    }

