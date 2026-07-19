from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.models import Account, RecurringTx, Transaction
from app.services.recurring import first_run, next_month_dom, run_due_recurring


def test_next_month_dom_and_first_run():
    assert next_month_dom(date(2026, 7, 1), 1) == date(2026, 8, 1)
    assert next_month_dom(date(2026, 12, 5), 5) == date(2027, 1, 5)
    # day 31 → clamp ke akhir Februari
    assert next_month_dom(date(2026, 1, 31), 31) == date(2026, 2, 28)
    # first_run: dom belum lewat bulan ini
    assert first_run(20, date(2026, 7, 10)) == date(2026, 7, 20)
    # dom sudah lewat → bulan depan
    assert first_run(5, date(2026, 7, 10)) == date(2026, 8, 5)


def test_run_due_recurring(db, uid):
    acc = db.scalars(select(Account)).first()
    r = RecurringTx(
        user_id=uid, amount=Decimal(800000), type="expense", account_id=acc.id,
        description="Kos", day_of_month=1, next_run=date(2026, 7, 1),
    )
    db.add(r)
    db.commit()

    created = run_due_recurring(db, date(2026, 7, 15))
    assert created == 1
    txs = db.scalars(select(Transaction).where(Transaction.source == "recurring")).all()
    assert len(txs) == 1 and txs[0].amount == Decimal(800000)
    db.refresh(r)
    assert r.next_run == date(2026, 8, 1)
    assert r.last_run == date(2026, 7, 1)
    # akun saldo turun
    db.refresh(acc)
    assert acc.balance == Decimal(-800000)

    # jalan lagi hari sama → tidak ada yang jatuh tempo
    assert run_due_recurring(db, date(2026, 7, 15)) == 0


def test_run_due_recurring_catches_up(db, uid):
    r = RecurringTx(user_id=uid, amount=Decimal(50000), type="expense", day_of_month=1, next_run=date(2026, 5, 1))
    db.add(r)
    db.commit()
    # dari Mei sampai Juli = 3 kejadian (Mei, Jun, Jul)
    created = run_due_recurring(db, date(2026, 7, 3))
    assert created == 3
    db.refresh(r)
    assert r.next_run == date(2026, 8, 1)


def test_recurring_api(auth_client):
    resp = auth_client.post(
        "/recurring",
        json={"amount": 50000, "type": "expense", "day_of_month": 5, "description": "Spotify"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["next_run"].endswith("-05")

    assert len(auth_client.get("/recurring").json()) == 1
    assert auth_client.delete(f"/recurring/{body['id']}").status_code == 204
    assert auth_client.get("/recurring").json() == []
