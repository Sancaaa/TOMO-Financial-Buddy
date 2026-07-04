from calendar import monthrange
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Account, Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionList,
    TransactionOut,
    TransactionUpdate,
)

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


def _apply_balance(db: Session, tx: Transaction, sign: int) -> None:
    """Sesuaikan saldo akun. sign=+1 menerapkan tx, sign=-1 membatalkannya.

    expense mengurangi saldo, income menambah. transfer tidak diproses di sini
    (double-entry transfer menyusul di fase berikutnya).
    """
    if tx.account_id is None or tx.type == "transfer":
        return
    account = db.get(Account, tx.account_id)
    if account is None:
        return
    direction = Decimal(1) if tx.type == "income" else Decimal(-1)
    account.balance = account.balance + direction * tx.amount * sign


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
    _apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)
    return tx


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
    _apply_balance(db, tx, sign=-1)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)
    _apply_balance(db, tx, sign=1)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)) -> None:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaksi tidak ditemukan")
    _apply_balance(db, tx, sign=-1)
    db.delete(tx)
    db.commit()
