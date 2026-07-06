import pytest

from app.core.cache import MISSING, TTLCache, clear_response_cache, make_cache_key
from app.services.elections import get_elections
from app.services.parties import get_parties
from app.services.results import get_results

pytestmark = pytest.mark.no_db


def test_ttl_cache_returns_hits_and_deep_copies():
    cache = TTLCache(ttl_seconds=300, max_entries=10)
    key = make_cache_key("namespace", {"party_key": ["psoe"]})
    value = {"items": [{"party_key": "psoe"}]}

    cache.set(key, value)
    first = cache.get(key)
    first["items"][0]["party_key"] = "changed"
    second = cache.get(key)

    assert second == value


def test_ttl_cache_expires_entries(monkeypatch):
    now = 100.0
    monkeypatch.setattr("app.core.cache.monotonic", lambda: now)
    cache = TTLCache(ttl_seconds=5, max_entries=10)
    key = make_cache_key("namespace", {"territory_code": "ES"})

    cache.set(key, {"items": []})
    assert cache.get(key) == {"items": []}

    now = 106.0
    assert cache.get(key) is MISSING


def test_ttl_cache_evicts_least_recently_used_entry():
    cache = TTLCache(ttl_seconds=300, max_entries=2)
    first_key = make_cache_key("namespace", {"offset": 0})
    second_key = make_cache_key("namespace", {"offset": 100})
    third_key = make_cache_key("namespace", {"offset": 200})

    cache.set(first_key, {"page": 1})
    cache.set(second_key, {"page": 2})
    assert cache.get(first_key) == {"page": 1}
    cache.set(third_key, {"page": 3})

    assert cache.get(second_key) is MISSING
    assert cache.get(first_key) == {"page": 1}
    assert cache.get(third_key) == {"page": 3}


def test_cache_key_normalizes_list_filters_as_ordered_sets():
    first = make_cache_key("results:list", {"party_key": ["psoe", "pp", "psoe"]})
    second = make_cache_key("results:list", {"party_key": ["pp", "psoe"]})

    assert first == second


def test_service_cache_reuses_identical_calls(monkeypatch):
    clear_response_cache()
    calls = []

    def list_elections(_db, **filters):
        calls.append(filters)
        return {"items": [{"call": len(calls)}], "limit": filters["limit"], "offset": filters["offset"], "total": 1}

    monkeypatch.setattr("app.services.elections.list_elections", list_elections)

    first = get_elections(object(), territory_code="ES", election_type=None, limit=100, offset=0)
    second = get_elections(object(), territory_code="ES", election_type=None, limit=100, offset=0)

    assert first == second
    assert len(calls) == 1


def test_service_cache_keeps_distinct_filters_separate(monkeypatch):
    clear_response_cache()
    calls = []

    def list_parties(_db, **filters):
        calls.append(filters)
        return {"items": [], "limit": filters["limit"], "offset": filters["offset"], "total": len(calls)}

    monkeypatch.setattr("app.services.parties.list_parties", list_parties)

    first = get_parties(object(), election_key=None, territory_code="ES", active_only=True, limit=100, offset=0)
    second = get_parties(object(), election_key=None, territory_code="ES", active_only=False, limit=100, offset=0)

    assert first["total"] == 1
    assert second["total"] == 2
    assert len(calls) == 2


def test_service_cache_normalizes_list_filter_order(monkeypatch):
    clear_response_cache()
    calls = []

    def list_results(_db, **filters):
        calls.append(filters)
        return {"items": [{"party_key": "psoe"}], "limit": filters["limit"], "offset": filters["offset"], "total": 1}

    monkeypatch.setattr("app.services.results.list_results", list_results)

    first = get_results(object(), party_key=["psoe", "pp"], limit=100, offset=0)
    second = get_results(object(), party_key=["pp", "psoe"], limit=100, offset=0)

    assert first == second
    assert len(calls) == 1
