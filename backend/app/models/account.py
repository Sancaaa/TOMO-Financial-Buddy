from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    type: Mapped[str] = mapped_column(String(20), default="cash")  # cash | bank | ewallet
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
