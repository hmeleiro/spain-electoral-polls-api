from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.election import ElectionRead
from app.services.elections import get_elections

router = APIRouter(prefix="/api/v1/elections", tags=["elections"])


@router.get("", response_model=PaginatedResponse[ElectionRead])
def list_elections(
    territory_code: str | None = None,
    election_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_elections(
        db,
        territory_code=territory_code,
        election_type=election_type,
        limit=limit,
        offset=offset,
    )
