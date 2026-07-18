from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import select

from app.core.clock import LOCAL_TZ, now_local
from app.models import Account, Category, Transaction
from app.services.budget import _prev_period, current_period, overview
from app.services.ledger import apply_balance, reconcile_balances


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


# ---------- Net worth ----------

def test_net_worth_sums_accounts_and_ignores_transfers(auth_client):
    auth_client.post("/accounts", json={"name": "Bank", "type": "bank", "balance": 500000})
    auth_client.post("/accounts", json={"name": "GoPay", "type": "ewallet", "balance": 150000})

    nw = auth_client.get("/accounts/net-worth").json()
    assert float(nw["total"]) == 650000  # Cash 0 + Bank 500k + GoPay 150k
    assert {a["name"] for a in nw["accounts"]} >= {"Cash", "Bank", "GoPay"}

    accs = _accounts_by_name(auth_client)
    # transfer antar akun → net worth tetap
    auth_client.post(
        "/transactions/transfer",
        json={"amount": 100000, "account_id": accs["Bank"]["id"], "dest_account_id": accs["GoPay"]["id"]},
    )
    assert float(auth_client.get("/accounts/net-worth").json()["total"]) == 650000

    # pengeluaran → net worth turun
    auth_client.post(
        "/transactions",
        json={"amount": 50000, "type": "expense", "account_id": accs["Cash"]["id"]},
    )
    assert float(auth_client.get("/accounts/net-worth").json()["total"]) == 600000


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


def test_goal_contribution_moves_real_money(auth_client):
    auth_client.post("/accounts", json={"name": "Tabungan", "type": "bank", "balance": 0})
    accs = _accounts_by_name(auth_client)
    cash, tab = accs["Cash"]["id"], accs["Tabungan"]["id"]

    g = auth_client.post(
        "/goals",
        json={"name": "Liburan", "target_amount": 1000000, "account_id": tab},
    ).json()
    assert g["account_id"] == tab

    # nabung 300k dari Cash → Cash -300k, Tabungan +300k, progres 300k (30%)
    g2 = auth_client.post(
        f"/goals/{g['id']}/contribute",
        json={"amount": 300000, "from_account_id": cash},
    ).json()
    assert float(g2["saved_amount"]) == 300000 and g2["pct"] == 30
    accs = _accounts_by_name(auth_client)
    assert float(accs["Cash"]["balance"]) == -300000
    assert float(accs["Tabungan"]["balance"]) == 300000

    # tercatat sebagai transfer (bukan pengeluaran) di riwayat
    summary = auth_client.get("/analytics/summary").json()
    assert float(summary["total_expense"]) == 0
    txs = auth_client.get("/transactions", params={"type": "transfer"}).json()
    assert any(t["description"] == "Nabung: Liburan" for t in txs["items"])

    # tarik 100k → Tabungan -100k, Cash +100k, progres 200k
    g3 = auth_client.post(
        f"/goals/{g['id']}/contribute",
        json={"amount": -100000, "from_account_id": cash},
    ).json()
    assert float(g3["saved_amount"]) == 200000
    accs = _accounts_by_name(auth_client)
    assert float(accs["Cash"]["balance"]) == -200000
    assert float(accs["Tabungan"]["balance"]) == 200000


# ---------- Rekonsiliasi saldo ----------

def test_reconcile_fixes_drift(db):
    acc = Account(name="Dompet", type="cash", balance=Decimal(0))
    db.add(acc)
    db.commit()

    # transaksi normal lewat apply_balance → saldo benar (50k)
    tx = Transaction(amount=Decimal(50000), type="income", account_id=acc.id, occurred_at=now_local())
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    assert acc.balance == Decimal(50000)

    # run pertama: tetapkan baseline, tak ada koreksi
    assert reconcile_balances(db) == []
    assert acc.opening_balance == Decimal(0)

    # DRIFT: transaksi masuk TANPA apply_balance (mis. import/bug)
    ghost = Transaction(amount=Decimal(20000), type="expense", account_id=acc.id, occurred_at=now_local())
    db.add(ghost)
    db.commit()
    assert acc.balance == Decimal(50000)  # saldo belum ikut turun → meleset

    changes = reconcile_balances(db)
    assert len(changes) == 1 and changes[0]["after"] == Decimal(30000)
    db.refresh(acc)
    assert acc.balance == Decimal(30000)  # 0 + 50k - 20k


def test_reconcile_endpoint_and_manual_edit_rebaselines(auth_client):
    acc = auth_client.post("/accounts", json={"name": "Bank", "type": "bank", "balance": 100000}).json()

    # baseline: 0 dikoreksi
    r = auth_client.post("/accounts/reconcile").json()
    assert r["corrected"] == 0

    # belanja 30k → saldo 70k
    auth_client.post("/transactions", json={"amount": 30000, "type": "expense", "account_id": acc["id"]})

    # edit saldo manual → 200k, harus jadi baseline baru (bukan ditimpa reconcile)
    auth_client.patch(f"/accounts/{acc['id']}", json={"balance": 200000})
    r2 = auth_client.post("/accounts/reconcile").json()
    assert r2["corrected"] == 0
    bal = next(a for a in r2["accounts"] if a["id"] == acc["id"])["balance"]
    assert float(bal) == 200000


def test_goal_contribution_without_savings_account_rejected(auth_client):
    cash = _accounts_by_name(auth_client)["Cash"]["id"]
    g = auth_client.post(
        "/goals", json={"name": "Tanpa akun", "target_amount": 500000}
    ).json()
    assert g["account_id"] is None
    # kirim akun sumber padahal target tak punya akun tabungan → 422
    resp = auth_client.post(
        f"/goals/{g['id']}/contribute",
        json={"amount": 1000, "from_account_id": cash},
    )
    assert resp.status_code == 422
    # tanpa akun sumber tetap boleh (mode counter)
    g2 = auth_client.post(
        f"/goals/{g['id']}/contribute", json={"amount": 1000}
    ).json()
    assert float(g2["saved_amount"]) == 1000
