from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

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
