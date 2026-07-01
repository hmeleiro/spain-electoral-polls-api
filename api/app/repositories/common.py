from datetime import date
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.pollster import Pollster


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
    election_key: str | None = None,
    territory_code: str | None = None,
    pollster_key: str | None = None,
    pollster: str | None = None,
    media: str | None = None,
    fieldwork_start_from: date | None = None,
    fieldwork_start_to: date | None = None,
    fieldwork_end_from: date | None = None,
    fieldwork_end_to: date | None = None,
    publication_date_from: date | None = None,
    publication_date_to: date | None = None,
) -> list[Any]:
    conditions: list[Any] = []
    if election_key:
        conditions.append(Election.election_key == election_key)
    if territory_code:
        conditions.append(Election.territory_code == territory_code)
    if pollster_key:
        conditions.append(func.lower(Pollster.pollster_key) == pollster_key.lower())
    if pollster:
        normalized = pollster.lower()
        conditions.append(
            or_(
                func.lower(Pollster.pollster_key) == normalized,
                func.lower(Pollster.pollster_name) == normalized,
            )
        )
    if media:
        conditions.append(Poll.media.ilike(f"%{media}%"))
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
