from sqlalchemy.orm import Session

from app.core.cache import cached_call
from app.repositories.results import list_results


def get_results(db: Session, **filters) -> dict:
    return cached_call("results:list", filters, lambda: list_results(db, **filters))
