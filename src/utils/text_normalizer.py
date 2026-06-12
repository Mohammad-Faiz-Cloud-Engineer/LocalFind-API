import re


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    result = text.lower().strip()
    result = re.sub(r"[\s\-_.]+", "", result)
    result = re.sub(r"[^\w]", "", result)
    return result


def normalize_list(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


def matches_search_term(text: str | None, term: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    if term in text_lower:
        return True
    text_norm = normalize_text(text)
    term_norm = normalize_text(term)
    if term_norm and term_norm in text_norm:
        return True
    return False
