from sqlalchemy.orm import Session

from app.repositories.elections import list_elections


def get_elections(db: Session, **filters) -> dict:
    return list_elections(db, **filters)
