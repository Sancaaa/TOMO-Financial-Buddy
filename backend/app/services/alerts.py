"""Cek ambang budget (80% & 100%) dan hasilkan pesan alert, dedup per periode."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BudgetAlert
from app.services.budget import current_period, cycle_start_day, overview
from app.services.money import rupiah

_THRESHOLDS = (80, 100)


def _already_sent(
    db: Session, category_id: int | None, period: str, threshold: int, user_id: int
) -> bool:
    stmt = select(BudgetAlert).where(
        BudgetAlert.user_id == user_id,
        BudgetAlert.period == period,
        BudgetAlert.threshold == threshold,
    )
    stmt = stmt.where(
        BudgetAlert.category_id.is_(None)
        if category_id is None
        else BudgetAlert.category_id == category_id
    )
    return db.scalar(stmt) is not None


def _message(name: str, pct: int, spent: Decimal, budget: Decimal, threshold: int) -> str:
    if threshold >= 100:
        return f"🍅 Budget {name} jebol! {pct}% — {rupiah(spent)} dari {rupiah(budget)}."
    return f"🍅 Budget {name} sudah {pct}% nih — {rupiah(spent)} dari {rupiah(budget)}. Pelan-pelan ya."


def _crossed_targets(ov) -> list[tuple[int | None, str, Decimal, Decimal]]:
    targets: list[tuple[int | None, str, Decimal, Decimal]] = [
        (c.category_id, c.name, c.budget, c.spent) for c in ov.categories if c.budget > 0
    ]
    if ov.total_budget and ov.total_budget > 0:
        targets.append((None, "Total", ov.total_budget, ov.total_spent))
    return targets


def preview_budget_alerts(db: Session, user_id: int, period: str | None = None) -> list[str]:
    """Ambang budget yang saat ini terlewati — untuk banner web.

    Read-only: TIDAK menandai dedup, jadi selalu mencerminkan keadaan sekarang
    (beda dari `check_budget_alerts` yang dipakai job harian sekali-per-ambang).
    """
    ov = overview(db, user_id, period)  # overview memakai default siklus bila None
    messages: list[str] = []
    for category_id, name, budget, spent in _crossed_targets(ov):
        pct = int((spent / budget * 100).to_integral_value())
        crossed = [t for t in _THRESHOLDS if pct >= t]
        if crossed:
            messages.append(_message(name, pct, spent, budget, max(crossed)))
    return messages


def check_budget_alerts(db: Session, user_id: int, period: str | None = None) -> list[str]:
    period = period or current_period(cycle_start_day(db, user_id))
    ov = overview(db, user_id, period)

    messages: list[str] = []
    for category_id, name, budget, spent in _crossed_targets(ov):
        pct = int((spent / budget * 100).to_integral_value())
        for threshold in _THRESHOLDS:
            if pct >= threshold and not _already_sent(db, category_id, period, threshold, user_id):
                db.add(
                    BudgetAlert(
                        user_id=user_id, category_id=category_id,
                        period=period, threshold=threshold,
                    )
                )
                messages.append(_message(name, pct, spent, budget, threshold))
    db.commit()
    return messages
