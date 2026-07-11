from calendar import monthrange
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models import Transaction
from app.schemas.receipt import OCRDraft, OCRItem, OCRResult
from app.schemas.transaction import (
    TransactionCreate,
    TransactionList,
    TransactionOut,
    TransactionUpdate,
)
from app.services.ledger import apply_balance
from app.services.receipts import build_draft, process_receipt

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


def _month_range(month: str) -> tuple[datetime, datetime]:
    """Ubah 'YYYY-MM' menjadi rentang [awal, akhir) bulan tersebut (UTC)."""
    try:
        year, mon = (int(x) for x in month.split("-"))
        start = datetime(year, mon, 1, tzinfo=timezone.utc)
        last_day = monthrange(year, mon)[1]
        end = datetime(year, mon, last_day, 23, 59, 59, 999999, tzinfo=timezone.utc)
    except (ValueError, IndexError):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Format month harus YYYY-MM, contoh 2026-07",
        )
    return start, end


@router.get("", response_model=TransactionList)
def list_transactions(
    month: str | None = None,
    category_id: int | None = None,
    account_id: int | None = None,
    type: str | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> TransactionList:
    filters = []
    if month is not None:
        start, end = _month_range(month)
        filters.append(Transaction.occurred_at >= start)
        filters.append(Transaction.occurred_at <= end)
    if category_id is not None:
        filters.append(Transaction.category_id == category_id)
    if account_id is not None:
        filters.append(Transaction.account_id == account_id)
    if type is not None:
        filters.append(Transaction.type == type)
    if q:
        filters.append(Transaction.description.ilike(f"%{q}%"))

    total = db.scalar(select(func.count()).select_from(Transaction).where(*filters))
    stmt = (
        select(Transaction)
        .where(*filters)
        .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list(db.scalars(stmt).all())
    return TransactionList(items=items, total=total or 0, limit=limit, offset=offset)


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate, db: Session = Depends(get_db)
) -> Transaction:
    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = datetime.now(timezone.utc)
    tx = Transaction(**data)
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/ocr", response_model=OCRResult)
def ocr_transaction(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> OCRResult:
    """Unggah foto struk → simpan + OCR → kembalikan draft untuk dikonfirmasi.

    Draft belum tersimpan sebagai transaksi; client mengirim POST /transactions
    dengan receipt_id untuk mempersisten.
    """
    image_bytes = file.file.read()
    if len(image_bytes) > settings.ocr_max_image_mb * 1024 * 1024:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"Gambar melebihi {settings.ocr_max_image_mb} MB",
        )
    media_type = file.content_type or "image/jpeg"
    receipt, extraction = process_receipt(db, image_bytes, media_type)

    if extraction is None:
        return OCRResult(receipt_id=receipt.id, ocr_status=receipt.ocr_status)

    draft = build_draft(db, extraction)
    return OCRResult(
        receipt_id=receipt.id,
        ocr_status=receipt.ocr_status,
        merchant=extraction.merchant,
        confidence=extraction.confidence,
        items=[OCRItem(name=i.name, qty=i.qty, price=i.price) for i in extraction.items],
        draft=OCRDraft(
            amount=draft.amount,
            type=draft.type,
            category_id=draft.category_id,
            category_name=draft.category_name,
            description=draft.description,
            occurred_at=draft.occurred_at,
        ),
    )


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaksi tidak ditemukan")
    return tx


@router.patch("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)
) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaksi tidak ditemukan")

    # batalkan efek saldo lama, terapkan perubahan, lalu terapkan efek saldo baru
    apply_balance(db, tx, sign=-1)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)
    apply_balance(db, tx, sign=1)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)) -> None:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaksi tidak ditemukan")
    apply_balance(db, tx, sign=-1)
    db.delete(tx)
    db.commit()

