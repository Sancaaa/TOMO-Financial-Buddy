"""Perhitungan budget: budget efektif, progress per kategori, safe-to-spend, proyeksi.

Sumber budget:
- default per-kategori  = `Category.monthly_budget`
- override per-periode  = tabel `budgets` (category_id, period='YYYY-MM')
- budget TOTAL          = tabel `budgets` (category_id NULL; period NULL default / 'YYYY-MM' override)
"""

from calendar import monthrange
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import LOCAL_TZ, now_local
from app.models import Budget, Category, Transaction


@dataclass
class CategoryBudget:
    category_id: int
    name: str
    budget: Decimal
    spent: Decimal
    remaining: Decimal
    pct: int
    status: str  # ok | warn | over


@dataclass
class BudgetOverview:
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
    categories: list[CategoryBudget] = field(default_factory=list)


def current_period() -> str:
    n = now_local()
    return f"{n.year:04d}-{n.month:02d}"


def _period_parts(period: str) -> tuple[int, int]:
    year, mon = (int(x) for x in period.split("-"))
    return year, mon


def _prev_period(period: str) -> str:
    year, mon = _period_parts(period)
    mon -= 1
    if mon == 0:
        mon = 12
        year -= 1
    return f"{year:04d}-{mon:02d}"


def _spent_by_category(db: Session, period: str, user_id: int) -> dict[int | None, Decimal]:
    start, end, _ = _bounds(period)
    rows = db.execute(
        select(Transaction.category_id, func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.occurred_at >= start,
            Transaction.occurred_at <= end,
        )
        .group_by(Transaction.category_id)
    ).all()
    return {cid: Decimal(total) for cid, total in rows}


def _bounds(period: str) -> tuple[datetime, datetime, int]:
    year, mon = _period_parts(period)
    last = monthrange(year, mon)[1]
    start = datetime(year, mon, 1, 0, 0, 0, tzinfo=LOCAL_TZ)
    end = datetime(year, mon, last, 23, 59, 59, 999999, tzinfo=LOCAL_TZ)
    return start, end, last


def _status(pct: int) -> str:
    if pct >= 100:
        return "over"
    if pct >= 70:
        return "warn"
    return "ok"


def effective_budget(
    db: Session,
    category_id: int | None,
    period: str,
    user_id: int,
    category: Category | None = None,
) -> Decimal | None:
    override = db.scalar(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.period == period,
        )
    )
    if override is not None:
        return override.amount
    if category_id is not None:
        cat = category or db.get(Category, category_id)
        return cat.monthly_budget if cat and cat.monthly_budget is not None else None
    # total: default berulang (period NULL)
    default = db.scalar(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id.is_(None),
            Budget.period.is_(None),
        )
    )
    return default.amount if default is not None else None


def overview(db: Session, user_id: int, period: str | None = None) -> BudgetOverview:
    period = period or current_period()
    start, end, days_in_month = _bounds(period)
    now = now_local()
    year, mon = _period_parts(period)
    is_current = now.year == year and now.month == mon
    day_today = now.day if is_current else days_in_month
    days_left = max(days_in_month - day_today + 1, 0) if is_current else 0

    spent_by_cat = _spent_by_category(db, period, user_id)
    all_spent = sum(spent_by_cat.values(), Decimal(0))

    prev_period = _prev_period(period)
    _prev_spent: dict[int | None, Decimal] | None = None

    categories: list[CategoryBudget] = []
    sum_cat_budget = Decimal(0)
    sum_budgeted_spent = Decimal(0)  # belanja di kategori yang punya budget saja
    expense_cats = db.scalars(
        select(Category).where(
            Category.user_id == user_id, Category.type == "expense"
        ).order_by(Category.name)
    ).all()
    for cat in expense_cats:
        budget = effective_budget(db, cat.id, period, user_id, cat)
        # rollover: tambahkan sisa positif budget bulan lalu
        if budget is not None and cat.budget_rollover:
            if _prev_spent is None:
                _prev_spent = _spent_by_category(db, prev_period, user_id)
            prev_budget = effective_budget(db, cat.id, prev_period, user_id, cat)
            if prev_budget:
                leftover = prev_budget - _prev_spent.get(cat.id, Decimal(0))
                if leftover > 0:
                    budget = budget + leftover
        spent = spent_by_cat.get(cat.id, Decimal(0))
        if budget is None and spent == 0:
            continue
        if budget:
            sum_cat_budget += budget
            sum_budgeted_spent += spent
        b = budget or Decimal(0)
        pct = int((spent / b * 100).to_integral_value()) if b > 0 else 0
        categories.append(
            CategoryBudget(
                category_id=cat.id,
                name=cat.name,
                budget=b,
                spent=spent,
                remaining=b - spent,
                pct=pct,
                status=_status(pct) if b > 0 else "ok",
            )
        )

    # Cakupan total_spent harus sama dengan total_budget agar sisa & safe-to-spend
    # koheren:
    #   - total eksplisit → payung untuk semua belanja → total_spent = all_spent
    #   - total diturunkan (jumlah budget kategori) → hanya belanja di kategori
    #     berbudget yang dihitung (belanja tak-berbudget tidak menggerus envelope)
    explicit_total = effective_budget(db, None, period, user_id)
    if explicit_total is not None:
        total_budget = explicit_total
        total_spent = all_spent
    elif sum_cat_budget > 0:
        total_budget = sum_cat_budget
        total_spent = sum_budgeted_spent
    else:
        total_budget = None
        total_spent = all_spent

    total_remaining = (total_budget - total_spent) if total_budget is not None else None
    safe_to_spend = None
    if total_budget is not None and days_left > 0:
        safe_to_spend = (total_budget - total_spent) / days_left

    exhaust_day = None
    if total_budget is not None and is_current and day_today > 0 and total_spent > 0:
        avg = total_spent / day_today
        if avg > 0:
            days_to_go = (total_budget - total_spent) / avg
            proj = day_today + int(days_to_go.to_integral_value())
            exhaust_day = min(max(proj, day_today), days_in_month)

    return BudgetOverview(
        period=period,
        total_budget=total_budget,
        total_budget_explicit=explicit_total is not None,
        total_spent=total_spent,
        total_remaining=total_remaining,
        safe_to_spend=safe_to_spend,
        days_left=days_left,
        day_today=day_today,
        days_in_month=days_in_month,
        exhaust_day=exhaust_day,
        categories=categories,
    )


def set_budget(
    db: Session,
    category_id: int | None,
    amount: Decimal | None,
    user_id: int,
    period: str | None = None,
) -> None:
    """Set/hapus budget (dibatasi ke `user_id`).

    category_id None + period None  → budget TOTAL default (tabel budgets).
    category_id set  + period None  → set Category.monthly_budget (default per-kategori).
    period 'YYYY-MM'                → override (tabel budgets).
    amount None → hapus override / kosongkan default.
    """
    if category_id is not None and period is None:
        cat = db.get(Category, category_id)
        if cat is not None and cat.user_id == user_id:
            cat.monthly_budget = amount
        db.commit()
        return

    existing = db.scalar(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.period == period,
        )
    )
    if amount is None:
        if existing is not None:
            db.delete(existing)
    elif existing is not None:
        existing.amount = amount
    else:
        db.add(Budget(user_id=user_id, category_id=category_id, period=period, amount=amount))
    db.commit()
