from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    type: Literal["cash", "bank", "ewallet"] = "cash"
    balance: Decimal = Decimal("0")


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    type: Literal["cash", "bank", "ewallet"] | None = None
    balance: Decimal | None = None


class AccountOut(AccountBase):
    id: int

    model_config = {"from_attributes": True}


class NetWorthOut(BaseModel):
    """Total kekayaan = jumlah saldo semua akun (+ rincian per akun)."""

    total: Decimal
    accounts: list[AccountOut]


class ReconcileChange(BaseModel):
    id: int
    name: str
    before: Decimal
    after: Decimal


class ReconcileOut(BaseModel):
    """Hasil rekonsiliasi: berapa akun dikoreksi + saldo terkini."""

    corrected: int
    changes: list[ReconcileChange]
    accounts: list[AccountOut]
