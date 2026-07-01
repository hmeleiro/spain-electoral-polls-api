from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.party import PartyRead
from app.services.parties import get_parties

router = APIRouter(prefix="/api/v1/parties", tags=["parties"])


@router.get("", response_model=PaginatedResponse[PartyRead])
def list_parties(
    election_key: str | None = None,
    territory_code: str | None = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    return get_parties(
        db,
        election_key=election_key,
        territory_code=territory_code,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
