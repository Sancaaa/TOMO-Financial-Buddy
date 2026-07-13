from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), index=True)
    icon: Mapped[str | None] = mapped_column(String(40), nullable=True)
    type: Mapped[str] = mapped_column(String(10), default="expense")  # expense | income
    # monthly_budget: default budget berulang; override per-periode ada di modul budget (Fase 5)
    monthly_budget: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    # rollover: sisa budget bulan lalu (jika positif) ditambahkan ke bulan ini
    budget_rollover: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
