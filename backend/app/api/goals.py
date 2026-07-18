from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.clock import now_local
from app.core.database import get_db
from app.models import Account, SavingGoal, Transaction
from app.schemas.goal import GoalContribute, GoalCreate, GoalOut, GoalUpdate
from app.services.ledger import apply_balance

router = APIRouter(
    prefix="/goals", tags=["goals"], dependencies=[Depends(get_current_user)]
)


def _to_out(g: SavingGoal) -> GoalOut:
    target = Decimal(g.target_amount)
    saved = Decimal(g.saved_amount)
    pct = int((saved / target * 100).to_integral_value()) if target > 0 else 0
    return GoalOut(
        id=g.id,
        name=g.name,
        target_amount=target,
        saved_amount=saved,
        target_date=g.target_date,
        account_id=g.account_id,
        pct=max(pct, 0),
        achieved=saved >= target,
    )


@router.get("", response_model=list[GoalOut])
def list_goals(db: Session = Depends(get_db)) -> list[GoalOut]:
    goals = db.scalars(select(SavingGoal).order_by(SavingGoal.created_at)).all()
    return [_to_out(g) for g in goals]


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)) -> GoalOut:
    g = SavingGoal(**payload.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return _to_out(g)


@router.patch("/{gid}", response_model=GoalOut)
def update_goal(gid: int, payload: GoalUpdate, db: Session = Depends(get_db)) -> GoalOut:
    g = db.get(SavingGoal, gid)
    if g is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(g, field, value)
    db.commit()
    db.refresh(g)
    return _to_out(g)


@router.post("/{gid}/contribute", response_model=GoalOut)
def contribute(gid: int, payload: GoalContribute, db: Session = Depends(get_db)) -> GoalOut:
    """Tambah/tarik tabungan.

    Bila akun sumber diberikan dan target punya akun tabungan, uang benar-benar
    dipindah (dicatat sebagai transfer sumber↔tabungan) sehingga saldo & riwayat
    ikut ter-update. Tanpa akun → sekadar menaikkan/menurunkan counter.
    """
    g = db.get(SavingGoal, gid)
    if g is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target tidak ditemukan")

    saved = Decimal(g.saved_amount)
    amount = payload.amount
    if amount < 0:  # tarik tak boleh melebihi yang sudah terkumpul
        amount = -min(-amount, saved)

    if amount != 0 and payload.from_account_id is not None:
        if g.account_id is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Target ini belum punya akun tabungan. Set dulu di 'Edit target'.",
            )
        if payload.from_account_id == g.account_id:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Akun sumber dan akun tabungan harus beda.",
            )
        for acc_id in (payload.from_account_id, g.account_id):
            if db.get(Account, acc_id) is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Akun tidak ditemukan")

        # positif: sumber → tabungan; negatif (tarik): tabungan → sumber
        src, dst = (
            (payload.from_account_id, g.account_id)
            if amount > 0
            else (g.account_id, payload.from_account_id)
        )
        tx = Transaction(
            amount=abs(amount),
            type="transfer",
            account_id=src,
            dest_account_id=dst,
            description=f"Nabung: {g.name}",
            occurred_at=now_local(),
            source="web",
        )
        db.add(tx)
        db.flush()
        apply_balance(db, tx, sign=1)

    g.saved_amount = saved + amount
    db.commit()
    db.refresh(g)
    return _to_out(g)


@router.delete("/{gid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(gid: int, db: Session = Depends(get_db)) -> None:
    g = db.get(SavingGoal, gid)
    if g is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target tidak ditemukan")
    db.delete(g)
    db.commit()
