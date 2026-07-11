"""Alur OCR struk: simpan foto, ekstrak via LLM, bangun draft transaksi.

Dipakai bersama oleh endpoint web (`/transactions/ocr`) dan bot Telegram.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.clock import now_local
from app.models import Receipt
from app.services import ocr as ocr_service
from app.services.categorizer import suggest_category
from app.services.storage import save_receipt

log = logging.getLogger("receipts")


@dataclass
class Draft:
    amount: Decimal | None
    type: str
    category_id: int | None
    category_name: str | None
    description: str | None
    occurred_at: datetime


def process_receipt(
    db: Session, image_bytes: bytes, media_type: str = "image/jpeg"
) -> tuple[Receipt, ocr_service.ReceiptExtraction | None]:
    """Simpan foto + jalankan OCR. Kembalikan (receipt, extraction|None)."""
    path = save_receipt(image_bytes, media_type)
    receipt = Receipt(file_path=path, ocr_status="pending")
    db.add(receipt)
    db.flush()

    extraction: ocr_service.ReceiptExtraction | None = None
    try:
        extraction = ocr_service.extract_receipt(image_bytes, media_type)
        receipt.ocr_raw = extraction.raw
        receipt.merchant = extraction.merchant
        receipt.total = extraction.total
        receipt.occurred_at = extraction.occurred_at
        receipt.ocr_status = (
            "done" if extraction.is_receipt and extraction.total is not None else "failed"
        )
    except Exception:
        log.exception("OCR gagal untuk receipt %s", receipt.id)
        receipt.ocr_status = "failed"

    db.commit()
    db.refresh(receipt)
    if receipt.ocr_status != "done":
        extraction = None
    return receipt, extraction


def build_draft(db: Session, extraction: ocr_service.ReceiptExtraction) -> Draft:
    """Rakit draft transaksi dari hasil ekstraksi, plus tebakan kategori."""
    item_text = " ".join(i.name for i in extraction.items)
    hint = " ".join(filter(None, [extraction.merchant, extraction.category_hint, item_text]))
    category = suggest_category(db, hint, "expense")
    return Draft(
        amount=extraction.total,
        type="expense",
        category_id=category.id if category else None,
        category_name=category.name if category else None,
        description=extraction.merchant or "Struk",
        occurred_at=extraction.occurred_at or now_local(),
    )
