from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# JSONB di Postgres, JSON generik saat test dengan SQLite
_JSON = JSONB().with_variant(JSON(), "sqlite")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # unik saat tidak NULL (Postgres & SQLite memperlakukan NULL sebagai distinct),
    # jadi satu chat Telegram hanya bisa terikat ke satu user.
    telegram_chat_id: Mapped[str | None] = mapped_column(
        String(50), nullable=True, unique=True
    )
    settings: Mapped[dict] = mapped_column(_JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
