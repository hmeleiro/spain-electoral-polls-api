from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_result import PollResult
from app.repositories.common import count_from_select, paginate_query


def list_parties(
    db: Session,
    *,
    election_key: str | None,
    territory_code: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> dict:
    conditions = []
    if active_only:
        conditions.extend([Poll.is_active.is_(True), Poll.identity_status != "manual_review"])
    if election_key:
        conditions.append(Election.election_key == election_key)
    if territory_code:
        conditions.append(Election.territory_code == territory_code)

    base_query = (
        select(
            PollResult.party_key,
            func.min(PollResult.party_raw).label("party_raw"),
            func.count(func.distinct(PollResult.poll_id)).label("poll_count"),
        )
        .join(Poll, Poll.id == PollResult.poll_id)
        .join(Election, Election.id == Poll.election_id)
        .where(*conditions)
        .group_by(PollResult.party_key)
        .order_by(PollResult.party_key)
    )
    return paginate_query(db, base_query, count_from_select(base_query), limit=limit, offset=offset)
