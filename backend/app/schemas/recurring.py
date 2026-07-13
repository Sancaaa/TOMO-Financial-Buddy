from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class RecurringBase(BaseModel):
    amount: Decimal = Field(gt=0)
    type: Literal["expense", "income"] = "expense"
    category_id: int | None = None
    account_id: int | None = None
    description: str | None = Field(default=None, max_length=255)
    day_of_month: int = Field(ge=1, le=28)


class RecurringCreate(RecurringBase):
    pass


class RecurringUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    type: Literal["expense", "income"] | None = None
    category_id: int | None = None
    account_id: int | None = None
    description: str | None = Field(default=None, max_length=255)
    day_of_month: int | None = Field(default=None, ge=1, le=28)
    active: bool | None = None


class RecurringOut(RecurringBase):
    id: int
    active: bool
    next_run: date
    last_run: date | None

    model_config = {"from_attributes": True}
