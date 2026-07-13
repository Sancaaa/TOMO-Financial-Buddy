from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    icon: str | None = None
    type: Literal["expense", "income"] = "expense"
    monthly_budget: Decimal | None = None
    budget_rollover: bool = False
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    icon: str | None = None
    type: Literal["expense", "income"] | None = None
    monthly_budget: Decimal | None = None
    budget_rollover: bool | None = None
    parent_id: int | None = None


class CategoryOut(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
