import httpx
import pytest
from sqlalchemy import text


@pytest.fixture
async def client(fastapi_app):
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
def manual_poll_id(test_engine) -> int:
    with test_engine.begin() as conn:
        return conn.execute(text("select id from polls where poll_key_strict = 'poll_manual'")).scalar_one()


@pytest.mark.anyio
async def test_manual_review_queue_returns_paginated_items(client):
    response = await client.get("/api/v1/admin/manual-review", params={"limit": 2, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "limit", "offset", "total"}
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["total"] == 3
    assert len(body["items"]) == 2

    item = body["items"][0]
    assert "poll_id" in item
    assert item["review_status"] == "pending"
    assert isinstance(item["anomalies"], list)
    assert isinstance(item["anomalies"][0], dict)


@pytest.mark.anyio
async def test_manual_review_detail_returns_404_for_unknown_poll(client):
    response = await client.get("/api/v1/admin/manual-review/999999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_manual_review_detail_returns_match_candidates_as_json(client, manual_poll_id):
    response = await client.get(f"/api/v1/admin/manual-review/{manual_poll_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["match_candidates"], list)
    assert len(body["match_candidates"]) == 1

    candidate = body["match_candidates"][0]
    assert candidate["rank"] == 1
    assert candidate["confidence"] == 0.82
    assert candidate["pollster_name"] == "40dB"
    assert candidate["media"] == "El Pais"
    assert candidate["sample_size"] == 1200
    assert candidate["reasons"] == ["same_election", "same_pollster", "same_media", "similar_vote_results"]
    assert isinstance(candidate["results"], list)
    assert candidate["results"][0]["party_key"] == "psoe"
    assert candidate["results"][0]["vote_share"] == 31.2


@pytest.mark.anyio
async def test_manual_review_action_rejects_invalid_action(client, manual_poll_id):
    response = await client.post(
        f"/api/v1/admin/manual-review/{manual_poll_id}/actions",
        json={"action": "approve-ish", "reviewer": "admin@example.com"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("action", "expected_identity_status", "expected_is_active"),
    [
        ("approved_new_poll", "new_poll", True),
        ("approved_match", "probable_match", True),
        ("rejected", "manual_review", False),
        ("needs_fix", "manual_review", True),
        ("comment", "manual_review", True),
    ],
)
async def test_manual_review_valid_actions_are_recorded_transactionally(
    client,
    test_engine,
    manual_poll_id,
    action,
    expected_identity_status,
    expected_is_active,
):
    response = await client.post(
        f"/api/v1/admin/manual-review/{manual_poll_id}/actions",
        json={
            "action": action,
            "reviewer": "admin@example.com",
            "notes": "Checked against source.",
            "corrected_payload": {"source": "test"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["poll_id"] == manual_poll_id
    assert body["review_action_id"] > 0
    assert body["action"] == action

    with test_engine.begin() as conn:
        poll = (
            conn.execute(
                text("select identity_status, is_active from polls where id = :poll_id"),
                {"poll_id": manual_poll_id},
            )
            .mappings()
            .one()
        )
        review_action = (
            conn.execute(
                text(
                    """
                    select action, previous_identity_status, new_identity_status, reviewer, notes, corrected_payload
                    from poll_review_actions
                    where id = :review_action_id
                    """
                ),
                {"review_action_id": body["review_action_id"]},
            )
            .mappings()
            .one()
        )
        event_type = conn.execute(
            text(
                """
                select event_type
                from poll_identity_events
                where poll_id = :poll_id
                order by created_at desc, id desc
                limit 1
                """
            ),
            {"poll_id": manual_poll_id},
        ).scalar_one()

    assert poll["identity_status"] == expected_identity_status
    assert poll["is_active"] is expected_is_active
    assert review_action["action"] == action
    assert review_action["previous_identity_status"] == "manual_review"
    assert review_action["new_identity_status"] == expected_identity_status
    assert review_action["reviewer"] == "admin@example.com"
    assert review_action["notes"] == "Checked against source."
    assert review_action["corrected_payload"] == {"source": "test"}
    assert event_type == f"manual_review_{action}"
