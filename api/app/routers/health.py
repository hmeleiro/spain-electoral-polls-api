from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    database_status = "ok"
    try:
        db.execute(text("select 1"))
    except Exception:
        database_status = "unavailable"
    return HealthResponse(status="ok", service="spain-electoral-polls-api", database=database_status)
