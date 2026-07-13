from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import SavingGoal
from app.schemas.goal import GoalContribute, GoalCreate, GoalOut, GoalUpdate

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
    g = db.get(SavingGoal, gid)
    if g is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target tidak ditemukan")
    g.saved_amount = max(Decimal(g.saved_amount) + payload.amount, Decimal(0))
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
