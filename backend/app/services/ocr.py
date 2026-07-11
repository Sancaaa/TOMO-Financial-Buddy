"""Ekstraksi struk/screenshot pembayaran memakai LLM Vision (Google Gemini).

Kirim gambar, terima JSON terstruktur berisi merchant, total, tanggal, item, dan
petunjuk kategori. Panggilan API diisolasi di `_call_vision` agar mudah difake
saat test (tanpa jaringan / API key).
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from decimal import Decimal, InvalidOperation

from app.core.clock import LOCAL_TZ
from app.core.config import settings

log = logging.getLogger("ocr")


@dataclass
class ReceiptItem:
    name: str
    qty: Decimal | None
    price: Decimal | None


@dataclass
class ReceiptExtraction:
    merchant: str | None
    total: Decimal | None
    occurred_at: datetime | None
    currency: str
    category_hint: str | None
    items: list[ReceiptItem] = field(default_factory=list)
    is_receipt: bool = False
    confidence: float = 0.0
    raw: dict = field(default_factory=dict)


_PROMPT = (
    "Ekstrak data dari gambar ini. Bisa berupa struk belanja Indonesia "
    "(Indomaret, Alfamart, GoFood, warung) atau screenshot pembayaran "
    "(GoPay, OVO, DANA, m-banking). Balas HANYA dengan JSON, bentuk persis:\n"
    '{"merchant": string|null, "date": "YYYY-MM-DD"|null, "total": number|null, '
    '"currency": string, "category_hint": string|null, '
    '"items": [{"name": string, "qty": number|null, "price": number|null}], '
    '"is_receipt": boolean, "confidence": number}\n'
    "Aturan:\n"
    "- total: jumlah akhir yang dibayar sebagai angka murni, tanpa titik ribuan "
    "(mis. 32000, bukan 32.000).\n"
    "- date: tanggal pada struk (YYYY-MM-DD) bila ada, selain itu null.\n"
    "- merchant: nama toko/penerima.\n"
    "- items: daftar barang bila terlihat; array kosong bila tidak.\n"
    "- category_hint: tebakan kategori singkat (mis. Makan, Transport).\n"
    "- is_receipt: false jika gambar bukan struk/bukti bayar.\n"
    "- confidence: keyakinan 0..1.\n"
    "Jika suatu nilai tidak terbaca, kembalikan null (jangan mengarang)."
)


def extract_receipt(image_bytes: bytes, media_type: str = "image/jpeg") -> ReceiptExtraction:
    data = _call_vision(image_bytes, media_type)
    return _parse(data)


def _call_vision(image_bytes: bytes, media_type: str) -> dict:
    # impor lokal: dependency hanya perlu di runtime, bukan saat test
    from google import genai
    from google.genai import types

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY belum diset")

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.ocr_model,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
            _PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )
    text = response.text
    if not text:
        raise RuntimeError("respons OCR kosong")
    return json.loads(text)


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _to_datetime(value) -> datetime | None:
    if not value:
        return None
    try:
        d = datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    # jam 12:00 lokal agar tidak bergeser hari saat konversi zona waktu
    return datetime.combine(d, time(12, 0), tzinfo=LOCAL_TZ)


def _parse(data: dict) -> ReceiptExtraction:
    items = [
        ReceiptItem(
            name=str(it.get("name", "")).strip(),
            qty=_to_decimal(it.get("qty")),
            price=_to_decimal(it.get("price")),
        )
        for it in (data.get("items") or [])
        if it.get("name")
    ]
    return ReceiptExtraction(
        merchant=(data.get("merchant") or None),
        total=_to_decimal(data.get("total")),
        occurred_at=_to_datetime(data.get("date")),
        currency=data.get("currency") or "IDR",
        category_hint=(data.get("category_hint") or None),
        items=items,
        is_receipt=bool(data.get("is_receipt", False)),
        confidence=float(data.get("confidence") or 0.0),
        raw=data,
    )
