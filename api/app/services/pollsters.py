from sqlalchemy.orm import Session

from app.core.cache import cached_call
from app.repositories.pollsters import list_pollsters


def get_pollsters(db: Session, **filters) -> dict:
    return cached_call("pollsters:list", filters, lambda: list_pollsters(db, **filters))
