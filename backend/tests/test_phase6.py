from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import select

from app.core.clock import LOCAL_TZ, now_local
from app.models import Category, Transaction
from app.services.budget import _prev_period, current_period, overview


# ---------- Transfer antar akun ----------

def _accounts_by_name(auth_client):
    return {a["name"]: a for a in auth_client.get("/accounts").json()}


def test_transfer_moves_balance_and_reverses(auth_client):
    auth_client.post("/accounts", json={"name": "GoPay", "type": "ewallet", "balance": 100000})
    accs = _accounts_by_name(auth_client)
    cash, gopay = accs["Cash"]["id"], accs["GoPay"]["id"]

    resp = auth_client.post(
        "/transactions/transfer",
        json={"amount": 30000, "account_id": cash, "dest_account_id": gopay},
    )
    assert resp.status_code == 201, resp.text
    tx = resp.json()
    assert tx["type"] == "transfer" and tx["dest_account_id"] == gopay

    accs = _accounts_by_name(auth_client)
    assert float(accs["Cash"]["balance"]) == -30000
    assert float(accs["GoPay"]["balance"]) == 130000

    # transfer tidak masuk pengeluaran/pemasukan
    summary = auth_client.get("/analytics/summary").json()
    assert float(summary["total_expense"]) == 0
    assert float(summary["total_income"]) == 0

    # hapus transfer → saldo balik
    auth_client.delete(f"/transactions/{tx['id']}")
    accs = _accounts_by_name(auth_client)
    assert float(accs["Cash"]["balance"]) == 0
    assert float(accs["GoPay"]["balance"]) == 100000


def test_transfer_same_account_rejected(auth_client):
    cash = _accounts_by_name(auth_client)["Cash"]["id"]
    resp = auth_client.post(
        "/transactions/transfer",
        json={"amount": 1000, "account_id": cash, "dest_account_id": cash},
    )
    assert resp.status_code == 422


# ---------- Rollover budget ----------

def _spend_at(db, name, amount, occ):
    cat = db.scalar(select(Category).where(Category.name == name))
    db.add(Transaction(amount=Decimal(amount), type="expense", category_id=cat.id, occurred_at=occ))
    db.commit()


def test_rollover_adds_prev_leftover(db):
    makan = db.scalar(select(Category).where(Category.name == "Makan"))
    makan.monthly_budget = Decimal(100000)
    makan.budget_rollover = True
    db.commit()

    prev = _prev_period(current_period())
    py, pm = (int(x) for x in prev.split("-"))
    _spend_at(db, "Makan", 30000, datetime(py, pm, 15, 12, 0, tzinfo=LOCAL_TZ))  # sisa 70k
    _spend_at(db, "Makan", 20000, now_local())

    cat = next(c for c in overview(db).categories if c.name == "Makan")
    assert cat.budget == Decimal(170000)  # 100k + 70k rollover
    assert cat.spent == Decimal(20000)


def test_no_rollover_when_flag_off(db):
    makan = db.scalar(select(Category).where(Category.name == "Makan"))
    makan.monthly_budget = Decimal(100000)
    makan.budget_rollover = False
    db.commit()
    prev = _prev_period(current_period())
    py, pm = (int(x) for x in prev.split("-"))
    _spend_at(db, "Makan", 30000, datetime(py, pm, 15, 12, 0, tzinfo=LOCAL_TZ))

    cat = next(c for c in overview(db).categories if c.name == "Makan")
    assert cat.budget == Decimal(100000)


# ---------- Saving goals ----------

def test_goal_lifecycle(auth_client):
    g = auth_client.post("/goals", json={"name": "Laptop baru", "target_amount": 5000000}).json()
    assert g["pct"] == 0 and g["achieved"] is False

    g2 = auth_client.post(f"/goals/{g['id']}/contribute", json={"amount": 2000000}).json()
    assert float(g2["saved_amount"]) == 2000000 and g2["pct"] == 40

    g3 = auth_client.post(f"/goals/{g['id']}/contribute", json={"amount": 3000000}).json()
    assert g3["achieved"] is True and g3["pct"] == 100

    # tarik melebihi saldo → mentok 0
    g4 = auth_client.post(f"/goals/{g['id']}/contribute", json={"amount": -9999999999}).json()
    assert float(g4["saved_amount"]) == 0

    assert auth_client.delete(f"/goals/{g['id']}").status_code == 204
    assert auth_client.get("/goals").json() == []
