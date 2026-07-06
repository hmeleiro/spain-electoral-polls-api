from datetime import date as Date
from decimal import Decimal

from pydantic import field_serializer

from app.schemas.common import DecimalJSONModel


class PollResultRead(DecimalJSONModel):
    party_key: str
    party_raw: str | None = None
    party_name: str | None = None
    short_name: str | None = None
    color_hex: str | None = None
    display_order: int | None = None
    vote_share: Decimal | None = None
    seats_min: int | None = None
    seats_max: int | None = None

    @field_serializer("vote_share")
    def serialize_vote_share(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)


class PollResultLongRead(PollResultRead):
    poll_id: int
    date: Date | None = None
    election_key: str
    pollster_key: str
    pollster_name: str
    media: str | None = None
    fieldwork_end: Date | None = None
    publication_date: Date | None = None
    sample_size: int | None = None
