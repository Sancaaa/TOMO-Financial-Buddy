from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Account
from app.schemas.account import AccountCreate, AccountOut, AccountUpdate

router = APIRouter(
    prefix="/accounts", tags=["accounts"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)) -> list[Account]:
    return list(db.scalars(select(Account).order_by(Account.name)).all())


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
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
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
