from sqlalchemy.orm import Session

from app.repositories.admin_manual_review import (
    create_manual_review_action,
    get_manual_review_detail,
    list_manual_review_queue,
)
from app.schemas.admin_manual_review import ReviewActionPayload


def get_manual_review_queue(db: Session, **filters) -> dict:
    return list_manual_review_queue(db, **filters)


def get_manual_review_poll(db: Session, *, poll_id: int) -> dict | None:
    return get_manual_review_detail(db, poll_id=poll_id)


def record_manual_review_action(
    db: Session,
    *,
    poll_id: int,
    payload: ReviewActionPayload,
) -> dict | None:
    return create_manual_review_action(db, poll_id=poll_id, payload=payload)
