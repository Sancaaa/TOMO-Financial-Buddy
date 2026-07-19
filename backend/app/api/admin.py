"""Dashboard admin: kelola user (khusus admin).

Buat/hapus user, reset password, jadikan/lepas admin, putus tautan Telegram.
User baru langsung diberi kategori & akun default (lihat seed.seed_user_defaults).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.database import get_db
from app.core.security import hash_password
from app.models import Transaction, User
from app.schemas.auth import AdminUserOut, AdminUserUpdate, UserCreate
from app.seed import seed_user_defaults

router = APIRouter(
    prefix="/admin/users", tags=["admin"], dependencies=[Depends(get_admin_user)]
)


def _to_out(db: Session, user: User) -> AdminUserOut:
    tx_count = db.scalar(
        select(func.count()).select_from(Transaction).where(Transaction.user_id == user.id)
    ) or 0
    return AdminUserOut(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        telegram_linked=user.telegram_chat_id is not None,
        telegram_chat_id=user.telegram_chat_id,
        tx_count=tx_count,
    )


@router.get("", response_model=list[AdminUserOut])
def list_users(db: Session = Depends(get_db)) -> list[AdminUserOut]:
    users = db.scalars(select(User).order_by(User.id)).all()
    return [_to_out(db, u) for u in users]


@router.post("", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> AdminUserOut:
    exists = db.scalar(select(User).where(User.username == payload.username))
    if exists is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username sudah dipakai")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_admin=payload.is_admin,
        settings={},
    )
    db.add(user)
    db.flush()  # butuh user.id untuk data default
    seed_user_defaults(db, user.id)
    db.commit()
    db.refresh(user)
    return _to_out(db, user)


@router.patch("/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> AdminUserOut:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User tidak ditemukan")

    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.telegram_chat_id is not None:
        user.telegram_chat_id = payload.telegram_chat_id
    elif payload.unlink_telegram:
        user.telegram_chat_id = None
    if payload.is_admin is not None:
        # jangan sampai admin terakhir kehilangan status admin
        if user.is_admin and not payload.is_admin and _admin_count(db) <= 1:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Harus ada minimal satu admin"
            )
        user.is_admin = payload.is_admin
    db.commit()
    db.refresh(user)
    return _to_out(db, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User tidak ditemukan")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Tak bisa menghapus diri sendiri")
    if user.is_admin and _admin_count(db) <= 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Harus ada minimal satu admin")
    # data user ikut terhapus lewat FK ON DELETE CASCADE
    db.delete(user)
    db.commit()


def _admin_count(db: Session) -> int:
    return db.scalar(
        select(func.count()).select_from(User).where(User.is_admin.is_(True))
    ) or 0
