import time

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas.auth import PasswordChange, Token, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate-limit login sederhana (in-memory, per-proses): tahan brute force.
_LOGIN_MAX_FAILS = 5
_LOGIN_WINDOW_SECONDS = 300
_login_fails: dict[str, list[float]] = {}


def _recent_fails(username: str, now: float) -> list[float]:
    fails = [t for t in _login_fails.get(username, []) if now - t < _LOGIN_WINDOW_SECONDS]
    if fails:
        _login_fails[username] = fails
    else:
        _login_fails.pop(username, None)
    return fails


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    now = time.monotonic()
    if len(_recent_fails(form.username, now)) >= _LOGIN_MAX_FAILS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan gagal. Coba lagi beberapa menit.",
        )

    user = db.scalar(select(User).where(User.username == form.username))
    if user is None or not verify_password(form.password, user.password_hash):
        _login_fails.setdefault(form.username, []).append(now)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
        )

    _login_fails.pop(form.username, None)  # reset saat sukses
    return Token(access_token=create_access_token(user.id))


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password lama salah",
        )
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
