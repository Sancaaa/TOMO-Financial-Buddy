from decimal import Decimal

from sqlalchemy import select

from app.core.clock import now_local
from app.models import Category, Transaction
from app.services.alerts import check_budget_alerts


def _makan_id(auth_client) -> int:
    return next(c for c in auth_client.get("/categories").json() if c["name"] == "Makan")["id"]


def test_budget_overview_and_safe_to_spend(auth_client):
    makan = _makan_id(auth_client)
    assert auth_client.put("/budgets", json={"category_id": makan, "amount": 900000}).status_code == 204
    assert auth_client.put("/budgets", json={"category_id": None, "amount": 2000000}).status_code == 204
    auth_client.post("/transactions", json={"amount": 300000, "type": "expense", "category_id": makan})

    ov = auth_client.get("/budgets").json()
    assert float(ov["total_budget"]) == 2000000
    assert ov["total_budget_explicit"] is True
    assert float(ov["total_spent"]) == 300000
    cat = next(c for c in ov["categories"] if c["category_id"] == makan)
    assert float(cat["budget"]) == 900000
    assert float(cat["spent"]) == 300000
    assert cat["pct"] == 33
    assert cat["status"] == "ok"

    sts = auth_client.get("/budgets/safe-to-spend").json()
    assert sts["safe_to_spend"] is not None
    assert float(sts["total_budget"]) == 2000000


def test_budget_status_transitions(auth_client):
    makan = _makan_id(auth_client)
    auth_client.put("/budgets", json={"category_id": makan, "amount": 100000})
    auth_client.post("/transactions", json={"amount": 80000, "type": "expense", "category_id": makan})
    cat = next(c for c in auth_client.get("/budgets").json()["categories"] if c["category_id"] == makan)
    assert cat["status"] == "warn" and cat["pct"] == 80

    auth_client.post("/transactions", json={"amount": 40000, "type": "expense", "category_id": makan})
    cat = next(c for c in auth_client.get("/budgets").json()["categories"] if c["category_id"] == makan)
    assert cat["status"] == "over" and cat["pct"] == 120


def test_budget_default_derived_from_categories(auth_client):
    # tanpa budget total eksplisit, total diturunkan dari jumlah budget kategori
    makan = _makan_id(auth_client)
    auth_client.put("/budgets", json={"category_id": makan, "amount": 500000})
    ov = auth_client.get("/budgets").json()
    assert float(ov["total_budget"]) == 500000
    assert ov["total_budget_explicit"] is False


def _cat_id(auth_client, name):
    return next(c for c in auth_client.get("/categories").json() if c["name"] == name)["id"]


def test_derived_total_counts_only_budgeted_spending(auth_client):
    # total diturunkan dari budget Makan; belanja di kategori tak-berbudget (Hiburan)
    # TIDAK boleh menggerus envelope total.
    makan, hiburan = _cat_id(auth_client, "Makan"), _cat_id(auth_client, "Hiburan")
    auth_client.put("/budgets", json={"category_id": makan, "amount": 500000})
    auth_client.post("/transactions", json={"amount": 200000, "type": "expense", "category_id": makan})
    auth_client.post("/transactions", json={"amount": 300000, "type": "expense", "category_id": hiburan})

    ov = auth_client.get("/budgets").json()
    assert ov["total_budget_explicit"] is False
    assert float(ov["total_budget"]) == 500000
    assert float(ov["total_spent"]) == 200000   # hanya Makan, bukan Hiburan
    assert float(ov["total_remaining"]) == 300000


def test_explicit_total_counts_all_spending(auth_client):
    # total eksplisit = payung → semua belanja dihitung (termasuk tak-berbudget)
    makan, hiburan = _cat_id(auth_client, "Makan"), _cat_id(auth_client, "Hiburan")
    auth_client.put("/budgets", json={"category_id": None, "amount": 1000000})
    auth_client.post("/transactions", json={"amount": 200000, "type": "expense", "category_id": makan})
    auth_client.post("/transactions", json={"amount": 300000, "type": "expense", "category_id": hiburan})

    ov = auth_client.get("/budgets").json()
    assert ov["total_budget_explicit"] is True
    assert float(ov["total_spent"]) == 500000
    assert float(ov["total_remaining"]) == 500000


def _spend_today(db, category_name, amount):
    cat = db.scalar(select(Category).where(Category.name == category_name))
    db.add(Transaction(amount=Decimal(amount), type="expense", category_id=cat.id, occurred_at=now_local()))
    db.commit()
    return cat


def test_budget_alerts_dedup(db):
    cat = db.scalar(select(Category).where(Category.name == "Makan"))
    cat.monthly_budget = Decimal(100000)
    db.commit()

    _spend_today(db, "Makan", 85000)
    msgs = check_budget_alerts(db)
    assert any("80" in m or "sudah" in m for m in msgs)
    # rerun → tidak dobel
    assert check_budget_alerts(db) == []

    _spend_today(db, "Makan", 20000)  # total 105k → jebol
    msgs2 = check_budget_alerts(db)
    assert any("jebol" in m for m in msgs2)
