# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Error handler robustness** — Added a general `HTTPException` handler with path-aware error messages for 404 and 405 status codes. Added safe `isinstance` check for non-string `exc.detail`. Retained integer 404/405 handlers required by Starlette's Router for unmatched routes. Extracted shared `_error_json()` helper for consistent response format. (`src/middleware/error_handler.py`)
- **`__import__('datetime')` hack** — Replaced inline `__import__` call in the `/health` endpoint with a proper top-level `from datetime import datetime, timezone` import. Health timestamp now uses timezone-aware UTC. (`app.py`)
- **Rate limiter memory leak** — `_rate_limit_store` was an unbounded `defaultdict(list)` that accumulated stale IPs forever. Added periodic cleanup every 5 minutes to purge expired entries. Rate limit constants now read from `Settings` and respect `RATE_LIMIT_REQUESTS`/`RATE_LIMIT_WINDOW` env vars. (`src/middleware/rate_limit.py`)
- **Settings class not env-driven** — `Settings` was a plain class with type annotations but no `@dataclass` decorator and never read environment variables. Converted to `@dataclass` with `field(default_factory=...)` for mutable defaults. Added `__post_init__` to read `APP_NAME`, `APP_VERSION`, `CORS_ORIGINS`, `CONTACT_PHONE`, `RATE_LIMIT_REQUESTS`, and `RATE_LIMIT_WINDOW` from environment. (`.env.example` is now functional.) (`src/config.py`)
- **O(n) `get_listing_by_id`** — Linear scan on every call across 8+ endpoints. Added a dict-based index (`_listings_index`) built at load time for O(1) lookups. (`src/data/loader.py`)
- **Duplicated search scoring logic** — The score/filter/mall-tenant/sort block was duplicated between `business_service.get_listings()` and `search_service.search_businesses()`. Extracted shared `score_and_rank_listings()` function in `search_service.py`, used by both callers. (`src/services/search_service.py`, `src/services/business_service.py`)

### Removed

- **Dead Pydantic models** — `ContactSubmission` and `ContactResponse` in `models.py` were defined but never imported or used anywhere. `contact.py` defines its own `ContactForm`. Removed dead models and unused `Field` import. (`src/models.py`)
- **Unauthenticated `GET /contact/submissions` endpoint** — Exposed submitted PII (name, email, phone, IP address, user-agent) with zero authentication. Removed to eliminate the PII leak vector. `POST /contact/submit` remains functional. (`src/routes/contact.py`, `README.md`)
- **Dead code cleanup** — Removed unused `normalize_text` import from `search_service.py` (only `matches_search_term` was used). Removed dead function `normalize_list()` from `text_normalizer.py` (never called). Removed dead functions `get_featured_listings()` and `get_verified_listings()` from `loader.py` (never imported). (`src/services/search_service.py`, `src/utils/text_normalizer.py`, `src/data/loader.py`)

### Changed

- **License metadata corrected** — README frontmatter `license: mit` changed to `license: bsd-2-clause` to match the actual LICENSE file (BSD 2-Clause). (`README.md`)

### Dependencies

- **Removed unused `pydantic-settings`** — Listed in `requirements.txt` but never imported anywhere in the codebase. Settings uses a custom `@dataclass` instead. (`requirements.txt`)
- **Docker base image upgraded** — `python:3.11-slim` → `python:3.13-slim` (latest stable Python release). (`Dockerfile`)
- **GitHub Actions updated to latest major versions** — `actions/checkout` v4→v6, `actions/configure-pages` v5→v6, `actions/upload-pages-artifact` v3→v5. `actions/deploy-pages` remains at v5 (already latest). (`.github/workflows/static.yml`, `.github/workflows/sync-huggingface.yml`)
