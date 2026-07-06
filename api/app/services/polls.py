from sqlalchemy.orm import Session

from app.core.cache import cached_call
from app.repositories.polls import get_poll_detail, list_polls


def get_polls(db: Session, **filters) -> dict:
    return cached_call("polls:list", filters, lambda: list_polls(db, **filters))


def get_poll(db: Session, **filters) -> dict | None:
    return cached_call("polls:detail", filters, lambda: get_poll_detail(db, **filters))
