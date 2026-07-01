from sqlalchemy.orm import Session

from app.repositories.polls import get_poll_detail, list_polls


def get_polls(db: Session, **filters) -> dict:
    return list_polls(db, **filters)


def get_poll(db: Session, **filters) -> dict | None:
    return get_poll_detail(db, **filters)
