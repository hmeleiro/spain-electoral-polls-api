from sqlalchemy.orm import Session

from app.core.cache import cached_call
from app.repositories.elections import list_elections


def get_elections(db: Session, **filters) -> dict:
    return cached_call("elections:list", filters, lambda: list_elections(db, **filters))
