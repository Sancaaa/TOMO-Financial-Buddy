from decimal import Decimal

from sqlalchemy import select

from app.bot.dispatcher import handle_update
from app.models import Category
from app.services.budget import set_budget

CHAT = 123


class FakeTG:
    def __init__(self):
        self.sent = []

    def send_message(self, chat_id, text, reply_markup=None):
        self.sent.append((chat_id, text, reply_markup))
        return {"ok": True}

    def edit_message_text(self, *a, **k):
        return {"ok": True}

    def answer_callback_query(self, *a, **k):
        return {"ok": True}


def _msg(text):
    return {"message": {"chat": {"id": CHAT}, "text": text, "message_id": 1}}


def test_budget_set_category(db):
    tg = FakeTG()
    handle_update(_msg("/budget makan 900rb"), db, tg, allowed_chat_id=str(CHAT))
    assert "di-set" in tg.sent[-1][1]
    makan = db.scalar(select(Category).where(Category.name == "Makan"))
    assert makan.monthly_budget == Decimal(900000)


def test_budget_set_total_and_show(db):
    tg = FakeTG()
    handle_update(_msg("/budget total 2jt"), db, tg, allowed_chat_id=str(CHAT))
    assert "di-set" in tg.sent[-1][1]
    handle_update(_msg("/budget"), db, tg, allowed_chat_id=str(CHAT))
    text = tg.sent[-1][1]
    assert "Budget" in text and "Total" in text


def test_budget_unknown_category(db):
    tg = FakeTG()
    handle_update(_msg("/budget xyz 100rb"), db, tg, allowed_chat_id=str(CHAT))
    assert "tak ketemu" in tg.sent[-1][1]


def test_quickadd_appends_safe_to_spend(db):
    set_budget(db, None, Decimal(2000000), None)
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg, allowed_chat_id=str(CHAT))
    assert any("Aman jajan" in s[1] for s in tg.sent)


def test_export_csv(auth_client):
    makan = next(c for c in auth_client.get("/categories").json() if c["name"] == "Makan")["id"]
    auth_client.post(
        "/transactions",
        json={"amount": 15000, "type": "expense", "category_id": makan, "description": "nasi goreng"},
    )
    resp = auth_client.get("/export")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    body = resp.text
    assert "tanggal" in body and "nasi goreng" in body
