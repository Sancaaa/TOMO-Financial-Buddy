"""Isi data awal sekali saat startup: user pertama, kategori default, akun cash.

Idempotent — hanya membuat data jika tabel terkait masih kosong.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import Account, Category, User

DEFAULT_CATEGORIES: list[tuple[str, str, str]] = [
    # (name, type, icon)
    ("Makan", "expense", "bowl"),
    ("Jajan", "expense", "coffee"),
    ("Transport", "expense", "car"),
    ("Kuota/Pulsa", "expense", "wifi"),
    ("Kos", "expense", "home"),
    ("Kuliah", "expense", "school"),
    ("Hiburan", "expense", "device-tv"),
    ("Kesehatan", "expense", "heartbeat"),
    ("Lainnya", "expense", "dots"),
    ("Kiriman", "income", "wallet"),
    ("Beasiswa", "income", "award"),
    ("Gaji/Freelance", "income", "briefcase"),
]


def seed(db: Session) -> None:
    _seed_user(db)
    _seed_categories(db)
    _seed_account(db)
    db.commit()


def _seed_user(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(User)):
        return
    db.add(
        User(
            username=settings.initial_username,
            password_hash=hash_password(settings.initial_password),
            telegram_chat_id=settings.telegram_chat_id,
            settings={},
        )
    )


def _seed_categories(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Category)):
        return
    for name, ctype, icon in DEFAULT_CATEGORIES:
        db.add(Category(name=name, type=ctype, icon=icon))


def _seed_account(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Account)):
        return
    db.add(Account(name="Cash", type="cash"))
