from datetime import date
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.pollster import Pollster

QueryValues = str | list[str] | None


def query_values(value: QueryValues) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = [value]
    else:
        values = value
    return [item for item in values if item]


def equals_any(column, value: QueryValues):
    values = query_values(value)
    if not values:
        return None
    if len(values) == 1:
        return column == values[0]
    return column.in_(values)


def lower_equals_any(column, value: QueryValues):
    values = [item.lower() for item in query_values(value)]
    if not values:
        return None
    lowered_column = func.lower(column)
    if len(values) == 1:
        return lowered_column == values[0]
    return lowered_column.in_(values)


def ilike_any(column, value: QueryValues):
    values = query_values(value)
    if not values:
        return None
    clauses = [column.ilike(f"%{item}%") for item in values]
    if len(clauses) == 1:
        return clauses[0]
    return or_(*clauses)


def pollster_matches_any(key_column, name_column, value: QueryValues):
    values = [item.lower() for item in query_values(value)]
    if not values:
        return None
    key_column = func.lower(key_column)
    name_column = func.lower(name_column)
    if len(values) == 1:
        return or_(key_column == values[0], name_column == values[0])
    return or_(key_column.in_(values), name_column.in_(values))


def public_poll_conditions(
    *,
    include_manual_review: bool = False,
    include_inactive: bool = False,
    identity_status: str | None = None,
) -> list[Any]:
    conditions: list[Any] = []
    if not include_inactive:
        conditions.append(Poll.is_active.is_(True))
    if identity_status:
        conditions.append(Poll.identity_status == identity_status)
    elif not include_manual_review:
        conditions.append(Poll.identity_status != "manual_review")
    return conditions


def poll_filter_conditions(
    *,
    election_key: QueryValues = None,
    territory_code: str | None = None,
    pollster_key: QueryValues = None,
    pollster: QueryValues = None,
    media: QueryValues = None,
    fieldwork_start_from: date | None = None,
    fieldwork_start_to: date | None = None,
    fieldwork_end_from: date | None = None,
    fieldwork_end_to: date | None = None,
    publication_date_from: date | None = None,
    publication_date_to: date | None = None,
) -> list[Any]:
    conditions: list[Any] = []
    condition = equals_any(Election.election_key, election_key)
    if condition is not None:
        conditions.append(condition)
    if territory_code:
        conditions.append(Election.territory_code == territory_code)
    condition = lower_equals_any(Pollster.pollster_key, pollster_key)
    if condition is not None:
        conditions.append(condition)
    condition = pollster_matches_any(Pollster.pollster_key, Pollster.pollster_name, pollster)
    if condition is not None:
        conditions.append(condition)
    condition = ilike_any(Poll.media, media)
    if condition is not None:
        conditions.append(condition)
    if fieldwork_start_from:
        conditions.append(Poll.fieldwork_start >= fieldwork_start_from)
    if fieldwork_start_to:
        conditions.append(Poll.fieldwork_start <= fieldwork_start_to)
    if fieldwork_end_from:
        conditions.append(Poll.fieldwork_end >= fieldwork_end_from)
    if fieldwork_end_to:
        conditions.append(Poll.fieldwork_end <= fieldwork_end_to)
    if publication_date_from:
        conditions.append(Poll.publication_date >= publication_date_from)
    if publication_date_to:
        conditions.append(Poll.publication_date <= publication_date_to)
    return conditions


def paginate_query(db: Session, query: Select, count_query: Select, *, limit: int, offset: int) -> dict[str, Any]:
    total = db.scalar(count_query) or 0
    rows = db.execute(query.limit(limit).offset(offset)).mappings().all()
    return {"items": [dict(row) for row in rows], "limit": limit, "offset": offset, "total": total}


def count_from_select(query: Select) -> Select:
    return select(func.count()).select_from(query.order_by(None).subquery())
