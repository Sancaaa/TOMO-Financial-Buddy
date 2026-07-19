from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Budget(Base):
    """Budget total atau override per-periode.

    - category_id NULL  = budget TOTAL keseluruhan.
    - period NULL       = default berulang; period 'YYYY-MM' = override bulan itu.
    Budget default per-kategori disimpan di `Category.monthly_budget`; tabel ini
    menampung budget total + override per-periode + flag rollover.
    """

    __tablename__ = "budgets"
    __table_args__ = (
        Index("ix_budget_scope", "category_id", "period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )
    period: Mapped[str | None] = mapped_column(String(7), nullable=True)  # 'YYYY-MM' atau NULL
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    rollover: Mapped[bool] = mapped_column(Boolean, default=False)


class BudgetAlert(Base):
    """Catatan alert budget terkirim, agar tidak dobel (sekali per ambang/periode)."""

    __tablename__ = "budget_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # NULL = total
    period: Mapped[str] = mapped_column(String(7))
    threshold: Mapped[int] = mapped_column(Integer)  # 80 | 100
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
