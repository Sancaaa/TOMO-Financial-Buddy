"""Jalankan transaksi berulang yang jatuh tempo (kos, langganan)."""

from calendar import monthrange
from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import LOCAL_TZ
from app.models import RecurringTx, Transaction
from app.services.ledger import apply_balance


def next_month_dom(d: date, dom: int) -> date:
    year, mon = d.year, d.month + 1
    if mon > 12:
        mon = 1
        year += 1
    last = monthrange(year, mon)[1]
    return date(year, mon, min(dom, last))


def first_run(dom: int, today: date) -> date:
    """Tanggal jalan pertama untuk day_of_month: bulan ini bila belum lewat, else bulan depan."""
    last = monthrange(today.year, today.month)[1]
    d = date(today.year, today.month, min(dom, last))
    return d if d >= today else next_month_dom(d, dom)


def run_due_recurring(db: Session, today: date) -> int:
    """Buat transaksi untuk tiap recurring yang next_run <= today. Kembalikan jumlah dibuat."""
    due = db.scalars(
        select(RecurringTx).where(
            RecurringTx.active.is_(True), RecurringTx.next_run <= today
        )
    ).all()
    created = 0
    for r in due:
        guard = 0
        while r.active and r.next_run <= today and guard < 12:
            occurred = datetime.combine(r.next_run, time(12, 0), tzinfo=LOCAL_TZ)
            tx = Transaction(
                amount=r.amount,
                type=r.type,
                category_id=r.category_id,
                account_id=r.account_id,
                description=r.description,
                occurred_at=occurred,
                source="recurring",
            )
            db.add(tx)
            db.flush()
            apply_balance(db, tx, sign=1)
            r.last_run = r.next_run
            r.next_run = next_month_dom(r.next_run, r.day_of_month)
            created += 1
            guard += 1
    db.commit()
    return created
