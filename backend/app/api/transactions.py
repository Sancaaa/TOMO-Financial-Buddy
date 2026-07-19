from calendar import monthrange
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.clock import LOCAL_TZ, now_local
from app.core.config import settings
from app.core.database import get_db
from app.models import Account, Category, Transaction, User
from app.schemas.receipt import OCRDraft, OCRItem, OCRResult
from app.schemas.transaction import (
    TransactionCreate,
    TransactionList,
    TransactionOut,
    TransactionQuick,
    TransactionUpdate,
    TransferCreate,
)
from app.services.categorizer import suggest_category
from app.services.ledger import apply_balance
from app.services.parser import parse_quick_input
from app.services.receipts import build_draft, process_receipt

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


def _month_range(month: str) -> tuple[datetime, datetime]:
    """Ubah 'YYYY-MM' menjadi rentang [awal, akhir] bulan tersebut (zona lokal).

    Batas dihitung di LOCAL_TZ agar konsisten dengan analitik & budget
    (lihat summary._month_bounds / budget._bounds), sehingga total di Riwayat
    cocok dengan total di Analitik untuk transaksi di sekitar batas bulan.
    """
    try:
        year, mon = (int(x) for x in month.split("-"))
        start = datetime(year, mon, 1, tzinfo=LOCAL_TZ)
        last_day = monthrange(year, mon)[1]
        end = datetime(year, mon, last_day, 23, 59, 59, 999999, tzinfo=LOCAL_TZ)
    except (ValueError, IndexError):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Format month harus YYYY-MM, contoh 2026-07",
        )
    return start, end


def _assert_owned(db: Session, model, obj_id: int | None, user_id: int, label: str) -> None:
    """Pastikan account/category (bila di-set) milik user; cegah tempel data orang lain."""
    if obj_id is None:
        return
    obj = db.get(model, obj_id)
    if obj is None or obj.user_id != user_id:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{label} tidak ditemukan")


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
    user: User = Depends(get_current_user),
) -> TransactionList:
    filters = [Transaction.user_id == user.id]
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
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Transaction:
    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = now_local()
    _assert_owned(db, Account, data.get("account_id"), user.id, "Akun")
    _assert_owned(db, Account, data.get("dest_account_id"), user.id, "Akun tujuan")
    _assert_owned(db, Category, data.get("category_id"), user.id, "Kategori")
    tx = Transaction(user_id=user.id, **data)
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/quick", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def quick_add(
    payload: TransactionQuick,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Transaction:
    """Quick-add via teks bebas (mis. "makan 15k") — parser sama dengan bot."""
    parsed = parse_quick_input(payload.text, now_local())
    if parsed is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Nominal tidak terbaca. Contoh: makan 15k / gojek 24rb",
        )
    category = suggest_category(db, parsed.description, parsed.type, user.id)
    account = db.scalars(
        select(Account).where(Account.user_id == user.id).order_by(Account.id)
    ).first()
    tx = Transaction(
        user_id=user.id,
        amount=parsed.amount,
        type=parsed.type,
        category_id=category.id if category else None,
        account_id=account.id if account else None,
        description=parsed.description or None,
        occurred_at=parsed.occurred_at,
        source="web",
        raw_input=payload.text,
    )
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/transfer", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transfer(
    payload: TransferCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Transaction:
    """Pindah saldo antar akun (bukan pengeluaran/pemasukan)."""
    if payload.account_id == payload.dest_account_id:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Akun asal dan tujuan harus beda"
        )
    _assert_owned(db, Account, payload.account_id, user.id, "Akun asal")
    _assert_owned(db, Account, payload.dest_account_id, user.id, "Akun tujuan")
    tx = Transaction(
        user_id=user.id,
        amount=payload.amount,
        type="transfer",
        account_id=payload.account_id,
        dest_account_id=payload.dest_account_id,
        description=payload.description,
        occurred_at=payload.occurred_at or now_local(),
        source="web",
    )
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/ocr", response_model=OCRResult)
def ocr_transaction(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
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
    receipt, extraction = process_receipt(db, image_bytes, user.id, media_type)

    if extraction is None:
        return OCRResult(receipt_id=receipt.id, ocr_status=receipt.ocr_status)

    draft = build_draft(db, extraction, user.id)
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


def _get_owned_tx(db: Session, tx_id: int, user_id: int) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None or tx.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaksi tidak ditemukan")
    return tx


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(
    tx_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Transaction:
    return _get_owned_tx(db, tx_id, user.id)


@router.patch("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Transaction:
    tx = _get_owned_tx(db, tx_id, user.id)

    changes = payload.model_dump(exclude_unset=True)
    _assert_owned(db, Account, changes.get("account_id"), user.id, "Akun")
    _assert_owned(db, Category, changes.get("category_id"), user.id, "Kategori")

    # batalkan efek saldo lama, terapkan perubahan, lalu terapkan efek saldo baru
    apply_balance(db, tx, sign=-1)
    for field, value in changes.items():
        setattr(tx, field, value)
    apply_balance(db, tx, sign=1)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    tx = _get_owned_tx(db, tx_id, user.id)
    apply_balance(db, tx, sign=-1)
    db.delete(tx)
    db.commit()

