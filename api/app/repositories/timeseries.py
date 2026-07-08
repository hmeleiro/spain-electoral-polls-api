from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.party import Party
from app.models.poll import Poll
from app.models.poll_result import PollResult
from app.models.pollster import Pollster
from app.models.public_views import ApiPollResultPublic
from app.repositories.common import (
    QueryValues,
    count_from_select,
    equals_any,
    ilike_any,
    lower_equals_any,
    paginate_query,
    poll_filter_conditions,
    pollster_matches_any,
    public_poll_conditions,
)


def _date_expression(date_field: str):
    if date_field == "fieldwork_end":
        return Poll.fieldwork_end
    if date_field == "publication_date":
        return Poll.publication_date
    return func.coalesce(Poll.fieldwork_end, Poll.publication_date)


def _view_date_expression(date_field: str):
    if date_field == "fieldwork_end":
        return ApiPollResultPublic.fieldwork_end
    if date_field == "publication_date":
        return ApiPollResultPublic.publication_date
    return func.coalesce(ApiPollResultPublic.fieldwork_end, ApiPollResultPublic.publication_date)


def list_timeseries(
    db: Session,
    *,
    election_key: QueryValues,
    territory_code: str | None,
    pollster_key: QueryValues,
    pollster: QueryValues,
    media: QueryValues,
    party_key: QueryValues,
    party: QueryValues,
    date_from: date | None,
    date_to: date | None,
    date_field: str,
    include_manual_review: bool,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> dict:
    if not include_manual_review and not include_inactive:
        party_filter = party_key or party
        selected_date = _view_date_expression(date_field).label("date")
        conditions = [selected_date.is_not(None)]
        condition = equals_any(ApiPollResultPublic.election_key, election_key)
        if condition is not None:
            conditions.append(condition)
        if territory_code:
            conditions.append(ApiPollResultPublic.territory_code == territory_code)
        condition = lower_equals_any(ApiPollResultPublic.pollster_key, pollster_key)
        if condition is not None:
            conditions.append(condition)
        condition = pollster_matches_any(
            ApiPollResultPublic.pollster_key,
            ApiPollResultPublic.pollster_name,
            pollster,
        )
        if condition is not None:
            conditions.append(condition)
        condition = ilike_any(ApiPollResultPublic.media, media)
        if condition is not None:
            conditions.append(condition)
        condition = lower_equals_any(ApiPollResultPublic.party_key, party_filter)
        if condition is not None:
            conditions.append(condition)
        if date_from:
            conditions.append(selected_date >= date_from)
        if date_to:
            conditions.append(selected_date <= date_to)

        base_query = (
            select(
                selected_date,
                ApiPollResultPublic.poll_id.label("poll_id"),
                ApiPollResultPublic.pollster_key.label("pollster_key"),
                ApiPollResultPublic.pollster_name.label("pollster_name"),
                ApiPollResultPublic.media.label("media"),
                ApiPollResultPublic.sample_size.label("sample_size"),
                ApiPollResultPublic.party_key.label("party_key"),
                ApiPollResultPublic.party_raw.label("party_raw"),
                ApiPollResultPublic.party_name.label("party_name"),
                ApiPollResultPublic.short_name.label("short_name"),
                ApiPollResultPublic.color_hex.label("color_hex"),
                ApiPollResultPublic.display_order.label("display_order"),
                ApiPollResultPublic.vote_share.label("vote_share"),
                ApiPollResultPublic.seats_min.label("seats_min"),
                ApiPollResultPublic.seats_max.label("seats_max"),
            )
            .where(*conditions)
        )
        query = base_query.order_by(
            selected_date.desc(),
            ApiPollResultPublic.poll_id.desc(),
            ApiPollResultPublic.display_order.asc().nulls_last(),
            ApiPollResultPublic.party_key,
        )
        return paginate_query(db, query, count_from_select(base_query), limit=limit, offset=offset)

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
    condition = lower_equals_any(PollResult.party_key, party_filter)
    if condition is not None:
        conditions.append(condition)
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
            func.coalesce(Party.party_name, PollResult.party_raw).label("party_name"),
            func.coalesce(Party.short_name, PollResult.party_raw).label("short_name"),
            Party.color_hex.label("color_hex"),
            Party.display_order.label("display_order"),
            PollResult.vote_share.label("vote_share"),
            PollResult.seats_min.label("seats_min"),
            PollResult.seats_max.label("seats_max"),
        )
        .join(Poll, Poll.id == PollResult.poll_id)
        .join(Election, Election.id == Poll.election_id)
        .join(Pollster, Pollster.id == Poll.pollster_id)
        .outerjoin(Party, Party.party_key == PollResult.party_key)
        .where(*conditions)
    )
    query = base_query.order_by(
        selected_date.desc(),
        Poll.id.desc(),
        Party.display_order.asc().nulls_last(),
        PollResult.party_key,
    )
    return paginate_query(db, query, count_from_select(base_query), limit=limit, offset=offset)
