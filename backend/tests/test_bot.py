from decimal import Decimal

from sqlalchemy import func, select

from app.bot.dispatcher import handle_update
from app.models import Category, Receipt, Transaction
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


def _photo_update():
    return {"message": {"chat": {"id": CHAT}, "photo": [{"file_id": "f1"}], "message_id": 1}}


def _msg(text):
    return {"message": {"chat": {"id": CHAT}, "text": text, "message_id": 1}}


def _tx_count(db):
    return db.scalar(select(func.count()).select_from(Transaction))


def test_unauthorized_chat_creates_nothing(db):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg, allowed_chat_id="999")
    assert "chat_id" in tg.sent[0][1]
    assert _tx_count(db) == 0


def test_quick_add_creates_transaction(db):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg, allowed_chat_id=str(CHAT))
    txs = db.scalars(select(Transaction)).all()
    assert len(txs) == 1
    assert txs[0].amount == Decimal(15000)
    assert txs[0].source == "telegram"
    assert "Tercatat" in tg.sent[0][1]
    assert tg.sent[0][2]["inline_keyboard"]  # ada tombol koreksi


_FAKE_RECEIPT = {
    "merchant": "Alfamart", "date": "2026-07-03", "total": 25000, "currency": "IDR",
    "category_hint": "belanja", "items": [{"name": "Snack", "qty": 1, "price": 25000}],
    "is_receipt": True, "confidence": 0.9,
}


def test_photo_ocr_creates_transaction(db, monkeypatch):
    monkeypatch.setattr(ocr, "_call_vision", lambda b, m: _FAKE_RECEIPT)
    tg = FakeTG()
    handle_update(_photo_update(), db, tg, allowed_chat_id=str(CHAT))

    tx = db.scalars(select(Transaction)).first()
    assert tx is not None
    assert tx.amount == Decimal(25000)
    assert tx.source == "ocr"
    assert tx.receipt_id is not None
    receipt = db.get(Receipt, tx.receipt_id)
    assert receipt.ocr_status == "done"
    assert any("Tercatat" in s[1] for s in tg.sent)


def test_photo_ocr_failure_no_transaction(db, monkeypatch):
    def boom(b, m):
        raise RuntimeError("vision down")

    monkeypatch.setattr(ocr, "_call_vision", boom)
    tg = FakeTG()
    handle_update(_photo_update(), db, tg, allowed_chat_id=str(CHAT))
    assert _tx_count(db) == 0
    assert any("belum terbaca" in s[1] for s in tg.sent)


def test_summary_hariini(db):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg, allowed_chat_id=str(CHAT))
    handle_update(_msg("/hariini"), db, tg, allowed_chat_id=str(CHAT))
    assert "Pengeluaran" in tg.sent[-1][1]
    assert "Rp15.000" in tg.sent[-1][1]


def test_undo_removes_last(db):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg, allowed_chat_id=str(CHAT))
    handle_update(_msg("/undo"), db, tg, allowed_chat_id=str(CHAT))
    assert _tx_count(db) == 0


def test_callback_change_category_and_learn(db):
    tg = FakeTG()
    handle_update(_msg("topup xyz 10k"), db, tg, allowed_chat_id=str(CHAT))
    tx = db.scalars(select(Transaction)).first()
    assert tx.category.name == "Lainnya"  # tebakan awal

    hiburan = db.scalar(select(Category).where(Category.name == "Hiburan"))
    callback = {
        "callback_query": {
            "id": "c1",
            "data": f"sc:{tx.id}:{hiburan.id}",
            "message": {"chat": {"id": CHAT}, "message_id": 2},
        }
    }
    handle_update(callback, db, tg, allowed_chat_id=str(CHAT))
    db.refresh(tx)
    assert tx.category_id == hiburan.id
    # bot belajar: input serupa kini menuju Hiburan
    assert suggest_category(db, "topup xyz beli", "expense").name == "Hiburan"


def test_callback_delete(db):
    tg = FakeTG()
    handle_update(_msg("makan 15k"), db, tg, allowed_chat_id=str(CHAT))
    tx = db.scalars(select(Transaction)).first()
    callback = {
        "callback_query": {
            "id": "c2",
            "data": f"del:{tx.id}",
            "message": {"chat": {"id": CHAT}, "message_id": 2},
        }
    }
    handle_update(callback, db, tg, allowed_chat_id=str(CHAT))
    assert _tx_count(db) == 0
