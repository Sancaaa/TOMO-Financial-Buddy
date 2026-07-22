from calendar import monthrange
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.clock import LOCAL_TZ, now_local
from app.core.database import get_db
from app.models import User
from app.schemas.analytics import (
    CategorySlice,
    ComparisonOut,
    HeatmapDay,
    HeatmapOut,
    MerchantStatOut,
    SummaryOut,
    TopMerchantsOut,
    TrendOut,
    TrendPoint,
)
from app.services.summary import (
    daily_expense,
    monthly_trend,
    period_summary,
    spending_comparison,
    top_merchants,
)

router = APIRouter(
    prefix="/analytics", tags=["analytics"], dependencies=[Depends(get_current_user)]
)


def _month_range(month: str | None) -> tuple[str, datetime, datetime]:
    now = now_local()
    if month is None:
        year, mon = now.year, now.month
    else:
        try:
            year, mon = (int(x) for x in month.split("-"))
            datetime(year, mon, 1)
        except (ValueError, IndexError):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Format month harus YYYY-MM"
            )
    start = datetime(year, mon, 1, 0, 0, 0, tzinfo=LOCAL_TZ)
    last = monthrange(year, mon)[1]
    end = datetime(year, mon, last, 23, 59, 59, 999999, tzinfo=LOCAL_TZ)
    return f"{year:04d}-{mon:02d}", start, end


@router.get("/summary", response_model=SummaryOut)
def summary(
    month: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SummaryOut:
    label, start, end = _month_range(month)
    s = period_summary(db, start, end, user.id)
    return SummaryOut(
        month=label,
        total_expense=s.total_expense,
        total_income=s.total_income,
        count=s.count,
        per_category=[CategorySlice(name=c.name, total=c.total) for c in s.per_category],
    )


@router.get("/trend", response_model=TrendOut)
def trend(
    months: int = Query(6, ge=1, le=24),
    month: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrendOut:
    # `month` (YYYY-MM) menganchor tren agar berakhir di bulan yang dipilih di UI.
    _, _, end = _month_range(month) if month else (None, None, now_local())
    points = monthly_trend(db, months, end, user.id)
    return TrendOut(
        points=[
            TrendPoint(month=p.month, expense=p.expense, income=p.income) for p in points
        ]
    )


@router.get("/comparison", response_model=ComparisonOut)
def comparison(
    month: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ComparisonOut:
    label, _, _ = _month_range(month)
    year, mon = (int(x) for x in label.split("-"))
    c = spending_comparison(db, year, mon, user.id)
    return ComparisonOut(
        month=c.month,
        prev_month=c.prev_month,
        total_expense=c.total_expense,
        prev_total_expense=c.prev_total_expense,
        pct=c.pct,
        up=c.up,
        driver_category=c.driver_category,
        driver_delta=c.driver_delta,
    )


@router.get("/heatmap", response_model=HeatmapOut)
def heatmap(
    month: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> HeatmapOut:
    label, _, _ = _month_range(month)
    year, mon = (int(x) for x in label.split("-"))
    first_weekday, days_in_month = monthrange(year, mon)
    totals = daily_expense(db, year, mon, user.id)
    return HeatmapOut(
        month=label,
        days_in_month=days_in_month,
        first_weekday=first_weekday,
        days=[HeatmapDay(day=d, total=totals.get(d, 0)) for d in range(1, days_in_month + 1)],
    )


@router.get("/top-merchants", response_model=TopMerchantsOut)
def top_merchants_endpoint(
    month: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TopMerchantsOut:
    label, _, _ = _month_range(month)
    year, mon = (int(x) for x in label.split("-"))
    merchants = top_merchants(db, year, mon, user.id)
    return TopMerchantsOut(
        month=label,
        merchants=[
            MerchantStatOut(merchant=m.merchant, total=m.total, count=m.count)
            for m in merchants
        ],
    )
