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


class ComparisonOut(BaseModel):
    month: str
    prev_month: str
    total_expense: Decimal
    prev_total_expense: Decimal
    pct: int | None
    up: bool
    driver_category: str | None
    driver_delta: Decimal | None


class HeatmapDay(BaseModel):
    day: int
    total: Decimal


class HeatmapOut(BaseModel):
    month: str
    days_in_month: int
    first_weekday: int  # 0=Senin .. 6=Minggu (weekday tgl 1)
    days: list[HeatmapDay]


class MerchantStatOut(BaseModel):
    merchant: str
    total: Decimal
    count: int


class TopMerchantsOut(BaseModel):
    month: str
    merchants: list[MerchantStatOut]
