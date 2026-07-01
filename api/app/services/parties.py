from sqlalchemy.orm import Session

from app.repositories.parties import list_parties


def get_parties(db: Session, **filters) -> dict:
    return list_parties(db, **filters)
