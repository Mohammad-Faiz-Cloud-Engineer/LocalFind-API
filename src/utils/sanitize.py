import re
from html import escape
from urllib.parse import urlparse

ALLOWED_PROTOCOLS = {"https", "http", "mailto", "tel", "whatsapp"}
SAFE_TAGS = {
    "b", "i", "u", "em", "strong", "a", "br", "p", "ul", "ol", "li",
    "code", "pre", "blockquote", "span", "div",
}
SAFE_ATTRS = {"href", "target", "rel", "class", "style"}


def sanitize_html(value: str | None) -> str:
    if value is None:
        return ""
    return escape(str(value), quote=True)


def validate_and_sanitize_url(url: str | None) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme.lower() not in ALLOWED_PROTOCOLS:
            return ""
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)
        if parsed.netloc:
            return url
    except Exception:
        pass
    return ""


def linkify_text(text: str) -> str:
    if not text:
        return ""
    url_pattern = re.compile(r"(https?://[^\s]+)")
    return url_pattern.sub(r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', escape(text))


PHONE_PATTERN = re.compile(r"^[\d\s+\-()]+$")


def is_valid_phone(phone: str | None) -> bool:
    if not phone:
        return False
    return bool(PHONE_PATTERN.match(phone.strip()))


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(email: str | None) -> bool:
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))
