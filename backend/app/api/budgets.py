from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.budget import (
    AlertsOut,
    BudgetOverviewOut,
    BudgetSet,
    CategoryBudgetOut,
    CycleOut,
    CycleSet,
    SafeToSpendOut,
)
from app.services.alerts import preview_budget_alerts
from app.services.budget import cycle_start_day, overview, set_budget

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
        unbudgeted_spent=ov.unbudgeted_spent,
        reserved_recurring=ov.reserved_recurring,
        avg_daily_spend=ov.avg_daily_spend,
        projected_month_total=ov.projected_month_total,
        categories=[CategoryBudgetOut(**vars(c)) for c in ov.categories],
    )


@router.get("", response_model=BudgetOverviewOut)
def get_budgets(
    period: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BudgetOverviewOut:
    return _to_overview_out(overview(db, user.id, period))


@router.get("/safe-to-spend", response_model=SafeToSpendOut)
def get_safe_to_spend(
    period: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SafeToSpendOut:
    ov = overview(db, user.id, period)
    return SafeToSpendOut(
        period=ov.period,
        total_budget=ov.total_budget,
        total_spent=ov.total_spent,
        safe_to_spend=ov.safe_to_spend,
        days_left=ov.days_left,
        exhaust_day=ov.exhaust_day,
        reserved_recurring=ov.reserved_recurring,
        projected_month_total=ov.projected_month_total,
    )


@router.get("/alerts", response_model=AlertsOut)
def get_alerts(
    period: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertsOut:
    """Status ambang budget saat ini untuk banner web (read-only, tanpa dedup)."""
    return AlertsOut(alerts=preview_budget_alerts(db, user.id, period))


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def put_budget(
    payload: BudgetSet,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    set_budget(db, payload.category_id, payload.amount, user.id, payload.period)


@router.get("/cycle", response_model=CycleOut)
def get_cycle(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CycleOut:
    return CycleOut(cycle_start_day=cycle_start_day(db, user.id))


@router.put("/cycle", status_code=status.HTTP_204_NO_CONTENT)
def put_cycle(
    payload: CycleSet,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    u = db.get(User, user.id)
    s = dict(u.settings or {})
    if payload.cycle_start_day <= 1:
        s.pop("cycle_start_day", None)  # 1 = default kalender → hapus setelan
    else:
        s["cycle_start_day"] = payload.cycle_start_day
    u.settings = s
    db.commit()
