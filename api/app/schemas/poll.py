from datetime import date, datetime
from decimal import Decimal

from pydantic import field_serializer

from app.schemas.common import DecimalJSONModel
from app.schemas.poll_result import PollResultRead


class PollSummary(DecimalJSONModel):
    id: int
    election_key: str
    election_name: str | None = None
    territory_code: str | None = None
    pollster_key: str
    pollster_name: str
    media: str | None = None
    fieldwork_start: date | None = None
    fieldwork_end: date | None = None
    publication_date: date | None = None
    sample_size: int | None = None
    turnout: Decimal | None = None
    lead: Decimal | None = None
    source_url: str | None = None
    source_title: str | None = None
    identity_status: str
    first_seen_at: datetime | None = None
    is_active: bool

    @field_serializer("turnout", "lead")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)

    @field_serializer("first_seen_at")
    def serialize_first_seen_at(self, value: datetime | None) -> str | None:
        return None if value is None else value.isoformat()


class PollDetail(PollSummary):
    results: list[PollResultRead]
