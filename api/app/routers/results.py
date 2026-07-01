from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.poll_result import PollResultLongRead
from app.services.results import get_results

router = APIRouter(prefix="/api/v1/results", tags=["results"])


@router.get("", response_model=PaginatedResponse[PollResultLongRead])
def list_results(
    election_key: str | None = None,
    territory_code: str | None = None,
    pollster_key: str | None = None,
    pollster: str | None = None,
    media: str | None = None,
    party_key: str | None = None,
    party: str | None = None,
    fieldwork_end_from: date | None = None,
    fieldwork_end_to: date | None = None,
    publication_date_from: date | None = None,
    publication_date_to: date | None = None,
    include_manual_review: bool = False,
    include_inactive: bool = False,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_results(
        db,
        election_key=election_key,
        territory_code=territory_code,
        pollster_key=pollster_key,
        pollster=pollster,
        media=media,
        party_key=party_key,
        party=party,
        fieldwork_end_from=fieldwork_end_from,
        fieldwork_end_to=fieldwork_end_to,
        publication_date_from=publication_date_from,
        publication_date_to=publication_date_to,
        include_manual_review=include_manual_review,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
