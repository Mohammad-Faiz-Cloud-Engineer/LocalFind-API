import logging
import os
import sys

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("localfind-api")

from src.config import settings
from src.data.loader import load_listings, get_all_listings, get_categories
from src.middleware.error_handler import setup_error_handlers
from src.middleware.rate_limit import rate_limiter_middleware
from src.routes.listings import router as listings_router
from src.routes.categories import router as categories_router
from src.routes.search import router as search_router
from src.routes.status import router as status_router
from src.routes.reviews import router as reviews_router
from src.routes.map import router as map_router
from src.routes.analytics import router as analytics_router
from src.routes.contact import router as contact_router
from src.routes.donation import router as donation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_listings()
    count = len(get_all_listings())
    cats = get_categories()
    logger.info("LocalFind API v%s started with %d businesses in %d categories", settings.app_version, count, len(cats))
    yield

app = FastAPI(
    title=settings.site_name,
    description=f"{settings.tagline} - API for {settings.area_name}",
    version=settings.app_version,
    contact={
        "name": "LocalFind Team",
        "email": settings.contact_email,
        "url": "https://localfind.com",
    },
    license_info={
        "name": "BSD 2-Clause License",
        "url": "https://opensource.org/licenses/BSD-2-Clause",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limiter_middleware)

setup_error_handlers(app)

app.include_router(listings_router, prefix=settings.api_prefix)
app.include_router(categories_router, prefix=settings.api_prefix)
app.include_router(search_router, prefix=settings.api_prefix)
app.include_router(status_router, prefix=settings.api_prefix)
app.include_router(reviews_router, prefix=settings.api_prefix)
app.include_router(map_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(contact_router, prefix=settings.api_prefix)
app.include_router(donation_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.site_name,
        "version": settings.app_version,
        "tagline": settings.tagline,
        "area": settings.area_name,
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "listings": f"{settings.api_prefix}/listings",
            "listings_detail": f"{settings.api_prefix}/listings/{{business_id}}",
            "listings_related": f"{settings.api_prefix}/listings/{{id}}/related",
            "listings_status": f"{settings.api_prefix}/listings/{{id}}/status",
            "listings_reviews": f"{settings.api_prefix}/listings/{{id}}/reviews",
            "listings_map_link": f"{settings.api_prefix}/listings/{{id}}/map-link",
            "listings_upi_link": f"{settings.api_prefix}/listings/{{id}}/upi-link",
            "listings_appointment": f"{settings.api_prefix}/listings/{{id}}/appointment-message",
            "categories": f"{settings.api_prefix}/categories",
            "search": f"{settings.api_prefix}/search?q=<query>",
            "search_commands": f"{settings.api_prefix}/search/commands",
            "search_aliases": f"{settings.api_prefix}/search/aliases",
            "status": f"{settings.api_prefix}/status",
            "status_open": f"{settings.api_prefix}/status/open",
            "reviews": f"{settings.api_prefix}/reviews",
            "reviews_business": f"{settings.api_prefix}/reviews/business/{{id}}",
            "map_bounds": f"{settings.api_prefix}/map/bounds?north=&south=&east=&west=",
            "map_nearby": f"{settings.api_prefix}/map/nearby?lat=&lng=&radius=",
            "map_center": f"{settings.api_prefix}/map/center",
            "map_validate": f"{settings.api_prefix}/map/validate-coordinates",
            "analytics_view": f"{settings.api_prefix}/analytics/view/{{id}}",
            "analytics_popular": f"{settings.api_prefix}/analytics/popular",
            "analytics_stats": f"{settings.api_prefix}/analytics/stats",
            "contact_submit": f"{settings.api_prefix}/contact/submit",
            "donation": f"{settings.api_prefix}/donation",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "businesses": len(get_all_listings()),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("app:app", host=host, port=port, reload=False, log_level="info")