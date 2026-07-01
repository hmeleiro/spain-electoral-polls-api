from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_result import PollResult
from app.models.pollster import Pollster
from app.repositories.common import count_from_select, paginate_query, poll_filter_conditions, public_poll_conditions


def _date_expression(date_field: str):
    if date_field == "fieldwork_end":
        return Poll.fieldwork_end
    if date_field == "publication_date":
        return Poll.publication_date
    return func.coalesce(Poll.fieldwork_end, Poll.publication_date)


def list_timeseries(
    db: Session,
    *,
    election_key: str | None,
    territory_code: str | None,
    pollster_key: str | None,
    pollster: str | None,
    media: str | None,
    party_key: str | None,
    party: str | None,
    date_from: date | None,
    date_to: date | None,
    date_field: str,
    include_manual_review: bool,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> dict:
    party_filter = party_key or party
    selected_date = _date_expression(date_field).label("date")
    conditions = [
        *public_poll_conditions(include_manual_review=include_manual_review, include_inactive=include_inactive),
        *poll_filter_conditions(
            election_key=election_key,
            territory_code=territory_code,
            pollster_key=pollster_key,
            pollster=pollster,
            media=media,
        ),
        selected_date.is_not(None),
    ]
    if party_filter:
        conditions.append(func.lower(PollResult.party_key) == party_filter.lower())
    if date_from:
        conditions.append(selected_date >= date_from)
    if date_to:
        conditions.append(selected_date <= date_to)

    base_query = (
        select(
            selected_date,
            Poll.id.label("poll_id"),
            Pollster.pollster_key.label("pollster_key"),
            Pollster.pollster_name.label("pollster_name"),
            Poll.media.label("media"),
            Poll.sample_size.label("sample_size"),
            PollResult.party_key.label("party_key"),
            PollResult.party_raw.label("party_raw"),
            PollResult.vote_share.label("vote_share"),
        )
        .join(Poll, Poll.id == PollResult.poll_id)
        .join(Election, Election.id == Poll.election_id)
        .join(Pollster, Pollster.id == Poll.pollster_id)
        .where(*conditions)
    )
    query = base_query.order_by(selected_date.desc(), Poll.id.desc(), PollResult.party_key)
    return paginate_query(db, query, count_from_select(base_query), limit=limit, offset=offset)
