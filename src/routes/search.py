from typing import Optional

from fastapi import APIRouter, Query

from src.services.search_service import search_businesses, COMMAND_MAP, parse_special_command
from src.utils.search_aliases import get_all_aliases

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=1, description="Search query (supports /command syntax)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None, description="Filter by status: open or closed"),
    is_new: Optional[bool] = Query(None, description="Filter new businesses (added within 7 days)"),
    lgbtq_friendly: Optional[bool] = Query(None, description="Filter LGBTQ+ friendly"),
    women_owned: Optional[bool] = Query(None, description="Filter women-owned"),
):
    return search_businesses(
        query=q,
        page=page,
        per_page=per_page,
        status_filter=status,
        is_new=is_new,
        lgbtq_friendly=lgbtq_friendly,
        women_owned=women_owned,
    )


@router.get("/commands")
async def list_commands():
    return {
        "total": len(COMMAND_MAP),
        "commands": [
            {"command": f"/{k}", "label": v["label"], "property": v["field"]}
            for k, v in sorted(COMMAND_MAP.items())
        ],
    }


@router.get("/aliases")
async def list_aliases():
    return {
        "total": len(get_all_aliases()),
        "aliases": get_all_aliases(),
    }


@router.post("/parse")
async def parse_query(q: str = Query(..., description="Query to parse")):
    cmd = parse_special_command(q)
    return {
        "query": q,
        "isCommand": cmd is not None,
        "parsed": cmd,
    }
