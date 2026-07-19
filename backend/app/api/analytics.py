from calendar import monthrange
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.clock import LOCAL_TZ, now_local
from app.core.database import get_db
from app.models import User
from app.schemas.analytics import CategorySlice, SummaryOut, TrendOut, TrendPoint
from app.services.summary import monthly_trend, period_summary

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
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrendOut:
    points = monthly_trend(db, months, now_local(), user.id)
    return TrendOut(
        points=[
            TrendPoint(month=p.month, expense=p.expense, income=p.income) for p in points
        ]
    )
