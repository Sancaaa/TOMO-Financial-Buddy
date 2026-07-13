from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    target_amount: Decimal = Field(gt=0)
    saved_amount: Decimal = Decimal("0")
    target_date: date | None = None


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    target_amount: Decimal | None = Field(default=None, gt=0)
    target_date: date | None = None


class GoalContribute(BaseModel):
    amount: Decimal  # boleh negatif untuk menarik


class GoalOut(BaseModel):
    id: int
    name: str
    target_amount: Decimal
    saved_amount: Decimal
    target_date: date | None
    pct: int
    achieved: bool
