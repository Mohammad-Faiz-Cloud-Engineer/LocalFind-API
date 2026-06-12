from src.config import settings


def expand_search_query(query: str) -> tuple[str, str | None]:
    query_lower = query.strip().lower()
    if not query_lower:
        return query, None
    alias_to_terms = settings.alias_to_terms
    if query_lower in alias_to_terms:
        alias = alias_to_terms[query_lower]
        expanded_terms = settings.search_aliases.get(alias, [])
        expanded = " ".join(expanded_terms)
        return expanded, alias
    for alias, terms in settings.search_aliases.items():
        if query_lower in terms or query_lower == alias:
            expanded = " ".join(terms)
            return expanded, alias
    return query, None


def get_all_aliases() -> dict[str, list[str]]:
    return dict(settings.search_aliases)
