from sqlalchemy.orm import Session

from app.repositories.timeseries import list_timeseries


def get_timeseries(db: Session, **filters) -> dict:
    return list_timeseries(db, **filters)
