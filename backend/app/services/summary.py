from calendar import monthrange
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import LOCAL_TZ
from app.models import Category, Transaction


@dataclass
class CategoryTotal:
    name: str
    total: Decimal


@dataclass
class PeriodSummary:
    total_expense: Decimal = Decimal(0)
    total_income: Decimal = Decimal(0)
    per_category: list[CategoryTotal] = field(default_factory=list)  # expense, desc
    count: int = 0


def period_summary(db: Session, start: datetime, end: datetime) -> PeriodSummary:
    window = (Transaction.occurred_at >= start, Transaction.occurred_at <= end)

    totals = db.execute(
        select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
        .where(*window)
        .group_by(Transaction.type)
    ).all()
    summary = PeriodSummary()
    for ttype, total in totals:
        if ttype == "income":
            summary.total_income = Decimal(total)
        elif ttype == "expense":
            summary.total_expense = Decimal(total)

    summary.count = db.scalar(
        select(func.count()).select_from(Transaction).where(*window)
    ) or 0

    rows = db.execute(
        select(Category.name, func.sum(Transaction.amount))
        .join(Category, Category.id == Transaction.category_id)
        .where(*window, Transaction.type == "expense")
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    summary.per_category = [CategoryTotal(name=n, total=Decimal(t)) for n, t in rows]
    return summary


@dataclass
class MonthPoint:
    month: str  # YYYY-MM
    expense: Decimal
    income: Decimal


def _month_bounds(year: int, mon: int) -> tuple[datetime, datetime]:
    start = datetime(year, mon, 1, 0, 0, 0, tzinfo=LOCAL_TZ)
    last = monthrange(year, mon)[1]
    end = datetime(year, mon, last, 23, 59, 59, 999999, tzinfo=LOCAL_TZ)
    return start, end


def monthly_trend(db: Session, months: int, ref: datetime) -> list[MonthPoint]:
    """Tren `months` bulan terakhir sampai bulan `ref` (kronologis menaik)."""
    year, mon = ref.year, ref.month
    seq: list[tuple[int, int]] = []
    for _ in range(months):
        seq.append((year, mon))
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
    seq.reverse()

    points: list[MonthPoint] = []
    for y, m in seq:
        start, end = _month_bounds(y, m)
        rows = db.execute(
            select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
            .where(Transaction.occurred_at >= start, Transaction.occurred_at <= end)
            .group_by(Transaction.type)
        ).all()
        totals = {t: Decimal(v) for t, v in rows}
        points.append(
            MonthPoint(
                month=f"{y:04d}-{m:02d}",
                expense=totals.get("expense", Decimal(0)),
                income=totals.get("income", Decimal(0)),
            )
        )
    return points
