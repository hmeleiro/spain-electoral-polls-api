from datetime import date as Date
from decimal import Decimal
from typing import Literal

from pydantic import field_serializer

from app.schemas.common import DecimalJSONModel

DateField = Literal["auto", "fieldwork_end", "publication_date"]


class TimeseriesPoint(DecimalJSONModel):
    date: Date
    poll_id: int
    pollster_key: str
    pollster_name: str | None = None
    media: str | None = None
    sample_size: int | None = None
    party_key: str
    party_raw: str | None = None
    party_name: str | None = None
    short_name: str | None = None
    color_hex: str | None = None
    display_order: int | None = None
    vote_share: Decimal | None = None

    @field_serializer("vote_share")
    def serialize_vote_share(self, value: Decimal | None) -> float | None:
        return self._decimal_to_float(value)
