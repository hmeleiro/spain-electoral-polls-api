from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.poll import PollDetail, PollSummary
from app.services.polls import get_poll, get_polls

router = APIRouter(prefix="/api/v1/polls", tags=["polls"])


@router.get("", response_model=PaginatedResponse[PollSummary])
def list_polls(
    election_key: str | None = None,
    territory_code: str | None = None,
    pollster_key: str | None = None,
    pollster: str | None = None,
    media: str | None = None,
    fieldwork_start_from: date | None = None,
    fieldwork_start_to: date | None = None,
    fieldwork_end_from: date | None = None,
    fieldwork_end_to: date | None = None,
    publication_date_from: date | None = None,
    publication_date_to: date | None = None,
    identity_status: str | None = None,
    include_manual_review: bool = False,
    include_inactive: bool = False,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_polls(
        db,
        election_key=election_key,
        territory_code=territory_code,
        pollster_key=pollster_key,
        pollster=pollster,
        media=media,
        fieldwork_start_from=fieldwork_start_from,
        fieldwork_start_to=fieldwork_start_to,
        fieldwork_end_from=fieldwork_end_from,
        fieldwork_end_to=fieldwork_end_to,
        publication_date_from=publication_date_from,
        publication_date_to=publication_date_to,
        identity_status=identity_status,
        include_manual_review=include_manual_review,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )


@router.get("/{poll_id}", response_model=PollDetail)
def get_poll_detail(
    poll_id: int,
    include_manual_review: bool = False,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
) -> dict:
    poll = get_poll(
        db,
        poll_id=poll_id,
        include_manual_review=include_manual_review,
        include_inactive=include_inactive,
    )
    if poll is None:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll
