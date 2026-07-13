from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SavingGoal(Base):
    """Target nabung: target + terkumpul + tenggat opsional."""

    __tablename__ = "saving_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    saved_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
