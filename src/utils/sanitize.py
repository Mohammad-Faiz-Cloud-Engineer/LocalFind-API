from html import escape


def sanitize_html(value: str | None) -> str:
    if value is None:
        return ""
    return escape(str(value), quote=True)
