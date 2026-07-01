from sqlalchemy.orm import Session

from app.repositories.pollsters import list_pollsters


def get_pollsters(db: Session, **filters) -> dict:
    return list_pollsters(db, **filters)
