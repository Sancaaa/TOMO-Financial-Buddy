"""Isi data awal: admin pertama + kategori/akun default per-user.

`seed()` idempotent — hanya membuat admin jika tabel users kosong.
`seed_user_defaults()` dipakai ulang saat admin membuat user baru (lihat api/admin.py).
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
    """Buat admin pertama + defaultnya bila DB benar-benar kosong."""
    if db.scalar(select(func.count()).select_from(User)):
        return  # sudah ada user — jangan seed ulang
    admin = User(
        username=settings.initial_username,
        password_hash=hash_password(settings.initial_password),
        is_admin=True,  # user pertama = admin (bisa kelola user lain)
        telegram_chat_id=settings.telegram_chat_id,
        settings={},
    )
    db.add(admin)
    db.flush()  # butuh admin.id untuk kategori/akun default
    seed_user_defaults(db, admin.id)
    db.commit()


def seed_user_defaults(db: Session, user_id: int) -> None:
    """Kategori default + akun 'Cash' untuk satu user (dipanggil saat user dibuat)."""
    for name, ctype, icon in DEFAULT_CATEGORIES:
        db.add(Category(user_id=user_id, name=name, type=ctype, icon=icon))
    db.add(Account(user_id=user_id, name="Cash", type="cash"))
