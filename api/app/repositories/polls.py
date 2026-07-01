from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_result import PollResult
from app.models.pollster import Pollster
from app.repositories.common import (
    count_from_select,
    paginate_query,
    poll_filter_conditions,
    public_poll_conditions,
)

POLL_PUBLIC_COLUMNS = (
    Poll.id.label("id"),
    Election.election_key.label("election_key"),
    Election.election_name.label("election_name"),
    Election.territory_code.label("territory_code"),
    Pollster.pollster_key.label("pollster_key"),
    Pollster.pollster_name.label("pollster_name"),
    Poll.media.label("media"),
    Poll.fieldwork_start.label("fieldwork_start"),
    Poll.fieldwork_end.label("fieldwork_end"),
    Poll.publication_date.label("publication_date"),
    Poll.sample_size.label("sample_size"),
    Poll.turnout.label("turnout"),
    Poll.lead.label("lead"),
    Poll.source_url.label("source_url"),
    Poll.source_title.label("source_title"),
    Poll.identity_status.label("identity_status"),
    Poll.first_seen_at.label("first_seen_at"),
    Poll.is_active.label("is_active"),
)


def _poll_base_query():
    return select(*POLL_PUBLIC_COLUMNS).join(Election, Election.id == Poll.election_id).join(
        Pollster, Pollster.id == Poll.pollster_id
    )


def list_polls(
    db: Session,
    *,
    election_key: str | None,
    territory_code: str | None,
    pollster_key: str | None,
    pollster: str | None,
    media: str | None,
    fieldwork_start_from: date | None,
    fieldwork_start_to: date | None,
    fieldwork_end_from: date | None,
    fieldwork_end_to: date | None,
    publication_date_from: date | None,
    publication_date_to: date | None,
    identity_status: str | None,
    include_manual_review: bool,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> dict:
    conditions = [
        *public_poll_conditions(
            include_manual_review=include_manual_review,
            include_inactive=include_inactive,
            identity_status=identity_status,
        ),
        *poll_filter_conditions(
            election_key=election_key,
            territory_code=territory_code,
            pollster_key=pollster_key,
            pollster=pollster,
            media=media,
            fieldwork_start_from=fieldwork_start_from,
            fieldwork_start_to=fieldwork_start_to,
            fieldwork_end_from=fieldwork_end_from,
            fieldwork_end_to=fieldwork_end_to,
            publication_date_from=publication_date_from,
            publication_date_to=publication_date_to,
        ),
    ]
    base_query = _poll_base_query().where(*conditions)
    query = base_query.order_by(
        Poll.fieldwork_end.desc().nulls_last(),
        Poll.publication_date.desc().nulls_last(),
        Poll.id.desc(),
    )
    return paginate_query(db, query, count_from_select(base_query), limit=limit, offset=offset)


def get_poll_detail(
    db: Session,
    *,
    poll_id: int,
    include_manual_review: bool,
    include_inactive: bool,
) -> dict | None:
    conditions = [
        Poll.id == poll_id,
        *public_poll_conditions(include_manual_review=include_manual_review, include_inactive=include_inactive),
    ]
    row = db.execute(_poll_base_query().where(*conditions)).mappings().first()
    if row is None:
        return None

    results = (
        db.execute(
            select(
                PollResult.party_key,
                PollResult.party_raw,
                PollResult.vote_share,
                PollResult.seats_min,
                PollResult.seats_max,
            )
            .where(PollResult.poll_id == poll_id)
            .order_by(PollResult.party_key)
        )
        .mappings()
        .all()
    )
    detail = dict(row)
    detail["results"] = [dict(result) for result in results]
    return detail
