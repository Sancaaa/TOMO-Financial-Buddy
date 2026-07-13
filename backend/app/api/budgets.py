from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.budget import (
    BudgetOverviewOut,
    BudgetSet,
    CategoryBudgetOut,
    SafeToSpendOut,
)
from app.services.budget import overview, set_budget

router = APIRouter(
    prefix="/budgets", tags=["budgets"], dependencies=[Depends(get_current_user)]
)


def _to_overview_out(ov) -> BudgetOverviewOut:
    return BudgetOverviewOut(
        period=ov.period,
        total_budget=ov.total_budget,
        total_budget_explicit=ov.total_budget_explicit,
        total_spent=ov.total_spent,
        total_remaining=ov.total_remaining,
        safe_to_spend=ov.safe_to_spend,
        days_left=ov.days_left,
        day_today=ov.day_today,
        days_in_month=ov.days_in_month,
        exhaust_day=ov.exhaust_day,
        categories=[CategoryBudgetOut(**vars(c)) for c in ov.categories],
    )


@router.get("", response_model=BudgetOverviewOut)
def get_budgets(period: str | None = None, db: Session = Depends(get_db)) -> BudgetOverviewOut:
    return _to_overview_out(overview(db, period))


@router.get("/safe-to-spend", response_model=SafeToSpendOut)
def get_safe_to_spend(period: str | None = None, db: Session = Depends(get_db)) -> SafeToSpendOut:
    ov = overview(db, period)
    return SafeToSpendOut(
        period=ov.period,
        total_budget=ov.total_budget,
        total_spent=ov.total_spent,
        safe_to_spend=ov.safe_to_spend,
        days_left=ov.days_left,
        exhaust_day=ov.exhaust_day,
    )


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def put_budget(payload: BudgetSet, db: Session = Depends(get_db)) -> None:
    set_budget(db, payload.category_id, payload.amount, payload.period)
