from sqlalchemy.orm import Session

from app.core.cache import cached_call
from app.repositories.parties import list_parties


def get_parties(db: Session, **filters) -> dict:
    return cached_call("parties:list", filters, lambda: list_parties(db, **filters))
