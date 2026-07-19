from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.bot.dispatcher import handle_update
from app.models import Category, Receipt, Transaction, User
from app.services import ocr
from app.services.categorizer import suggest_category

CHAT = 123


class FakeTG:
    def __init__(self):
        self.sent = []
        self.edits = []
        self.answers = []
        self.file_bytes = b"fake-image"

    def send_message(self, chat_id, text, reply_markup=None):
        self.sent.append((chat_id, text, reply_markup))
        return {"ok": True}

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None):
        self.edits.append((chat_id, message_id, text, reply_markup))
        return {"ok": True}

    def answer_callback_query(self, cq_id, text=None):
        self.answers.append((cq_id, text))
        return {"ok": True}

    def get_file(self, file_id):
        return "photos/file.jpg"

    def download_file(self, file_path):
        return self.file_bytes


@pytest.fixture()
def admin(db):
    """Admin ter-seed, ditautkan ke CHAT agar bot mengenalinya."""
    user = db.scalar(select(User))
    user.telegram_chat_id = str(CHAT)
    db.commit()
    return user


def _photo_update(chat=CHAT):
    return {"message": {"chat": {"id": chat}, "photo": [{"file_id": "f1"}], "message_id": 1}}


def _msg(text, chat=CHAT):
    return {"message": {"chat": {"id": chat}, "text": text, "message_id": 1}}


def _tx_count(db):
    return db.scalar(select(func.count()).select_from(Transaction))


def test_unauthorized_chat_creates_nothing(db, admin):
    tg = FakeTG()
    handle_update(_msg("makan 15k", chat=999), db, tg)  # chat tak terikat user mana pun
    assert "chat_id" in tg.sent[0][1]
    assert _tx_count(db) == 0


def test_quick_add_creates_transaction(db, admin):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg)
    txs = db.scalars(select(Transaction)).all()
    assert len(txs) == 1
    assert txs[0].amount == Decimal(15000)
    assert txs[0].source == "telegram"
    assert txs[0].user_id == admin.id
    assert "Tercatat" in tg.sent[0][1]
    assert tg.sent[0][2]["inline_keyboard"]  # ada tombol koreksi


_FAKE_RECEIPT = {
    "merchant": "Alfamart", "date": "2026-07-03", "total": 25000, "currency": "IDR",
    "category_hint": "belanja", "items": [{"name": "Snack", "qty": 1, "price": 25000}],
    "is_receipt": True, "confidence": 0.9,
}


def test_photo_ocr_creates_transaction(db, admin, monkeypatch):
    monkeypatch.setattr(ocr, "_call_vision", lambda b, m: _FAKE_RECEIPT)
    tg = FakeTG()
    handle_update(_photo_update(), db, tg)

    tx = db.scalars(select(Transaction)).first()
    assert tx is not None
    assert tx.amount == Decimal(25000)
    assert tx.source == "ocr"
    assert tx.receipt_id is not None
    receipt = db.get(Receipt, tx.receipt_id)
    assert receipt.ocr_status == "done"
    assert receipt.user_id == admin.id
    assert any("Tercatat" in s[1] for s in tg.sent)


def test_photo_ocr_failure_no_transaction(db, admin, monkeypatch):
    def boom(b, m):
        raise RuntimeError("vision down")

    monkeypatch.setattr(ocr, "_call_vision", boom)
    tg = FakeTG()
    handle_update(_photo_update(), db, tg)
    assert _tx_count(db) == 0
    assert any("belum terbaca" in s[1] for s in tg.sent)


def test_summary_hariini(db, admin):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg)
    handle_update(_msg("/hariini"), db, tg)
    assert "Pengeluaran" in tg.sent[-1][1]
    assert "Rp15.000" in tg.sent[-1][1]


def test_undo_removes_last(db, admin):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg)
    handle_update(_msg("/undo"), db, tg)
    assert _tx_count(db) == 0


def test_callback_change_category_and_learn(db, admin):
    tg = FakeTG()
    handle_update(_msg("topup xyz 10k"), db, tg)
    tx = db.scalars(select(Transaction)).first()
    assert tx.category.name == "Lainnya"  # tebakan awal

    hiburan = db.scalar(
        select(Category).where(Category.user_id == admin.id, Category.name == "Hiburan")
    )
    callback = {
        "callback_query": {
            "id": "c1",
            "data": f"sc:{tx.id}:{hiburan.id}",
            "message": {"chat": {"id": CHAT}, "message_id": 2},
        }
    }
    handle_update(callback, db, tg)
    db.refresh(tx)
    assert tx.category_id == hiburan.id
    # bot belajar: input serupa kini menuju Hiburan
    assert suggest_category(db, "topup xyz beli", "expense", admin.id).name == "Hiburan"


def test_callback_delete(db, admin):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg)
    tx = db.scalars(select(Transaction)).first()
    callback = {
        "callback_query": {
            "id": "c2",
            "data": f"del:{tx.id}",
            "message": {"chat": {"id": CHAT}, "message_id": 2},
        }
    }
    handle_update(callback, db, tg)
    assert _tx_count(db) == 0


def test_link_binds_chat(db):
    """User dengan kode /link bisa menautkan chat baru."""
    from datetime import timedelta
    from app.core.clock import now_local

    user = db.scalar(select(User))
    user.settings = {
        "link_code": "ABC123",
        "link_expires": (now_local() + timedelta(minutes=5)).isoformat(),
    }
    db.commit()

    tg = FakeTG()
    handle_update(_msg("/link ABC123", chat=555), db, tg)
    db.refresh(user)
    assert user.telegram_chat_id == "555"
    assert "Terhubung" in tg.sent[0][1]
    # sesudah tertaut, catat transaksi jalan
    handle_update(_msg("kopi 18k", chat=555), db, tg)
    assert _tx_count(db) == 1
