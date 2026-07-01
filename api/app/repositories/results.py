from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_result import PollResult
from app.models.pollster import Pollster
from app.repositories.common import count_from_select, paginate_query, poll_filter_conditions, public_poll_conditions


def list_results(
    db: Session,
    *,
    election_key: str | None,
    territory_code: str | None,
    pollster_key: str | None,
    pollster: str | None,
    media: str | None,
    party_key: str | None,
    party: str | None,
    fieldwork_end_from: date | None,
    fieldwork_end_to: date | None,
    publication_date_from: date | None,
    publication_date_to: date | None,
    include_manual_review: bool,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> dict:
    party_filter = party_key or party
    conditions = [
        *public_poll_conditions(include_manual_review=include_manual_review, include_inactive=include_inactive),
        *poll_filter_conditions(
            election_key=election_key,
            territory_code=territory_code,
            pollster_key=pollster_key,
            pollster=pollster,
            media=media,
            fieldwork_end_from=fieldwork_end_from,
            fieldwork_end_to=fieldwork_end_to,
            publication_date_from=publication_date_from,
            publication_date_to=publication_date_to,
        ),
    ]
    if party_filter:
        conditions.append(func.lower(PollResult.party_key) == party_filter.lower())

    date_expr = func.coalesce(Poll.fieldwork_end, Poll.publication_date).label("date")
    base_query = (
        select(
            PollResult.poll_id.label("poll_id"),
            date_expr,
            Election.election_key.label("election_key"),
            Pollster.pollster_key.label("pollster_key"),
            Pollster.pollster_name.label("pollster_name"),
            Poll.media.label("media"),
            Poll.fieldwork_end.label("fieldwork_end"),
            Poll.publication_date.label("publication_date"),
            Poll.sample_size.label("sample_size"),
            PollResult.party_key.label("party_key"),
            PollResult.party_raw.label("party_raw"),
            PollResult.vote_share.label("vote_share"),
            PollResult.seats_min.label("seats_min"),
            PollResult.seats_max.label("seats_max"),
        )
        .join(Poll, Poll.id == PollResult.poll_id)
        .join(Election, Election.id == Poll.election_id)
        .join(Pollster, Pollster.id == Poll.pollster_id)
        .where(*conditions)
    )
    query = base_query.order_by(
        Poll.fieldwork_end.desc().nulls_last(),
        Poll.publication_date.desc().nulls_last(),
        PollResult.party_key,
    )
    return paginate_query(db, query, count_from_select(base_query), limit=limit, offset=offset)
