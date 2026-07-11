from decimal import Decimal

from pydantic import BaseModel


class CategorySlice(BaseModel):
    name: str
    total: Decimal


class SummaryOut(BaseModel):
    month: str
    total_expense: Decimal
    total_income: Decimal
    count: int
    per_category: list[CategorySlice]


class TrendPoint(BaseModel):
    month: str
    expense: Decimal
    income: Decimal


class TrendOut(BaseModel):
    points: list[TrendPoint]
