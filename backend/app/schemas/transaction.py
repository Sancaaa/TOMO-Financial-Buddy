from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.account import AccountOut
from app.schemas.category import CategoryOut


class TransactionBase(BaseModel):
    amount: Decimal = Field(gt=0)
    type: Literal["expense", "income", "transfer"] = "expense"
    category_id: int | None = None
    account_id: int | None = None
    description: str | None = Field(default=None, max_length=255)
    occurred_at: datetime | None = None


class TransactionCreate(TransactionBase):
    source: str = "web"
    raw_input: str | None = None


class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    type: Literal["expense", "income", "transfer"] | None = None
    category_id: int | None = None
    account_id: int | None = None
    description: str | None = Field(default=None, max_length=255)
    occurred_at: datetime | None = None


class TransactionOut(BaseModel):
    id: int
    amount: Decimal
    type: str
    category_id: int | None
    account_id: int | None
    description: str | None
    occurred_at: datetime
    source: str
    created_at: datetime
    category: CategoryOut | None = None
    account: AccountOut | None = None

    model_config = {"from_attributes": True}


class TransactionList(BaseModel):
    items: list[TransactionOut]
    total: int
    limit: int
    offset: int
