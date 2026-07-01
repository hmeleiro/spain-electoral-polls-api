from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.repositories.common import paginate_query


def list_elections(
    db: Session,
    *,
    territory_code: str | None,
    election_type: str | None,
    limit: int,
    offset: int,
) -> dict:
    conditions = []
    if territory_code:
        conditions.append(Election.territory_code == territory_code)
    if election_type:
        conditions.append(Election.election_type == election_type)

    query = (
        select(
            Election.id,
            Election.election_key,
            Election.election_type,
            Election.territory_code,
            Election.election_name,
            Election.election_date,
        )
        .where(*conditions)
        .order_by(Election.election_date.desc().nulls_last(), Election.election_key)
    )
    count_query = select(func.count()).select_from(Election).where(*conditions)
    return paginate_query(db, query, count_query, limit=limit, offset=offset)
