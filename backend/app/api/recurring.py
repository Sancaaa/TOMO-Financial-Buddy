from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.clock import now_local
from app.core.database import get_db
from app.models import RecurringTx
from app.schemas.recurring import RecurringCreate, RecurringOut, RecurringUpdate
from app.services.recurring import first_run, next_month_dom

router = APIRouter(
    prefix="/recurring", tags=["recurring"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[RecurringOut])
def list_recurring(db: Session = Depends(get_db)) -> list[RecurringTx]:
    return list(db.scalars(select(RecurringTx).order_by(RecurringTx.day_of_month)).all())


@router.post("", response_model=RecurringOut, status_code=status.HTTP_201_CREATED)
def create_recurring(payload: RecurringCreate, db: Session = Depends(get_db)) -> RecurringTx:
    r = RecurringTx(
        **payload.model_dump(),
        next_run=first_run(payload.day_of_month, now_local().date()),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/{rid}", response_model=RecurringOut)
def update_recurring(
    rid: int, payload: RecurringUpdate, db: Session = Depends(get_db)
) -> RecurringTx:
    r = db.get(RecurringTx, rid)
    if r is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recurring tidak ditemukan")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(r, field, value)
    if "day_of_month" in data and r.last_run is not None:
        r.next_run = next_month_dom(r.last_run, r.day_of_month)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring(rid: int, db: Session = Depends(get_db)) -> None:
    r = db.get(RecurringTx, rid)
    if r is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recurring tidak ditemukan")
    db.delete(r)
    db.commit()
