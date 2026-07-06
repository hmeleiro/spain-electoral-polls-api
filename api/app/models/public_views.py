from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ApiPollPublic(Base):
    __tablename__ = "api_polls_public"

    poll_id: Mapped[int] = mapped_column(primary_key=True)
    election_key: Mapped[str | None] = mapped_column(Text)
    election_type: Mapped[str | None] = mapped_column(Text)
    territory_code: Mapped[str | None] = mapped_column(Text)
    election_name: Mapped[str | None] = mapped_column(Text)
    election_date: Mapped[date | None] = mapped_column(Date)
    pollster_key: Mapped[str | None] = mapped_column(Text)
    pollster_name: Mapped[str | None] = mapped_column(Text)
    media: Mapped[str | None] = mapped_column(Text)
    fieldwork_start: Mapped[date | None] = mapped_column(Date)
    fieldwork_end: Mapped[date | None] = mapped_column(Date)
    publication_date: Mapped[date | None] = mapped_column(Date)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    turnout: Mapped[Decimal | None] = mapped_column(Numeric)
    lead: Mapped[Decimal | None] = mapped_column(Numeric)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_title: Mapped[str | None] = mapped_column(Text)
    identity_status: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool | None] = mapped_column(Boolean)


class ApiPollResultPublic(Base):
    __tablename__ = "api_poll_results_public"

    poll_id: Mapped[int] = mapped_column(primary_key=True)
    party_key: Mapped[str] = mapped_column(Text, primary_key=True)
    election_key: Mapped[str | None] = mapped_column(Text)
    election_type: Mapped[str | None] = mapped_column(Text)
    territory_code: Mapped[str | None] = mapped_column(Text)
    pollster_key: Mapped[str | None] = mapped_column(Text)
    pollster_name: Mapped[str | None] = mapped_column(Text)
    media: Mapped[str | None] = mapped_column(Text)
    fieldwork_start: Mapped[date | None] = mapped_column(Date)
    fieldwork_end: Mapped[date | None] = mapped_column(Date)
    publication_date: Mapped[date | None] = mapped_column(Date)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    party_raw: Mapped[str | None] = mapped_column(Text)
    party_name: Mapped[str | None] = mapped_column(Text)
    short_name: Mapped[str | None] = mapped_column(Text)
    color_hex: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int | None] = mapped_column(Integer)
    vote_share: Mapped[Decimal | None] = mapped_column(Numeric)
    seats_min: Mapped[int | None] = mapped_column(Integer)
    seats_max: Mapped[int | None] = mapped_column(Integer)
