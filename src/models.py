from typing import Any, Optional

from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lng: float


class Hours(BaseModel):
    open: str = "00:00"
    close: str = "00:00"
    open2: Optional[str] = None
    close2: Optional[str] = None


class Review(BaseModel):
    id: str = ""
    author: str = ""
    role: str = ""
    rating: float = 0.0
    date: str = ""
    text: str = ""
    verified: bool = False


class BusinessBase(BaseModel):
    id: str
    name: str
    category: str
    categorySlug: str
    featured: bool = False
    verified: bool = False
    status: str = "open"
    rating: float = 0.0
    reviewCount: int = 0
    coordinates: Coordinates
    address: str = ""
    mapLink: str = ""
    phone: str = ""
    phoneName: str = ""
    phoneSecondary: Optional[str] = None
    phoneSecondaryName: Optional[str] = None
    phoneThird: Optional[str] = None
    phoneThirdName: Optional[str] = None
    phoneFourth: Optional[str] = None
    phoneFourthName: Optional[str] = None
    email: str = ""
    website: str = ""
    whatsapp: str = ""
    whatsappName: str = ""
    whatsappSecondary: Optional[str] = None
    whatsappSecondaryName: Optional[str] = None
    whatsappThird: Optional[str] = None
    whatsappThirdName: Optional[str] = None
    whatsappFourth: Optional[str] = None
    whatsappFourthName: Optional[str] = None
    instagram: str = ""
    youtube: str = ""
    linkedin: str = ""
    facebook: str = ""
    hours: dict[str, Hours]
    description: str = ""
    tags: list[str] = []
    addedDate: str = ""
    upiId: str = ""
    upiName: str = ""
    upiIds: list[str] = []
    bloodDonor: str = ""
    onlineOrder: str = ""
    zomato: str = ""
    magicpin: str = ""
    menu: str = ""
    bookTable: str = ""
    orderOnline: str = ""
    bookMyShow: str = ""
    districtIn: str = ""
    lgbtqFriendly: bool = False
    womenOwned: bool = False
    disableAppointment: bool = False
    locatedInMall: Optional[str] = None
    tenants: list[str] = []
    reviews: list[Review] = []

    model_config = {"extra": "ignore"}


class BusinessSummary(BaseModel):
    id: str
    name: str
    category: str
    categorySlug: str
    featured: bool
    verified: bool
    status: str
    rating: float
    reviewCount: int
    coordinates: Coordinates
    address: str
    phone: str
    whatsapp: str
    tags: list[str]
    addedDate: str
    bloodDonor: str = ""
    lgbtqFriendly: bool = False
    womenOwned: bool = False


class BusinessStatus(BaseModel):
    businessId: str
    businessName: str
    isOpen: Optional[bool] = None
    message: str = ""
    cssClass: str = "status-unknown"
    nextChange: Optional[str] = None
    minutesUntilClose: Optional[int] = None
    minutesUntilOpen: Optional[int] = None
    showCountdown: bool = False
    currentTime: str = ""
    todayHours: Optional[dict[str, str]] = None


class CategoryInfo(BaseModel):
    slug: str
    name: str
    count: int


class SearchResult(BaseModel):
    query: str
    expandedQuery: Optional[str] = None
    results: list[BusinessSummary]
    total: int
    page: int
    perPage: int


class PaginatedResponse(BaseModel):
    data: list[BusinessSummary]
    total: int
    page: int
    perPage: int
    totalPages: int


class ErrorResponse(BaseModel):
    error: str
    message: str
    statusCode: int


class MapBoundsResponse(BaseModel):
    data: list[BusinessSummary]
    bounds: dict[str, float]
    total: int


class PopularBusiness(BaseModel):
    id: str
    name: str
    category: str
    views: int


def business_to_summary(biz: dict[str, Any]) -> dict[str, Any]:
    coords = biz.get("coordinates", {})
    return {
        "id": biz.get("id", ""),
        "name": biz.get("name", ""),
        "category": biz.get("category", ""),
        "categorySlug": biz.get("categorySlug", ""),
        "featured": biz.get("featured", False),
        "verified": biz.get("verified", False),
        "status": biz.get("status", "open"),
        "rating": biz.get("rating", 0.0),
        "reviewCount": biz.get("reviewCount", 0),
        "coordinates": {"lat": coords.get("lat", 0), "lng": coords.get("lng", 0)},
        "address": biz.get("address", ""),
        "phone": biz.get("phone", ""),
        "whatsapp": biz.get("whatsapp", ""),
        "tags": biz.get("tags", []),
        "addedDate": biz.get("addedDate", ""),
        "bloodDonor": biz.get("bloodDonor", ""),
        "lgbtqFriendly": biz.get("lgbtqFriendly", False),
        "womenOwned": biz.get("womenOwned", False),
    }


