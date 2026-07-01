from datetime import date, datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_serializer

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DecimalJSONModel(APIModel):
    @staticmethod
    def _decimal_to_float(value: Decimal | None) -> float | None:
        return None if value is None else float(value)


class PaginatedResponse(APIModel, Generic[T]):
    items: list[T]
    limit: int
    offset: int
    total: int


class HealthResponse(APIModel):
    status: str
    service: str
    database: str


class DateRange(APIModel):
    start: date | None = None
    end: date | None = None


class Timestamped(APIModel):
    first_seen_at: datetime | None = None

    @field_serializer("first_seen_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return None if value is None else value.isoformat()
