from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Account
from app.schemas.account import (
    AccountCreate,
    AccountOut,
    AccountUpdate,
    NetWorthOut,
    ReconcileChange,
    ReconcileOut,
)
from app.services.ledger import reconcile_balances

router = APIRouter(
    prefix="/accounts", tags=["accounts"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)) -> list[Account]:
    return list(db.scalars(select(Account).order_by(Account.name)).all())


@router.get("/net-worth", response_model=NetWorthOut)
def net_worth(db: Session = Depends(get_db)) -> NetWorthOut:
    """Total kekayaan bersih = jumlah saldo semua akun.

    Transfer & tabungan-goal adalah perpindahan antar akun (net nol), jadi jumlah
    ini mencerminkan uang riil yang dimiliki.
    """
    accounts = list(db.scalars(select(Account).order_by(Account.name)).all())
    total = sum((a.balance for a in accounts), Decimal(0))
    return NetWorthOut(total=total, accounts=accounts)


@router.post("/reconcile", response_model=ReconcileOut)
def reconcile(db: Session = Depends(get_db)) -> ReconcileOut:
    """Hitung ulang saldo dari transaksi; koreksi bila ada yang meleset."""
    changes = reconcile_balances(db)
    accounts = list(db.scalars(select(Account).order_by(Account.name)).all())
    return ReconcileOut(
        corrected=len(changes),
        changes=[ReconcileChange(**c) for c in changes],
        accounts=accounts,
    )


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)) -> Account:
    account = Account(**payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)
) -> Account:
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Akun tidak ditemukan")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(account, field, value)
    if "balance" in data:
        # saldo diedit manual → jadikan kondisi baru sebagai baseline rekonsiliasi
        account.opening_balance = None
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)) -> None:
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Akun tidak ditemukan")
    db.delete(account)
    db.commit()
