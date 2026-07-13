import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.transactions import _month_range
from app.core.database import get_db
from app.models import Transaction

router = APIRouter(tags=["export"], dependencies=[Depends(get_current_user)])


@router.get("/export")
def export_csv(month: str | None = None, db: Session = Depends(get_db)) -> StreamingResponse:
    stmt = select(Transaction).order_by(Transaction.occurred_at)
    if month is not None:
        start, end = _month_range(month)
        stmt = stmt.where(Transaction.occurred_at >= start, Transaction.occurred_at <= end)
    rows = db.scalars(stmt).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["tanggal", "tipe", "kategori", "akun", "deskripsi", "jumlah", "sumber"])
    for tx in rows:
        writer.writerow([
            tx.occurred_at.isoformat(),
            tx.type,
            tx.category.name if tx.category else "",
            tx.account.name if tx.account else "",
            tx.description or "",
            f"{tx.amount}",
            tx.source,
        ])
    buffer.seek(0)
    filename = f"tomo-{month or 'semua'}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
