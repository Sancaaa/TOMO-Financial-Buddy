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


def period_summary(
    db: Session, start: datetime, end: datetime, user_id: int
) -> PeriodSummary:
    window = (
        Transaction.user_id == user_id,
        Transaction.occurred_at >= start,
        Transaction.occurred_at <= end,
    )

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
class SpendingComparison:
    month: str
    prev_month: str
    total_expense: Decimal
    prev_total_expense: Decimal
    pct: int | None  # None bila bulan lalu Rp0 (tak bisa dibandingkan)
    up: bool
    driver_category: str | None  # kategori pendorong perubahan
    driver_delta: Decimal | None  # selisih kategori itu (bertanda)


def _prev_ym(year: int, mon: int) -> tuple[int, int]:
    return (year, mon - 1) if mon > 1 else (year - 1, 12)


def spending_comparison(db: Session, year: int, mon: int, user_id: int) -> SpendingComparison:
    """Bandingkan pengeluaran bulan (year, mon) vs bulan sebelumnya, plus kategori
    pendorong perubahan (pergerakan terbesar searah dengan perubahan total)."""
    p_year, p_mon = _prev_ym(year, mon)
    cur = period_summary(db, *_month_bounds(year, mon), user_id)
    prev = period_summary(db, *_month_bounds(p_year, p_mon), user_id)

    cur_map = {c.name: c.total for c in cur.per_category}
    prev_map = {c.name: c.total for c in prev.per_category}
    up = cur.total_expense >= prev.total_expense
    deltas = {
        n: cur_map.get(n, Decimal(0)) - prev_map.get(n, Decimal(0))
        for n in set(cur_map) | set(prev_map)
    }
    candidates = [(n, d) for n, d in deltas.items() if (d > 0 if up else d < 0)]
    driver_category, driver_delta = (
        max(candidates, key=lambda kv: abs(kv[1])) if candidates else (None, None)
    )

    pct = None
    if prev.total_expense > 0:
        pct = int(
            ((cur.total_expense - prev.total_expense) / prev.total_expense * 100)
            .to_integral_value()
        )

    return SpendingComparison(
        month=f"{year:04d}-{mon:02d}",
        prev_month=f"{p_year:04d}-{p_mon:02d}",
        total_expense=cur.total_expense,
        prev_total_expense=prev.total_expense,
        pct=pct,
        up=up,
        driver_category=driver_category,
        driver_delta=driver_delta,
    )


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


def monthly_trend(db: Session, months: int, ref: datetime, user_id: int) -> list[MonthPoint]:
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
            .where(
                Transaction.user_id == user_id,
                Transaction.occurred_at >= start,
                Transaction.occurred_at <= end,
            )
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
