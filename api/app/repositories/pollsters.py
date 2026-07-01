from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.pollster import Pollster
from app.repositories.common import count_from_select, paginate_query


def list_pollsters(
    db: Session,
    *,
    election_key: str | None,
    territory_code: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> dict:
    join_conditions = [Poll.pollster_id == Pollster.id]
    where_conditions = []
    if active_only:
        join_conditions.extend([Poll.is_active.is_(True), Poll.identity_status != "manual_review"])

    query = (
        select(
            Pollster.id,
            Pollster.pollster_key,
            Pollster.pollster_name,
            func.count(Poll.id).label("poll_count"),
        )
        .join(Poll, and_(*join_conditions))
        .join(Election, Election.id == Poll.election_id)
    )
    if election_key:
        where_conditions.append(Election.election_key == election_key)
    if territory_code:
        where_conditions.append(Election.territory_code == territory_code)

    base_query = (
        query.where(*where_conditions)
        .group_by(Pollster.id, Pollster.pollster_key, Pollster.pollster_name)
        .order_by(Pollster.pollster_name)
    )
    return paginate_query(db, base_query, count_from_select(base_query), limit=limit, offset=offset)
