from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_key_strict: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    poll_signature: Mapped[str] = mapped_column(Text, nullable=False)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id"), nullable=False)
    pollster_id: Mapped[int] = mapped_column(ForeignKey("pollsters.id"), nullable=False)
    media: Mapped[str | None] = mapped_column(Text)
    fieldwork_start: Mapped[date | None] = mapped_column(Date)
    fieldwork_end: Mapped[date | None] = mapped_column(Date)
    publication_date: Mapped[date | None] = mapped_column(Date)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    turnout: Mapped[Decimal | None] = mapped_column(Numeric)
    lead: Mapped[Decimal | None] = mapped_column(Numeric)
    wiki_page: Mapped[str] = mapped_column(Text, nullable=False)
    wiki_revision_id: Mapped[int | None] = mapped_column(Integer)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_title: Mapped[str | None] = mapped_column(Text)
    source_reference_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    source_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
    row_hash: Mapped[str] = mapped_column(Text, nullable=False)
    identity_status: Mapped[str] = mapped_column(Text, nullable=False)
    identity_confidence: Mapped[Decimal | None] = mapped_column(Numeric)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    election = relationship("Election", back_populates="polls")
    pollster = relationship("Pollster", back_populates="polls")
    results = relationship("PollResult", back_populates="poll", cascade="all, delete-orphan")
