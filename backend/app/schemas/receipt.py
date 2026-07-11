from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OCRItem(BaseModel):
    name: str
    qty: Decimal | None = None
    price: Decimal | None = None


class OCRDraft(BaseModel):
    amount: Decimal | None
    type: str
    category_id: int | None
    category_name: str | None
    description: str | None
    occurred_at: datetime


class OCRResult(BaseModel):
    receipt_id: int
    ocr_status: str
    merchant: str | None = None
    confidence: float = 0.0
    items: list[OCRItem] = []
    draft: OCRDraft | None = None


class ReceiptOut(BaseModel):
    id: int
    ocr_status: str
    merchant: str | None
    total: Decimal | None
    occurred_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
