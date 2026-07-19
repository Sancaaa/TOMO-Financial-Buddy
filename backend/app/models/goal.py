from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SavingGoal(Base):
    """Target nabung: target + terkumpul + tenggat opsional.

    Bila `account_id` di-set (akun tabungan), setiap kontribusi mencatat transfer
    uang riil dari akun sumber ke akun tabungan ini. Bila None → sekadar counter.
    """

    __tablename__ = "saving_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(80))
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    saved_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
