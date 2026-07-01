from sqlalchemy.orm import Session

from app.repositories.results import list_results


def get_results(db: Session, **filters) -> dict:
    return list_results(db, **filters)
