"""Perhitungan budget: budget efektif, progress per kategori, safe-to-spend, proyeksi.

Sumber budget:
- default per-kategori  = `Category.monthly_budget`
- override per-periode  = tabel `budgets` (category_id, period='YYYY-MM')
- budget TOTAL          = tabel `budgets` (category_id NULL; period NULL default / 'YYYY-MM' override)
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import LOCAL_TZ, now_local
from app.models import Budget, Category, RecurringTx, Transaction, User


@dataclass
class CategoryBudget:
    category_id: int
    name: str
    budget: Decimal
    spent: Decimal
    remaining: Decimal
    pct: int
    status: str  # ok | warn | over
    exhaust_day: int | None = None  # perkiraan tanggal budget kategori ini habis


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
    unbudgeted_spent: Decimal = Decimal(0)  # belanja di kategori tanpa budget
    reserved_recurring: Decimal = Decimal(0)  # tagihan rutin belum jatuh tempo bln ini
    avg_daily_spend: Decimal | None = None  # rata-rata belanja/hari (periode berjalan)
    projected_month_total: Decimal | None = None  # proyeksi total akhir bulan
    categories: list[CategoryBudget] = field(default_factory=list)


def cycle_start_day(db: Session, user_id: int) -> int:
    """Hari mulai siklus budget user (1..28). 1 = bulan kalender biasa (default)."""
    user = db.get(User, user_id)
    d = (user.settings or {}).get("cycle_start_day") if user else None
    return d if isinstance(d, int) and 1 <= d <= 28 else 1


def current_period(day: int = 1) -> str:
    """Label periode (YYYY-MM = bulan tempat siklus DIMULAI) yang memuat hari ini."""
    n = now_local()
    year, mon = n.year, n.month
    if n.day < day:  # belum masuk siklus bulan ini → masih siklus yang mulai bulan lalu
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
    return f"{year:04d}-{mon:02d}"


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


def _spent_by_category(
    db: Session, period: str, user_id: int, day: int = 1
) -> dict[int | None, Decimal]:
    start, end, _ = _bounds(period, day)
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


def _bounds(period: str, day: int = 1) -> tuple[datetime, datetime, int]:
    """Batas siklus untuk `period`. day=1 → identik dengan bulan kalender.

    Siklus berjalan dari (period-month, day) sampai sesaat sebelum bulan berikutnya
    di tanggal yang sama. day dijamin 1..28 sehingga selalu valid tiap bulan.
    """
    year, mon = _period_parts(period)
    start = datetime(year, mon, day, 0, 0, 0, tzinfo=LOCAL_TZ)
    ny, nm = (year, mon + 1) if mon < 12 else (year + 1, 1)
    end = datetime(ny, nm, day, 0, 0, 0, tzinfo=LOCAL_TZ) - timedelta(microseconds=1)
    cycle_len = (end.date() - start.date()).days + 1
    return start, end, cycle_len


def _status(pct: int) -> str:
    if pct >= 100:
        return "over"
    if pct >= 70:
        return "warn"
    return "ok"


def _exhaust_day(
    budget: Decimal | None,
    spent: Decimal,
    day_today: int,
    cycle_len: int,
    start_date: date,
) -> int | None:
    """Tanggal (day-of-month) perkiraan budget habis. None bila tak relevan.

    `day_today`/`cycle_len` adalah posisi & panjang dalam siklus; hasil dikonversi
    ke tanggal kalender via `start_date` agar tetap masuk akal saat siklus custom
    melintasi batas bulan.
    """
    if budget is None or budget <= 0 or spent <= 0 or day_today <= 0:
        return None
    avg = spent / day_today
    if avg <= 0:
        return None
    days_to_go = (budget - spent) / avg
    pos = day_today + int(days_to_go.to_integral_value())
    pos = min(max(pos, day_today), cycle_len)
    return (start_date + timedelta(days=pos - 1)).day


def _pending_recurring_expense(
    db: Session, user_id: int, today: date, period_end: date
) -> Decimal:
    """Total recurring pengeluaran yang belum jatuh tempo di sisa periode ini.

    Dipakai menyisihkan tagihan rutin (kos, langganan) dari "sisa aman", supaya
    safe-to-spend tidak menjanjikan uang yang sebenarnya sudah teralokasi.
    """
    rows = db.scalars(
        select(RecurringTx).where(
            RecurringTx.user_id == user_id,
            RecurringTx.active.is_(True),
            RecurringTx.type == "expense",
            RecurringTx.next_run >= today,
            RecurringTx.next_run <= period_end,
        )
    ).all()
    return sum((r.amount for r in rows), Decimal(0))


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
    day = cycle_start_day(db, user_id)
    period = period or current_period(day)
    start, end, days_in_month = _bounds(period, day)  # days_in_month = panjang siklus
    now = now_local()
    is_current = start <= now <= end
    if is_current:
        day_today = (now.date() - start.date()).days + 1
        days_left = max(days_in_month - day_today + 1, 0)
    else:
        day_today = days_in_month
        days_left = 0

    spent_by_cat = _spent_by_category(db, period, user_id, day)
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
                _prev_spent = _spent_by_category(db, prev_period, user_id, day)
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
        cat_exhaust = (
            _exhaust_day(b, spent, day_today, days_in_month, start.date())
            if is_current
            else None
        )
        categories.append(
            CategoryBudget(
                category_id=cat.id,
                name=cat.name,
                budget=b,
                spent=spent,
                remaining=b - spent,
                pct=pct,
                status=_status(pct) if b > 0 else "ok",
                exhaust_day=cat_exhaust,
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

    # Sisihkan tagihan rutin yang belum jatuh tempo dari "sisa aman" agar jujur.
    reserved_recurring = Decimal(0)
    safe_to_spend = None
    if total_budget is not None and days_left > 0:
        reserved_recurring = _pending_recurring_expense(
            db, user_id, now.date(), end.date()
        )
        remaining_after = total_budget - total_spent - reserved_recurring
        safe_to_spend = max(remaining_after, Decimal(0)) / days_left

    exhaust_day = (
        _exhaust_day(total_budget, total_spent, day_today, days_in_month, start.date())
        if is_current
        else None
    )

    # Belanja di kategori tanpa budget = titik buta yang tidak menggerus envelope.
    unbudgeted_spent = all_spent - sum_budgeted_spent

    # Rata-rata & proyeksi jalan tanpa perlu budget (pakai total belanja sebenarnya).
    avg_daily_spend = None
    projected_month_total = None
    if is_current and day_today > 0:
        avg_daily_spend = all_spent / day_today
        projected_month_total = avg_daily_spend * days_in_month

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
        unbudgeted_spent=unbudgeted_spent,
        reserved_recurring=reserved_recurring,
        avg_daily_spend=avg_daily_spend,
        projected_month_total=projected_month_total,
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
