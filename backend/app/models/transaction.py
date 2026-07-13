from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    type: Mapped[str] = mapped_column(String(10), index=True)  # expense | income | transfer
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    dest_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    receipt_id: Mapped[int | None] = mapped_column(
        ForeignKey("receipts.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    # asal transaksi: web | telegram | ocr | recurring | import
    source: Mapped[str] = mapped_column(String(20), default="web")
    # input mentah (mis. "makan 15k") — disimpan agar bisa di-reparse jika parser membaik
    raw_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    category: Mapped["Category | None"] = relationship(lazy="joined")
    account: Mapped["Account | None"] = relationship(
        "Account", foreign_keys="Transaction.account_id", lazy="joined"
    )
    dest_account: Mapped["Account | None"] = relationship(
        "Account", foreign_keys="Transaction.dest_account_id", lazy="joined"
    )
