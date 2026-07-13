"""Cek ambang budget (80% & 100%) dan hasilkan pesan alert, dedup per periode."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BudgetAlert
from app.services.budget import current_period, overview
from app.services.money import rupiah

_THRESHOLDS = (80, 100)


def _already_sent(db: Session, category_id: int | None, period: str, threshold: int) -> bool:
    stmt = select(BudgetAlert).where(
        BudgetAlert.period == period, BudgetAlert.threshold == threshold
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


def check_budget_alerts(db: Session, period: str | None = None) -> list[str]:
    period = period or current_period()
    ov = overview(db, period)

    targets: list[tuple[int | None, str, Decimal, Decimal]] = [
        (c.category_id, c.name, c.budget, c.spent) for c in ov.categories if c.budget > 0
    ]
    if ov.total_budget and ov.total_budget > 0:
        targets.append((None, "Total", ov.total_budget, ov.total_spent))

    messages: list[str] = []
    for category_id, name, budget, spent in targets:
        pct = int((spent / budget * 100).to_integral_value())
        for threshold in _THRESHOLDS:
            if pct >= threshold and not _already_sent(db, category_id, period, threshold):
                db.add(BudgetAlert(category_id=category_id, period=period, threshold=threshold))
                messages.append(_message(name, pct, spent, budget, threshold))
    db.commit()
    return messages
