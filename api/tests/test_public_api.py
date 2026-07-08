import httpx
import pytest


@pytest.fixture
async def client(fastapi_app):
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.mark.anyio
async def test_health_returns_ok(client):
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "spain-electoral-polls-api"
    assert body["database"] == "ok"


@pytest.mark.anyio
async def test_openapi_is_available(client):
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Spain Electoral Polls API"


@pytest.mark.anyio
async def test_polls_returns_paginated_structure(client):
    response = await client.get("/api/v1/polls")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "limit", "offset", "total"}
    assert body["limit"] == 100
    assert body["offset"] == 0
    assert body["total"] == 1
    assert "id" in body["items"][0]
    assert "poll_id" not in body["items"][0]
    assert body["items"][0]["pollster_name"] == "40dB"


@pytest.mark.anyio
async def test_parties_returns_canonical_catalog(client):
    response = await client.get("/api/v1/parties", params={"territory_code": "ES", "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 2
    first_keys = [item["party_key"] for item in body["items"][:2]]
    assert first_keys == ["psoe", "pp"]
    assert body["items"][0]["party_name"] == "Partido Socialista Obrero Espanol"
    assert body["items"][0]["short_name"] == "PSOE"
    assert body["items"][0]["color_hex"] == "#e30613"
    assert "party_raw" not in body["items"][0]


@pytest.mark.anyio
async def test_poll_detail_includes_results(client):
    poll_id = (await client.get("/api/v1/polls")).json()["items"][0]["id"]
    response = await client.get(f"/api/v1/polls/{poll_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == poll_id
    assert len(body["results"]) == 3
    assert {item["party_key"] for item in body["results"]} == {"new_party", "pp", "psoe"}
    psoe = next(item for item in body["results"] if item["party_key"] == "psoe")
    unknown = next(item for item in body["results"] if item["party_key"] == "new_party")
    assert psoe["party_name"] == "Partido Socialista Obrero Espanol"
    assert psoe["short_name"] == "PSOE"
    assert psoe["color_hex"] == "#e30613"
    assert unknown["party_name"] == "New Party"
    assert unknown["short_name"] == "New Party"
    assert unknown["color_hex"] is None


@pytest.mark.anyio
async def test_results_returns_long_format(client):
    response = await client.get("/api/v1/results", params={"party": "psoe"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["party_key"] == "psoe"
    assert item["party_name"] == "Partido Socialista Obrero Espanol"
    assert item["short_name"] == "PSOE"
    assert item["color_hex"] == "#e30613"
    assert item["vote_share"] == 31.2
    assert item["fieldwork_end"] == "2026-06-05"


@pytest.mark.anyio
async def test_results_accepts_multiple_party_keys(client):
    response = await client.get(
        "/api/v1/results",
        params=[("party_key", "psoe"), ("party_key", "pp")],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["party_key"] for item in body["items"]} == {"psoe", "pp"}


@pytest.mark.anyio
async def test_timeseries_auto_uses_fieldwork_end(client):
    response = await client.get("/api/v1/timeseries", params={"party": "psoe"})

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["date"] == "2026-06-05"
    assert item["party_name"] == "Partido Socialista Obrero Espanol"
    assert item["seats_min"] == 120
    assert item["seats_max"] == 125


@pytest.mark.anyio
async def test_timeseries_publication_date_mode(client):
    response = await client.get(
        "/api/v1/timeseries",
        params={"party": "psoe", "date_field": "publication_date"},
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["date"] == "2026-06-07"


@pytest.mark.anyio
async def test_timeseries_accepts_multiple_party_keys_with_manual_review(client):
    response = await client.get(
        "/api/v1/timeseries",
        params=[
            ("party_key", "psoe"),
            ("party_key", "pp"),
            ("include_manual_review", "true"),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 4
    assert {item["party_key"] for item in body["items"]} == {"psoe", "pp"}
    psoe = next(item for item in body["items"] if item["party_key"] == "psoe")
    assert psoe["seats_min"] == 120
    assert psoe["seats_max"] == 125


@pytest.mark.anyio
async def test_polls_accepts_multiple_media_values(client):
    response = await client.get(
        "/api/v1/polls",
        params=[
            ("media", "El Pais"),
            ("media", "La Sexta"),
            ("include_inactive", "true"),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["media"] for item in body["items"]} == {"El Pais", "La Sexta"}


@pytest.mark.anyio
async def test_defaults_exclude_manual_review_and_inactive(client):
    response = await client.get("/api/v1/polls")

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["identity_status"] != "manual_review"
    assert items[0]["is_active"] is True


@pytest.mark.anyio
async def test_include_manual_review_includes_manual_rows(client):
    response = await client.get("/api/v1/polls", params={"include_manual_review": "true"})

    assert response.status_code == 200
    statuses = {item["identity_status"] for item in response.json()["items"]}
    assert "manual_review" in statuses


@pytest.mark.anyio
async def test_include_inactive_includes_inactive_rows(client):
    response = await client.get("/api/v1/polls", params={"include_inactive": "true"})

    assert response.status_code == 200
    assert any(item["is_active"] is False for item in response.json()["items"])


@pytest.mark.anyio
async def test_limit_cannot_exceed_1000(client):
    response = await client.get("/api/v1/polls", params={"limit": 1001})

    assert response.status_code == 422


@pytest.mark.anyio
async def test_public_endpoints_do_not_expose_internal_fields(client):
    poll_id = (await client.get("/api/v1/polls")).json()["items"][0]["id"]
    responses = [
        await client.get("/api/v1/polls"),
        await client.get(f"/api/v1/polls/{poll_id}"),
        await client.get("/api/v1/results"),
        await client.get("/api/v1/timeseries"),
    ]
    forbidden = {
        "row_hash",
        "poll_signature",
        "poll_key_strict",
        "source_reference_ids",
        "source_metadata",
        "raw_value",
        "payload_json",
    }

    for response in responses:
        assert response.status_code == 200
        assert forbidden.isdisjoint(response.text)
