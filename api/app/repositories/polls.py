from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.election import Election
from app.models.party import Party
from app.models.poll import Poll
from app.models.poll_result import PollResult
from app.models.pollster import Pollster
from app.models.public_views import ApiPollPublic
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

POLL_VIEW_COLUMNS = (
    ApiPollPublic.poll_id.label("id"),
    ApiPollPublic.election_key.label("election_key"),
    ApiPollPublic.election_name.label("election_name"),
    ApiPollPublic.territory_code.label("territory_code"),
    ApiPollPublic.pollster_key.label("pollster_key"),
    ApiPollPublic.pollster_name.label("pollster_name"),
    ApiPollPublic.media.label("media"),
    ApiPollPublic.fieldwork_start.label("fieldwork_start"),
    ApiPollPublic.fieldwork_end.label("fieldwork_end"),
    ApiPollPublic.publication_date.label("publication_date"),
    ApiPollPublic.sample_size.label("sample_size"),
    ApiPollPublic.turnout.label("turnout"),
    ApiPollPublic.lead.label("lead"),
    ApiPollPublic.source_url.label("source_url"),
    ApiPollPublic.source_title.label("source_title"),
    ApiPollPublic.identity_status.label("identity_status"),
    ApiPollPublic.first_seen_at.label("first_seen_at"),
    ApiPollPublic.is_active.label("is_active"),
)


def _poll_base_query():
    return select(*POLL_PUBLIC_COLUMNS).join(Election, Election.id == Poll.election_id).join(
        Pollster, Pollster.id == Poll.pollster_id
    )


def _use_public_poll_view(*, include_manual_review: bool, include_inactive: bool, identity_status: str | None) -> bool:
    return not include_manual_review and not include_inactive and identity_status != "manual_review"


def _poll_view_conditions(
    *,
    election_key: QueryValues,
    territory_code: str | None,
    pollster_key: QueryValues,
    pollster: QueryValues,
    media: QueryValues,
    fieldwork_start_from: date | None,
    fieldwork_start_to: date | None,
    fieldwork_end_from: date | None,
    fieldwork_end_to: date | None,
    publication_date_from: date | None,
    publication_date_to: date | None,
    identity_status: str | None,
) -> list:
    conditions = []
    condition = equals_any(ApiPollPublic.election_key, election_key)
    if condition is not None:
        conditions.append(condition)
    if territory_code:
        conditions.append(ApiPollPublic.territory_code == territory_code)
    condition = lower_equals_any(ApiPollPublic.pollster_key, pollster_key)
    if condition is not None:
        conditions.append(condition)
    condition = pollster_matches_any(ApiPollPublic.pollster_key, ApiPollPublic.pollster_name, pollster)
    if condition is not None:
        conditions.append(condition)
    condition = ilike_any(ApiPollPublic.media, media)
    if condition is not None:
        conditions.append(condition)
    if fieldwork_start_from:
        conditions.append(ApiPollPublic.fieldwork_start >= fieldwork_start_from)
    if fieldwork_start_to:
        conditions.append(ApiPollPublic.fieldwork_start <= fieldwork_start_to)
    if fieldwork_end_from:
        conditions.append(ApiPollPublic.fieldwork_end >= fieldwork_end_from)
    if fieldwork_end_to:
        conditions.append(ApiPollPublic.fieldwork_end <= fieldwork_end_to)
    if publication_date_from:
        conditions.append(ApiPollPublic.publication_date >= publication_date_from)
    if publication_date_to:
        conditions.append(ApiPollPublic.publication_date <= publication_date_to)
    if identity_status:
        conditions.append(ApiPollPublic.identity_status == identity_status)
    return conditions


def list_polls(
    db: Session,
    *,
    election_key: QueryValues,
    territory_code: str | None,
    pollster_key: QueryValues,
    pollster: QueryValues,
    media: QueryValues,
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
    if _use_public_poll_view(
        include_manual_review=include_manual_review,
        include_inactive=include_inactive,
        identity_status=identity_status,
    ):
        conditions = _poll_view_conditions(
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
            identity_status=identity_status,
        )
        base_query = select(*POLL_VIEW_COLUMNS).where(*conditions)
        query = base_query.order_by(
            ApiPollPublic.fieldwork_end.desc().nulls_last(),
            ApiPollPublic.publication_date.desc().nulls_last(),
            ApiPollPublic.poll_id.desc(),
        )
        return paginate_query(db, query, count_from_select(base_query), limit=limit, offset=offset)

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
                func.coalesce(Party.party_name, PollResult.party_raw).label("party_name"),
                func.coalesce(Party.short_name, PollResult.party_raw).label("short_name"),
                Party.color_hex.label("color_hex"),
                Party.display_order.label("display_order"),
                PollResult.vote_share,
                PollResult.seats_min,
                PollResult.seats_max,
            )
            .outerjoin(Party, Party.party_key == PollResult.party_key)
            .where(PollResult.poll_id == poll_id)
            .order_by(Party.display_order.asc().nulls_last(), PollResult.party_key)
        )
        .mappings()
        .all()
    )
    detail = dict(row)
    detail["results"] = [dict(result) for result in results]
    return detail
