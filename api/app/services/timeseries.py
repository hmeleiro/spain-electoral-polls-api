from sqlalchemy.orm import Session

from app.core.cache import cached_call
from app.repositories.timeseries import list_timeseries


def get_timeseries(db: Session, **filters) -> dict:
    return cached_call("timeseries:list", filters, lambda: list_timeseries(db, **filters))
