from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.schemas.admin_manual_review import ReviewActionPayload

ACTION_EFFECTS = {
    "approved_new_poll": ("new_poll", True),
    "approved_match": ("probable_match", True),
    "rejected": ("manual_review", False),
    "needs_fix": ("manual_review", None),
    "comment": (None, None),
}


def _queue_filter_sql(
    *,
    election_key: str | None,
    page_key: str | None,
    review_status: str | None,
) -> tuple[str, dict[str, Any]]:
    clauses = []
    params: dict[str, Any] = {}

    if election_key:
        clauses.append("election_key = :election_key")
        params["election_key"] = election_key
    if page_key:
        clauses.append("wiki_page = :page_key")
        params["page_key"] = page_key
    if review_status:
        clauses.append("review_status = :review_status")
        params["review_status"] = review_status

    if not clauses:
        return "", params
    return "where " + " and ".join(clauses), params


def _coerce_detail(row: dict[str, Any]) -> dict[str, Any]:
    results = row.get("results") or []
    row["results"] = [{**result, "poll_id": row["poll_id"]} for result in results]
    row["anomalies"] = row.get("anomalies") or []
    row["match_candidates"] = row.get("match_candidates") or []
    row["source_reference_ids"] = row.get("source_reference_ids") or []
    row["source_metadata"] = row.get("source_metadata") or {}
    row["review_priority"] = _review_priority(row)
    return row


def _review_priority(row: dict[str, Any]) -> int:
    review_status = row.get("review_status")
    if review_status in {"pending", "needs_fix"} and row.get("error_count", 0) > 0:
        return 100
    if review_status in {"pending", "needs_fix"} and row.get("identity_status") == "manual_review":
        return 80
    if review_status in {"pending", "needs_fix"} and row.get("warning_count", 0) > 0:
        return 60
    return 10


def list_manual_review_queue(
    db: Session,
    *,
    election_key: str | None,
    page_key: str | None,
    review_status: str | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    where_sql, params = _queue_filter_sql(
        election_key=election_key,
        page_key=page_key,
        review_status=review_status,
    )
    params.update({"limit": limit, "offset": offset})

    total = db.scalar(text(f"select count(*) from admin_poll_review_queue {where_sql}"), params) or 0
    rows = (
        db.execute(
            text(
                f"""
                select *
                from admin_poll_review_queue
                {where_sql}
                order by
                  review_priority desc,
                  coalesce(fieldwork_end, publication_date) desc nulls last,
                  poll_id desc
                limit :limit offset :offset
                """
            ),
            params,
        )
        .mappings()
        .all()
    )
    return {"items": [dict(row) for row in rows], "limit": limit, "offset": offset, "total": total}


def get_manual_review_detail(db: Session, *, poll_id: int) -> dict[str, Any] | None:
    row = (
        db.execute(
            text(
                """
                select *
                from admin_poll_review_detail
                where poll_id = :poll_id
                """
            ),
            {"poll_id": poll_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    return _coerce_detail(dict(row))


def create_manual_review_action(
    db: Session,
    *,
    poll_id: int,
    payload: ReviewActionPayload,
) -> dict[str, Any] | None:
    action = payload.action
    target_identity_status, target_is_active = ACTION_EFFECTS[action]

    try:
        poll = (
            db.execute(
                text(
                    """
                    select id, identity_status, identity_confidence, is_active, wiki_revision_id
                    from polls
                    where id = :poll_id
                    for update
                    """
                ),
                {"poll_id": poll_id},
            )
            .mappings()
            .first()
        )
        if poll is None:
            db.rollback()
            return None

        previous_identity_status = poll["identity_status"]
        previous_is_active = poll["is_active"]
        new_identity_status = target_identity_status or previous_identity_status
        new_is_active = target_is_active if target_is_active is not None else previous_is_active

        review_action_id = db.scalar(
            text(
                """
                insert into poll_review_actions (
                  poll_id,
                  action,
                  previous_identity_status,
                  new_identity_status,
                  reviewer,
                  notes,
                  corrected_payload
                )
                values (
                  :poll_id,
                  :action,
                  :previous_identity_status,
                  :new_identity_status,
                  :reviewer,
                  :notes,
                  :corrected_payload
                )
                returning id
                """
            ).bindparams(bindparam("corrected_payload", type_=JSONB)),
            {
                "poll_id": poll_id,
                "action": action,
                "previous_identity_status": previous_identity_status,
                "new_identity_status": new_identity_status,
                "reviewer": payload.reviewer,
                "notes": payload.notes,
                "corrected_payload": payload.corrected_payload,
            },
        )

        if target_identity_status is not None or target_is_active is not None:
            db.execute(
                text(
                    """
                    update polls
                    set
                      identity_status = :new_identity_status,
                      is_active = :new_is_active,
                      updated_at = now()
                    where id = :poll_id
                    """
                ),
                {
                    "poll_id": poll_id,
                    "new_identity_status": new_identity_status,
                    "new_is_active": new_is_active,
                },
            )

        db.execute(
            text(
                """
                insert into poll_identity_events (
                  poll_id,
                  wiki_revision_id,
                  event_type,
                  old_payload,
                  new_payload,
                  confidence,
                  reasons
                )
                values (
                  :poll_id,
                  :wiki_revision_id,
                  :event_type,
                  :old_payload,
                  :new_payload,
                  :identity_confidence,
                  :reasons
                )
                """
            ).bindparams(
                bindparam("old_payload", type_=JSONB),
                bindparam("new_payload", type_=JSONB),
                bindparam("reasons", type_=JSONB),
            ),
            {
                "poll_id": poll_id,
                "wiki_revision_id": poll["wiki_revision_id"],
                "event_type": f"manual_review_{action}",
                "old_payload": {
                    "identity_status": previous_identity_status,
                    "is_active": previous_is_active,
                },
                "new_payload": {
                    "identity_status": new_identity_status,
                    "is_active": new_is_active,
                    "review_action_id": review_action_id,
                },
                "identity_confidence": poll["identity_confidence"],
                "reasons": ["admin_review_decision", action],
            },
        )

        db.commit()
        return {"poll_id": poll_id, "review_action_id": review_action_id, "action": action}
    except Exception:
        db.rollback()
        raise
