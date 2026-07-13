from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecurringTx(Base):
    """Transaksi berulang bulanan (kos, langganan) yang dibuat otomatis scheduler."""

    __tablename__ = "recurring_txs"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    type: Mapped[str] = mapped_column(String(10), default="expense")
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    day_of_month: Mapped[int] = mapped_column(Integer, default=1)  # 1..28
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    next_run: Mapped[date] = mapped_column(Date, index=True)
    last_run: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
