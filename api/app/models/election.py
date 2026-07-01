from datetime import date, datetime

from sqlalchemy import Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Election(Base):
    __tablename__ = "elections"

    id: Mapped[int] = mapped_column(primary_key=True)
    election_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    election_type: Mapped[str] = mapped_column(Text, nullable=False)
    territory_code: Mapped[str] = mapped_column(Text, nullable=False)
    election_name: Mapped[str] = mapped_column(Text, nullable=False)
    election_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    polls = relationship("Poll", back_populates="election")
