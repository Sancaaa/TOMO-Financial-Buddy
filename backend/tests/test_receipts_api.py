from decimal import Decimal

from app.services import ocr

FAKE = {
    "merchant": "Warteg Bahari",
    "date": "2026-07-02",
    "total": 18000,
    "currency": "IDR",
    "category_hint": "Makan",
    "items": [{"name": "Nasi + ayam", "qty": 1, "price": 18000}],
    "is_receipt": True,
    "confidence": 0.9,
}


def test_ocr_endpoint_returns_draft_and_saves_receipt(auth_client, monkeypatch):
    monkeypatch.setattr(ocr, "_call_vision", lambda b, m: FAKE)
    resp = auth_client.post(
        "/transactions/ocr",
        files={"file": ("struk.jpg", b"\xff\xd8\xff-fake-jpeg", "image/jpeg")},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ocr_status"] == "done"
    assert data["merchant"] == "Warteg Bahari"
    assert Decimal(str(data["draft"]["amount"])) == Decimal("18000")

    # konfirmasi → buat transaksi tertaut receipt
    rid = data["receipt_id"]
    draft = data["draft"]
    created = auth_client.post(
        "/transactions",
        json={
            "amount": draft["amount"],
            "type": draft["type"],
            "category_id": draft["category_id"],
            "description": draft["description"],
            "occurred_at": draft["occurred_at"],
            "source": "ocr",
            "receipt_id": rid,
        },
    )
    assert created.status_code == 201, created.text

    # foto struk bisa diambil kembali
    img = auth_client.get(f"/receipts/{rid}/image")
    assert img.status_code == 200

    meta = auth_client.get(f"/receipts/{rid}").json()
    assert meta["ocr_status"] == "done"


def test_ocr_endpoint_failed_extraction(auth_client, monkeypatch):
    def boom(b, m):
        raise RuntimeError("API down")

    monkeypatch.setattr(ocr, "_call_vision", boom)
    resp = auth_client.post(
        "/transactions/ocr",
        files={"file": ("x.jpg", b"data", "image/jpeg")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ocr_status"] == "failed"
    assert body["draft"] is None
