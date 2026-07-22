from decimal import Decimal

from pydantic import BaseModel, Field

class CategoryBudgetOut(BaseModel):
    category_id: int
    name: str
    budget: Decimal
    spent: Decimal
    remaining: Decimal
    pct: int
    status: str
    exhaust_day: int | None = None


class BudgetOverviewOut(BaseModel):
    period: str
    total_budget: Decimal | None
    total_budget_explicit: bool
    total_spent: Decimal
    total_remaining: Decimal | None
    safe_to_spend: Decimal | None
    days_left: int
    day_today: int
    days_in_month: int
    exhaust_day: int | None
    unbudgeted_spent: Decimal
    reserved_recurring: Decimal
    avg_daily_spend: Decimal | None
    projected_month_total: Decimal | None
    categories: list[CategoryBudgetOut]


class SafeToSpendOut(BaseModel):
    period: str
    total_budget: Decimal | None
    total_spent: Decimal
    safe_to_spend: Decimal | None
    days_left: int
    exhaust_day: int | None
    reserved_recurring: Decimal
    projected_month_total: Decimal | None


class AlertsOut(BaseModel):
    alerts: list[str]


class CycleOut(BaseModel):
    cycle_start_day: int  # 1 = mengikuti bulan kalender


class CycleSet(BaseModel):
    cycle_start_day: int = Field(ge=1, le=28)


class BudgetSet(BaseModel):
    category_id: int | None = None  # None = budget total
    amount: Decimal | None  # None = hapus
    period: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")  # None = default berulang
