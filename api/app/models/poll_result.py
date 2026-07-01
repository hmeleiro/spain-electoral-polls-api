from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PollResult(Base):
    __tablename__ = "poll_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id", ondelete="CASCADE"), nullable=False)
    party_key: Mapped[str] = mapped_column(Text, nullable=False)
    party_raw: Mapped[str | None] = mapped_column(Text)
    vote_share: Mapped[Decimal | None] = mapped_column(Numeric)
    seats_min: Mapped[int | None] = mapped_column(Integer)
    seats_max: Mapped[int | None] = mapped_column(Integer)
    raw_value: Mapped[str | None] = mapped_column(Text)

    poll = relationship("Poll", back_populates="results")
