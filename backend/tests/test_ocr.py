from decimal import Decimal

from app.services import ocr

FAKE = {
    "merchant": "Indomaret",
    "date": "2026-07-01",
    "total": 32000,
    "currency": "IDR",
    "category_hint": "belanja",
    "items": [
        {"name": "Aqua 600ml", "qty": 2, "price": 6000},
        {"name": "Roti", "qty": 1, "price": 20000},
    ],
    "is_receipt": True,
    "confidence": 0.95,
}


def test_extract_parses_fields(monkeypatch):
    monkeypatch.setattr(ocr, "_call_vision", lambda b, m: FAKE)
    result = ocr.extract_receipt(b"img", "image/jpeg")
    assert result.merchant == "Indomaret"
    assert result.total == Decimal("32000")
    assert result.occurred_at.year == 2026 and result.occurred_at.month == 7
    assert result.is_receipt is True
    assert len(result.items) == 2
    assert result.items[0].price == Decimal("6000")


def test_extract_handles_nulls(monkeypatch):
    data = {
        "merchant": None, "date": None, "total": None, "currency": "IDR",
        "category_hint": None, "items": [], "is_receipt": False, "confidence": 0.1,
    }
    monkeypatch.setattr(ocr, "_call_vision", lambda b, m: data)
    result = ocr.extract_receipt(b"img", "image/jpeg")
    assert result.total is None
    assert result.occurred_at is None
    assert result.is_receipt is False
    assert result.items == []
