from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.admin_manual_review import (
    ReviewActionPayload,
    ReviewActionResponse,
    ReviewDetail,
    ReviewQueueItem,
    ReviewStatus,
)
from app.schemas.common import PaginatedResponse
from app.services.admin_manual_review import (
    get_manual_review_poll,
    get_manual_review_queue,
    record_manual_review_action,
)

router = APIRouter(prefix="/api/v1/admin/manual-review", tags=["admin"])


@router.get("", response_model=PaginatedResponse[ReviewQueueItem])
def list_manual_review(
    election_key: str | None = None,
    page_key: str | None = None,
    review_status: ReviewStatus | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_manual_review_queue(
        db,
        election_key=election_key,
        page_key=page_key,
        review_status=review_status,
        limit=limit,
        offset=offset,
    )


@router.get("/{poll_id}", response_model=ReviewDetail)
def get_manual_review_detail(poll_id: int, db: Session = Depends(get_db)) -> dict:
    poll = get_manual_review_poll(db, poll_id=poll_id)
    if poll is None:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll


@router.post("/{poll_id}/actions", response_model=ReviewActionResponse)
def create_manual_review_action(
    poll_id: int,
    payload: ReviewActionPayload,
    db: Session = Depends(get_db),
) -> dict:
    action = record_manual_review_action(db, poll_id=poll_id, payload=payload)
    if action is None:
        raise HTTPException(status_code=404, detail="Poll not found")
    return action