def normalize_business(biz: dict[str, Any]) -> dict[str, Any]:
    hours_raw = biz.get("hours", {})
    hours: dict[str, Any] = {}
    for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        if day in hours_raw:
            h = hours_raw[day]
            hours[day] = {
                "open": h.get("open", "00:00"),
                "close": h.get("close", "00:00"),
            }
            if h.get("open2") is not None:
                hours[day]["open2"] = h["open2"]
            if h.get("close2") is not None:
                hours[day]["close2"] = h["close2"]
        else:
            hours[day] = {"open": "00:00", "close": "00:00"}
    reviews_raw = biz.get("reviews", [])
    reviews = []
    for r in reviews_raw:
        reviews.append({
            "id": r.get("id", ""),
            "author": r.get("author", ""),
            "role": r.get("role", ""),
            "rating": r.get("rating", 0.0),
            "date": r.get("date", ""),
            "text": r.get("text", ""),
            "verified": r.get("verified", False),
        })
    return {
        "id": biz.get("id", ""),
        "name": biz.get("name", ""),
        "category": biz.get("category", ""),
        "categorySlug": biz.get("categorySlug", ""),
        "featured": biz.get("featured", False),
        "verified": biz.get("verified", False),
        "status": biz.get("status", "open"),
        "rating": biz.get("rating", 0.0),
        "reviewCount": biz.get("reviewCount", 0),
        "coordinates": {
            "lat": biz.get("coordinates", {}).get("lat", 0),
            "lng": biz.get("coordinates", {}).get("lng", 0),
        },
        "address": biz.get("address", ""),
        "mapLink": biz.get("mapLink", ""),
        "phone": biz.get("phone", ""),
        "phoneName": biz.get("phoneName", ""),
        "phoneSecondary": biz.get("phoneSecondary"),
        "phoneSecondaryName": biz.get("phoneSecondaryName"),
        "phoneThird": biz.get("phoneThird"),
        "phoneThirdName": biz.get("phoneThirdName"),
        "phoneFourth": biz.get("phoneFourth"),
        "phoneFourthName": biz.get("phoneFourthName"),
        "email": biz.get("email", ""),
        "website": biz.get("website", ""),
        "whatsapp": biz.get("whatsapp", ""),
        "whatsappName": biz.get("whatsappName", ""),
        "whatsappSecondary": biz.get("whatsappSecondary"),
        "whatsappSecondaryName": biz.get("whatsappSecondaryName"),
        "whatsappThird": biz.get("whatsappThird"),
        "whatsappThirdName": biz.get("whatsappThirdName"),
        "whatsappFourth": biz.get("whatsappFourth"),
        "whatsappFourthName": biz.get("whatsappFourthName"),
        "instagram": biz.get("instagram", ""),
        "youtube": biz.get("youtube", ""),
        "linkedin": biz.get("linkedin", ""),
        "facebook": biz.get("facebook", ""),
        "hours": hours,
        "description": biz.get("description", ""),
        "tags": biz.get("tags", []),
        "addedDate": biz.get("addedDate", ""),
        "upiId": biz.get("upiId", ""),
        "upiName": biz.get("upiName", ""),
        "upiIds": biz.get("upiIds", []),
        "bloodDonor": biz.get("bloodDonor", ""),
        "onlineOrder": biz.get("onlineOrder", ""),
        "zomato": biz.get("zomato", ""),
        "magicpin": biz.get("magicpin", ""),
        "menu": biz.get("menu", ""),
        "bookTable": biz.get("bookTable", ""),
        "orderOnline": biz.get("orderOnline", ""),
        "bookMyShow": biz.get("bookMyShow", ""),
        "districtIn": biz.get("districtIn", ""),
        "lgbtqFriendly": biz.get("lgbtqFriendly", False),
        "womenOwned": biz.get("womenOwned", False),
        "disableAppointment": biz.get("disableAppointment", False),
        "locatedInMall": biz.get("locatedInMall"),
        "tenants": biz.get("tenants", []),
        "reviews": reviews,
    }
