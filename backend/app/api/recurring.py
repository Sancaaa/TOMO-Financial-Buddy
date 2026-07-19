from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.clock import now_local
from app.core.database import get_db
from app.models import Account, Category, RecurringTx, User
from app.schemas.recurring import RecurringCreate, RecurringOut, RecurringUpdate
from app.services.recurring import first_run, next_month_dom

router = APIRouter(
    prefix="/recurring", tags=["recurring"], dependencies=[Depends(get_current_user)]
)


def _assert_owned(db: Session, model, obj_id: int | None, user_id: int, label: str) -> None:
    if obj_id is None:
        return
    obj = db.get(model, obj_id)
    if obj is None or obj.user_id != user_id:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{label} tidak ditemukan")


@router.get("", response_model=list[RecurringOut])
def list_recurring(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[RecurringTx]:
    return list(
        db.scalars(
            select(RecurringTx)
            .where(RecurringTx.user_id == user.id)
            .order_by(RecurringTx.day_of_month)
        ).all()
    )


@router.post("", response_model=RecurringOut, status_code=status.HTTP_201_CREATED)
def create_recurring(
    payload: RecurringCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecurringTx:
    data = payload.model_dump()
    _assert_owned(db, Account, data.get("account_id"), user.id, "Akun")
    _assert_owned(db, Category, data.get("category_id"), user.id, "Kategori")
    r = RecurringTx(
        user_id=user.id,
        **data,
        next_run=first_run(payload.day_of_month, now_local().date()),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/{rid}", response_model=RecurringOut)
def update_recurring(
    rid: int,
    payload: RecurringUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecurringTx:
    r = db.get(RecurringTx, rid)
    if r is None or r.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recurring tidak ditemukan")
    data = payload.model_dump(exclude_unset=True)
    _assert_owned(db, Account, data.get("account_id"), user.id, "Akun")
    _assert_owned(db, Category, data.get("category_id"), user.id, "Kategori")
    for field, value in data.items():
        setattr(r, field, value)
    if "day_of_month" in data and r.last_run is not None:
        r.next_run = next_month_dom(r.last_run, r.day_of_month)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring(
    rid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    r = db.get(RecurringTx, rid)
    if r is None or r.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recurring tidak ditemukan")
    db.delete(r)
    db.commit()
