import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.search_service import search_businesses


def test_search_by_name():
    result = search_businesses("aman garments")
    assert result["total"] > 0
    assert any("aman" in b["name"].lower() for b in result["results"])


def test_search_by_category():
    result = search_businesses("healthcare")
    assert result["total"] > 0


def test_search_by_tag():
    result = search_businesses("clothing")
    assert result["total"] > 0


def test_search_no_results():
    result = search_businesses("xyznonexistent")
    assert result["total"] == 0


def test_search_alias_expansion():
    result = search_businesses("csc")
    assert result["expandedQuery"] is not None or result["total"] > 0


def test_search_pagination():
    result = search_businesses("a", page=1, per_page=5)
    assert len(result["results"]) <= 5
    assert result["page"] == 1
    assert result["perPage"] == 5


def test_search_with_empty_query():
    result = search_businesses("a")
    assert "results" in result
    assert "total" in result


if __name__ == "__main__":
    test_search_by_name()
    test_search_by_category()
    test_search_by_tag()
    test_search_no_results()
    test_search_alias_expansion()
    test_search_pagination()
    test_search_with_empty_query()
    print("All search tests passed!")
