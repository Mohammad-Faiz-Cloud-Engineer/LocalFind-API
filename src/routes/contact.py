import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.utils.sanitize import sanitize_html

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["Contact"])

_contact_submissions: list[dict] = []


class ContactForm(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    phone: Optional[str] = Field(default=None, max_length=20)
    businessId: Optional[str] = Field(default=None, max_length=100)
    message: str = Field(..., min_length=10, max_length=2000)


@router.post("/submit")
async def submit_contact(form: ContactForm, request: Request):
    sanitized = {
        "name": sanitize_html(form.name),
        "email": sanitize_html(form.email),
        "phone": sanitize_html(form.phone) if form.phone else "",
        "businessId": sanitize_html(form.businessId) if form.businessId else None,
        "message": sanitize_html(form.message),
        "ip": request.client.host if request.client else None,
        "userAgent": request.headers.get("user-agent", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _contact_submissions.append(sanitized)
    if len(_contact_submissions) > 1000:
        _contact_submissions[:500] = []
    logger.info("Contact submission #%d received", len(_contact_submissions))
    return {
        "success": True,
        "message": "Thank you for your message. We will get back to you shortly.",
        "submissionId": len(_contact_submissions),
    }
