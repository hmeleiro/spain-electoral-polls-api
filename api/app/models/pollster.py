from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Pollster(Base):
    __tablename__ = "pollsters"

    id: Mapped[int] = mapped_column(primary_key=True)
    pollster_name: Mapped[str] = mapped_column(Text, nullable=False)
    pollster_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    polls = relationship("Poll", back_populates="pollster")
