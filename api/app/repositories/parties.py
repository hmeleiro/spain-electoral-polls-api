from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.party import Party
from app.models.public_views import ApiPollResultPublic
from app.repositories.common import QueryValues, count_from_select, equals_any, paginate_query


def list_parties(
    db: Session,
    *,
    election_key: QueryValues,
    territory_code: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> dict:
    party_conditions = []
    result_conditions = []
    if active_only:
        party_conditions.append(Party.is_active.is_(True))
    election_condition = equals_any(ApiPollResultPublic.election_key, election_key)
    if election_condition is not None:
        result_conditions.append(election_condition)
    if territory_code:
        party_conditions.append(Party.territory_code == territory_code)

    count_subquery = (
        select(
            ApiPollResultPublic.party_key.label("party_key"),
            func.count(func.distinct(ApiPollResultPublic.poll_id)).label("poll_count"),
        )
        .where(*result_conditions)
        .group_by(ApiPollResultPublic.party_key)
        .subquery()
    )

    base_query = (
        select(
            Party.party_key,
            Party.party_name,
            Party.short_name,
            Party.territory_code,
            Party.color_hex,
            Party.display_order,
            Party.is_active,
            func.coalesce(count_subquery.c.poll_count, 0).label("poll_count"),
        )
        .outerjoin(count_subquery, count_subquery.c.party_key == Party.party_key)
        .where(*party_conditions)
    )
    if election_condition is not None:
        base_query = base_query.where(count_subquery.c.poll_count.is_not(None))

    base_query = base_query.order_by(Party.display_order.asc().nulls_last(), Party.party_key)
    return paginate_query(db, base_query, count_from_select(base_query), limit=limit, offset=offset)
