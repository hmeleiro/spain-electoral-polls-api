from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.pollster import PollsterRead
from app.services.pollsters import get_pollsters

router = APIRouter(prefix="/api/v1/pollsters", tags=["pollsters"])


@router.get("", response_model=PaginatedResponse[PollsterRead])
def list_pollsters(
    election_key: str | None = None,
    territory_code: str | None = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_pollsters(
        db,
        election_key=election_key,
        territory_code=territory_code,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
