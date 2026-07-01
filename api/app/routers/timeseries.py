from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.timeseries import DateField, TimeseriesPoint
from app.services.timeseries import get_timeseries

router = APIRouter(prefix="/api/v1/timeseries", tags=["timeseries"])


@router.get("", response_model=PaginatedResponse[TimeseriesPoint])
def list_timeseries(
    election_key: str | None = None,
    territory_code: str | None = None,
    pollster_key: str | None = None,
    pollster: str | None = None,
    media: str | None = None,
    party_key: str | None = None,
    party: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    date_field: DateField = "auto",
    include_manual_review: bool = False,
    include_inactive: bool = False,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_timeseries(
        db,
        election_key=election_key,
        territory_code=territory_code,
        pollster_key=pollster_key,
        pollster=pollster,
        media=media,
        party_key=party_key,
        party=party,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        include_manual_review=include_manual_review,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
