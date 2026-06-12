---
title: LocalFind API
emoji: 🏪
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# LocalFind API

> Discover Everything Around You — API for Rasauli, Barabanki, Uttar Pradesh

A production-ready REST API that powers the LocalFind business discovery platform. Serves 40+ local businesses with full-text search, real-time open/closed status, geographic queries, reviews, analytics, and more.

## Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
  - [Root & Health](#root--health)
  - [Listings](#listings)
  - [Categories](#categories)
  - [Search](#search)
  - [Business Status](#business-status)
  - [Reviews](#reviews)
  - [Map & Geography](#map--geography)
  - [Analytics](#analytics)
  - [Contact](#contact)
- [Authentication](#authentication)
- [Pagination](#pagination)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Deployment](#deployment)
  - [HuggingFace Spaces (Recommended)](#huggingface-spaces-recommended)
  - [Local Development](#local-development)
  - [Docker](#docker)
  - [Production Considerations](#production-considerations)
- [Data Model](#data-model)
- [Architecture](#architecture)
- [Testing](#testing)
- [FAQ](#faq)

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### 1. Clone and Enter Project Directory

```bash
cd LocalFind-API
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

```bash
python app.py
```

The API will start at **http://localhost:7860**.

### 4. Explore Interactive Docs

Open your browser and go to **http://localhost:7860/docs** — FastAPI's interactive Swagger UI lets you test every endpoint.

---

## API Endpoints

### Root & Health

#### `GET /`

Returns API metadata and a list of all available endpoints.

```bash
curl http://localhost:7860/
```

**Response:**
```json
{
  "name": "LocalFind",
  "version": "4.3.7",
  "tagline": "Discover Everything Around You",
  "area": "Rasauli, Barabanki, Uttar Pradesh",
  "documentation": "/docs",
  "openapi": "/openapi.json",
  "endpoints": {
    "listings": "/api/v1/listings",
    "categories": "/api/v1/categories",
    "search": "/api/v1/search?q=<query>",
    "status": "/api/v1/status",
    "reviews": "/api/v1/reviews",
    "map": "/api/v1/map",
    "analytics": "/api/v1/analytics",
    "contact": "/api/v1/contact/submit",
    "health": "/health"
  }
}
```

#### `GET /health`

Health check endpoint.

```bash
curl http://localhost:7860/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "4.3.7",
  "timestamp": "2026-06-12T15:30:00.000000",
  "businesses": 40
}
```

---

### Listings

The core endpoint for browsing and filtering businesses.

#### `GET /api/v1/listings`

List all businesses with optional filters.

**Query Parameters:**

| Parameter   | Type    | Default | Description |
|------------|---------|---------|-------------|
| `category`  | string  | —       | Filter by category slug (e.g. `healthcare`, `fashion`) |
| `featured`  | boolean | —       | Filter featured businesses only |
| `verified`  | boolean | —       | Filter verified businesses only |
| `search`    | string  | —       | Full-text search across name, tags, description |
| `page`      | integer | 1       | Page number |
| `per_page`  | integer | 6       | Items per page (max 50) |
| `sort_by`   | string  | —       | Sort field: `name`, `rating`, `reviewCount`, `addedDate` |
| `sort_order`| string  | `asc`   | Sort direction: `asc` or `desc` |

**Examples:**

```bash
# Get all listings (paginated)
curl http://localhost:7860/api/v1/listings

# Filter by category
curl http://localhost:7860/api/v1/listings?category=healthcare

# Featured businesses only
curl http://localhost:7860/api/v1/listings?featured=true

# Search for a business
curl http://localhost:7860/api/v1/listings?search=aman%20garments

# Sort by rating (highest first)
curl http://localhost:7860/api/v1/listings?sort_by=rating&sort_order=desc

# Paginated
curl http://localhost:7860/api/v1/listings?page=2&per_page=10
```

**Response:**
```json
{
  "data": [
    {
      "id": "aman-garments",
      "name": "Aman Garments",
      "category": "Fashion & Apparel",
      "categorySlug": "fashion",
      "featured": true,
      "verified": true,
      "status": "open",
      "rating": 4.0,
      "reviewCount": 1,
      "coordinates": { "lat": 26.9230278, "lng": 81.2609167 },
      "address": "Village & Post Rasauli, District Barabanki...",
      "phone": "+91 63068 84047",
      "whatsapp": "+91 63068 84047",
      "tags": ["clothing", "fashion", "apparel", "ethnic-wear"],
      "addedDate": "2026-02-25",
      "bloodDonor": "",
      "lgbtqFriendly": false,
      "womenOwned": false
    }
  ],
  "total": 40,
  "page": 1,
  "perPage": 6,
  "totalPages": 7
}
```

#### `GET /api/v1/listings/{business_id}`

Get full details for a single business.

```bash
curl http://localhost:7860/api/v1/listings/aman-garments
```

Returns the complete business object including hours, reviews, contact info, UPI details, social links, service links, and more.

#### `GET /api/v1/listings/{business_id}/related`

Get related businesses in the same category.

| Parameter | Type    | Default | Description |
|-----------|---------|---------|-------------|
| `limit`   | integer | 4       | Max related businesses (max 20) |

```bash
curl http://localhost:7860/api/v1/listings/aman-garments/related
```

#### `GET /api/v1/listings/{business_id}/reviews`

Get reviews for a specific business.

```bash
curl http://localhost:7860/api/v1/listings/aman-garments/reviews
```

#### `GET /api/v1/listings/{business_id}/status`

Get real-time open/closed status for a business.

```bash
curl http://localhost:7860/api/v1/listings/aman-garments/status
```

---

### Categories

#### `GET /api/v1/categories`

List all categories with business counts.

```bash
curl http://localhost:7860/api/v1/categories
```

**Response:**
```json
{
  "total": 12,
  "categories": [
    { "slug": "healthcare", "name": "Healthcare & Pharmacy", "count": 8 },
    { "slug": "fashion", "name": "Fashion & Apparel", "count": 5 }
  ]
}
```

#### `GET /api/v1/categories/{category_slug}`

Get all businesses in a category.

```bash
curl http://localhost:7860/api/v1/categories/healthcare
```

---

### Search

#### `GET /api/v1/search?q=<query>`

Full-text search with smart alias expansion.

**How Search Works:**

1. Your query is first checked against the **alias dictionary** (e.g. `csc` expands to `common service center`, `csc center`)
2. If an alias match is found, all related terms are searched
3. Results are scored by relevance:
   - Exact ID/name match: +40-50 points
   - Name contains query: +15 points
   - Tag match: +10 points
   - Category match: +6 points
   - Description/address match: +2-3 points
   - Featured/verified bonus: +1 point each
4. Results sorted by score descending, then name

**Examples:**

```bash
# Basic search
curl "http://localhost:7860/api/v1/search?q=clothing"

# Search with alias expansion (finds CSC centers)
curl "http://localhost:7860/api/v1/search?q=csc"

# Search for hospitals (also matches clinic, medical center, etc.)
curl "http://localhost:7860/api/v1/search?q=hospital"

# Paginated search
curl "http://localhost:7860/api/v1/search?q=garments&page=1&per_page=5"
```

**Response:**
```json
{
  "query": "csc",
  "expandedQuery": "common service center common service centre csc center raheem csc golden csc vineet csc",
  "matchedAlias": "csc",
  "results": [...],
  "total": 3,
  "page": 1,
  "perPage": 20
}
```

#### `GET /api/v1/search/aliases`

Get the complete alias dictionary (mapping shorthand → search terms).

```bash
curl http://localhost:7860/api/v1/search/aliases
```

---

### Business Status

#### `GET /api/v1/status`

Get real-time open/closed status for ALL businesses.

#### `GET /api/v1/status/open`

Get only currently open businesses.

**Status Calculation:**

The API calculates business status in real-time using Indian Standard Time (IST, UTC+5:30):
- Checks today's operating hours from the business's `hours` object
- `00:00–00:00` means closed for the day
- Returns custom messages: "Open • Closes in 2h", "Closed • Opens in 30 min"
- Shows countdown timer when remaining time ≤ 60 minutes

**Response:**
```json
{
  "businessId": "aman-garments",
  "businessName": "Aman Garments",
  "isOpen": true,
  "message": "Open • Closes at 11:00 PM",
  "cssClass": "status-open",
  "nextChange": "23:00",
  "minutesUntilClose": 120,
  "minutesUntilOpen": null,
  "showCountdown": false,
  "currentTime": "21:00",
  "todayHours": {
    "open": "08:00",
    "close": "23:00"
  }
}
```

---

### Reviews

#### `GET /api/v1/reviews`

List all reviews across all businesses (paginated).

#### `GET /api/v1/reviews/business/{business_id}`

Get all reviews for a specific business.

```bash
curl http://localhost:7860/api/v1/reviews/business/aman-garments
```

---

### Map & Geography

#### `GET /api/v1/map/bounds`

Get businesses within a geographic bounding box. Useful for map viewports.

| Parameter | Type   | Description |
|-----------|--------|-------------|
| `north`   | float  | North latitude bound |
| `south`   | float  | South latitude bound |
| `east`    | float  | East longitude bound |
| `west`    | float  | West longitude bound |

```bash
curl "http://localhost:7860/api/v1/map/bounds?north=26.95&south=26.88&east=81.30&west=81.15"
```

#### `GET /api/v1/map/nearby`

Get businesses near a point, sorted by distance.

| Parameter | Type    | Default | Description |
|-----------|---------|---------|-------------|
| `lat`     | float   | —       | Center latitude |
| `lng`     | float   | —       | Center longitude |
| `radius`  | float   | 5.0     | Search radius in kilometers |
| `limit`   | integer | 20      | Max results |

```bash
curl "http://localhost:7860/api/v1/map/nearby?lat=26.92&lng=81.26&radius=3"
```

Response includes `distance` (meters) and `distanceKm` for each business.

#### `GET /api/v1/map/center`

Get the default map center coordinates.

```bash
curl http://localhost:7860/api/v1/map/center
```

---

### Analytics

Track and retrieve business view statistics. Analytics are in-memory and reset on server restart.

#### `POST /api/v1/analytics/view/{business_id}`

Record a business view (called when a user views a business detail).

```bash
curl -X POST http://localhost:7860/api/v1/analytics/view/aman-garments
```

#### `GET /api/v1/analytics/view/{business_id}`

Get view count for a business.

#### `GET /api/v1/analytics/popular`

Get most viewed businesses.

| Parameter | Type    | Default | Description |
|-----------|---------|---------|-------------|
| `limit`   | integer | 10      | Number of results |

```bash
curl http://localhost:7860/api/v1/analytics/popular?limit=5
```

#### `GET /api/v1/analytics/stats`

Get overall analytics statistics.

```bash
curl http://localhost:7860/api/v1/analytics/stats
```

---

### Contact

#### `POST /api/v1/contact/submit`

Submit a contact form message. Rate limited to 5 requests per hour per IP.

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91 98765 43210",
  "businessId": "aman-garments",
  "message": "I would like to inquire about your services."
}
```

| Field        | Type   | Required | Description |
|-------------|--------|----------|-------------|
| `name`      | string | Yes      | 2–100 characters |
| `email`     | string | Yes      | Valid email |
| `phone`     | string | No       | Max 20 characters |
| `businessId`| string | No       | Reference to a business |
| `message`   | string | Yes      | 10–2000 characters |

```bash
curl -X POST http://localhost:7860/api/v1/contact/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","message":"I have a question"}'
```

#### `GET /api/v1/contact/submissions`

List recent contact submissions (admin use, last 50).

---

## Authentication

The API currently has **no authentication** — it is designed for open public access. For production use, consider adding:

- **API Key auth** via header (`X-API-Key`)
- **JWT-based auth** for review/contact endpoints
- **Rate limiting** per IP (already implemented)

---

## Pagination

All list endpoints support pagination with these parameters:

| Parameter  | Default | Description |
|-----------|---------|-------------|
| `page`    | 1       | Current page (1-indexed) |
| `per_page`| varies  | Items per page |

All paginated responses include:

```json
{
  "data": [...],
  "total": 40,
  "page": 1,
  "perPage": 6,
  "totalPages": 7
}
```

---

## Error Handling

All errors return a consistent JSON structure:

```json
{
  "error": "not_found",
  "message": "Business 'nonexistent' not found",
  "statusCode": 404
}
```

**Common HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| 200  | Success |
| 400  | Bad request (invalid parameters) |
| 404  | Resource not found |
| 429  | Rate limit exceeded |
| 500  | Internal server error |

---

## Rate Limiting

| Endpoint Group       | Limit                  | Window |
|---------------------|------------------------|--------|
| General API         | 100 requests           | 60 seconds |
| Contact submission  | 5 requests             | 1 hour |

When exceeded, the API returns HTTP 429:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Limit: 100 per 60s"
}
```

---

## Deployment

### HuggingFace Spaces (Recommended)

#### Option A: Docker Space

1. **Create a new Space** at https://huggingface.co/new-space
2. **Choose Docker** as the Space SDK
3. **Set the following Space secrets** (optional):
   - `PORT`: 7860
4. **Push the code** — HuggingFace will build from the Dockerfile automatically

The `Dockerfile` uses `python:3.11-slim` and exposes port 7860.

#### Option B: Python Space (Auto-Detect)

1. **Create a new Space** at https://huggingface.co/new-space
2. **Choose Python** as the Space SDK
3. HuggingFace will auto-detect the FastAPI app in `app.py` and serve it with uvicorn

**Important for HuggingFace:** The `app.py` at the root level is the entry point. It serves the FastAPI app on port 7860.

### Local Development

```bash
# Clone the repository
cd LocalFind-API

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### Docker

```bash
# Build the image
docker build -t localfind-api .

# Run the container
docker run -p 7860:7860 localfind-api
```

### Production Considerations

1. **Database**: Replace in-memory JSON with PostgreSQL/MongoDB
2. **Authentication**: Add API keys or JWT
3. **Caching**: Add Redis for status calculations and popular queries
4. **Monitoring**: Add structured logging and metrics
5. **CI/CD**: Set up GitHub Actions for automated deployment to HuggingFace
6. **HTTPS**: HuggingFace handles SSL automatically. For self-hosting, use a reverse proxy

---

## Data Model

### Business Object (Full)

```json
{
  "id": "aman-garments",
  "name": "Aman Garments",
  "category": "Fashion & Apparel",
  "categorySlug": "fashion",
  "featured": true,
  "verified": true,
  "status": "open",
  "rating": 4.0,
  "reviewCount": 1,

  "coordinates": { "lat": 26.923, "lng": 81.260 },

  "address": "Rasauli, Barabanki, Uttar Pradesh",
  "mapLink": "https://maps.app.goo.gl/...",

  "phone": "+91 63068 84047",
  "phoneName": "Aman Yadav",
  "phoneSecondary": "+91 63062 03254",
  "phoneSecondaryName": "Noman",
  "phoneThird": null,
  "phoneThirdName": null,
  "phoneFourth": null,
  "phoneFourthName": null,

  "email": "amanyadav92471@gmail.com",
  "website": "",

  "whatsapp": "+91 63068 84047",
  "whatsappName": "Aman Yadav",
  "whatsappSecondary": null,
  "whatsappSecondaryName": null,
  "whatsappThird": null,
  "whatsappThirdName": null,
  "whatsappFourth": null,
  "whatsappFourthName": null,

  "instagram": "https://www.instagram.com/aman_garments_rasauli",
  "youtube": "",
  "linkedin": "",
  "facebook": "",

  "hours": {
    "mon": { "open": "08:00", "close": "23:00" },
    "tue": { "open": "08:00", "close": "23:00" },
    "wed": { "open": "08:00", "close": "23:00" },
    "thu": { "open": "08:00", "close": "23:00" },
    "fri": { "open": "08:00", "close": "23:00" },
    "sat": { "open": "08:00", "close": "23:00" },
    "sun": { "open": "08:00", "close": "23:00" }
  },

  "description": "Aman Garments is your premier destination for fashionable clothing...",
  "tags": ["clothing", "fashion", "apparel", "ethnic-wear"],
  "addedDate": "2026-02-25",

  "upiId": "",
  "upiName": "",
  "upiIds": [],

  "bloodDonor": "",
  "onlineOrder": "",
  "zomato": "",
  "magicpin": "",
  "menu": "",
  "bookTable": "",
  "orderOnline": "",
  "bookMyShow": "",
  "districtIn": "",

  "lgbtqFriendly": false,
  "womenOwned": false,
  "disableAppointment": false,

  "locatedInMall": null,
  "tenants": [],

  "reviews": [
    {
      "id": "review-1",
      "author": "Admin",
      "role": "LocalFind Team",
      "rating": 4.0,
      "date": "2026-02-27",
      "text": "Excellent service...",
      "verified": true
    }
  ]
}
```

### Business Summary (List Response)

A lighter version returned by list endpoints:

```json
{
  "id": "aman-garments",
  "name": "Aman Garments",
  "category": "Fashion & Apparel",
  "categorySlug": "fashion",
  "featured": true,
  "verified": true,
  "status": "open",
  "rating": 4.0,
  "reviewCount": 1,
  "coordinates": { "lat": 26.923, "lng": 81.260 },
  "address": "Rasauli, Barabanki...",
  "phone": "+91 63068 84047",
  "whatsapp": "+91 63068 84047",
  "tags": ["clothing", "fashion"],
  "addedDate": "2026-02-25",
  "bloodDonor": "",
  "lgbtqFriendly": false,
  "womenOwned": false
}
```

---

## Architecture

```
./
├── app.py                    # FastAPI entry point (HuggingFace-compatible)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker build for HuggingFace Spaces
├── .env.example              # Environment variable template
├── README.md                 # This guide
│
├── src/                      # Application source code
│   ├── config.py             # Settings, aliases, constants
│   │
│   ├── data/
│   │   ├── listings.json     # 40 businesses extracted from frontend
│   │   └── loader.py         # In-memory data access layer
│   │
│   ├── models.py             # Pydantic models & data transformers
│   │
│   ├── services/             # Business logic layer
│   │   ├── business_service.py   # CRUD, filtering, sorting
│   │   ├── search_service.py     # Full-text search with aliases
│   │   ├── status_service.py     # Real-time open/closed
│   │   ├── geo_service.py        # Map bounds & nearby queries
│   │   └── analytics_service.py  # View tracking & popular
│   │
│   ├── routes/               # FastAPI route handlers
│   │   ├── listings.py       # /api/v1/listings/*
│   │   ├── categories.py     # /api/v1/categories/*
│   │   ├── search.py         # /api/v1/search/*
│   │   ├── status.py         # /api/v1/status/*
│   │   ├── reviews.py        # /api/v1/reviews/*
│   │   ├── map.py            # /api/v1/map/*
│   │   ├── analytics.py      # /api/v1/analytics/*
│   │   └── contact.py        # /api/v1/contact/*
│   │
│   ├── middleware/           # Middleware layer
│   │   ├── rate_limit.py     # Per-IP rate limiting
│   │   └── error_handler.py  # Global exception handlers
│   │
│   └── utils/                # Utility functions
│       ├── sanitize.py       # XSS prevention, URL validation
│       ├── time_utils.py     # IST time, status calculation
│       └── search_aliases.py # Query expansion logic
│
└── tests/                    # Test suite
    ├── test_listings.py
    ├── test_search.py
    └── test_status.py
```

### Data Flow

```
Client Request
  → FastAPI Router (routes/)
    → Service Layer (services/)
      → Data Access (data/loader.py)
        → JSON File (data/listings.json)
      ← Business Objects
    ← Processed Response
  ← JSON Response
```

### Key Design Decisions

- **In-memory data**: Loaded from JSON at startup — fast, zero-database setup
- **No framework dependencies**: Pure FastAPI + Pydantic
- **IST-based status**: Real-time open/closed using Indian Standard Time
- **Alias-powered search**: Maps shorthand (`csc`, `atm`, `hospital`) to full business terms
- **In-memory analytics**: View counters reset on restart — swap to Redis for persistence
- **Rate limiting**: Per-IP with stricter limits on contact form
- **HuggingFace-optimized**: Dockerfile + app.py entry point, port 7860

---

## Testing

### Run All Tests

```bash
cd LocalFind-API
python -m pytest tests/ -v
```

### Run Individual Test Files

```bash
python tests/test_listings.py
python tests/test_search.py
python tests/test_status.py
```

### Test Coverage

- **Listings**: Loading, filtering, business detail, category counts
- **Search**: By name, category, tags, alias expansion, pagination, empty results
- **Status**: IST time, 12-hour conversion, time parsing, business open/closed, no-hours edge case

---

## FAQ

**Q: How do I update the business data?**
Edit `src/data/listings.json` and restart the server. The data is loaded fresh on each startup.

**Q: How do I add a new category?**
Businesses with a new `categorySlug` will automatically appear as a new category. No config changes needed.

**Q: Can I use this with React Native / Flutter?**
Yes! The API returns standard JSON — works with any HTTP client. See the [Search](#search) section for alias-powered queries that make search feel native.

**Q: How do I deploy to HuggingFace?**
Push the code to a HuggingFace Space. See the [HuggingFace Spaces (Recommended)](#huggingface-spaces-recommended) section.

**Q: How do I add authentication?**
The API is designed for open access. For production, add middleware for API key or JWT validation.

**Q: How is the business status calculated?**
Using Indian Standard Time (IST, UTC+5:30). The API checks the business's hours for today's day of the week and calculates if the current time falls within operating hours. Split shifts (e.g., 09:00–13:00, 16:00–20:00) are also supported.

---

## License

BSD 2-Clause License — see the [LICENSE](LICENSE) file for details.

Built with ❤️ by the LocalFind Team
