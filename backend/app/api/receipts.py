from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Receipt, User
from app.schemas.receipt import ReceiptOut

router = APIRouter(
    prefix="/receipts", tags=["receipts"], dependencies=[Depends(get_current_user)]
)


@router.get("/{receipt_id}", response_model=ReceiptOut)
def get_receipt(
    receipt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Receipt:
    receipt = db.get(Receipt, receipt_id)
    if receipt is None or receipt.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Struk tidak ditemukan")
    return receipt


@router.get("/{receipt_id}/image")
def get_receipt_image(
    receipt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> FileResponse:
    receipt = db.get(Receipt, receipt_id)
    if (
        receipt is None
        or receipt.user_id != user.id
        or not Path(receipt.file_path).exists()
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto struk tidak ditemukan")
    return FileResponse(receipt.file_path)
