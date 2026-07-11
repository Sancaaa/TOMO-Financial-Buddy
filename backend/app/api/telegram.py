import logging

from fastapi import APIRouter, Body, Depends, Header, Response, status
from sqlalchemy.orm import Session

from app.bot.dispatcher import handle_update
from app.bot.telegram_client import TelegramClient
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/telegram", tags=["telegram"])
log = logging.getLogger("telegram")


@router.post("/webhook")
def webhook(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    secret: str | None = Header(None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    # Verifikasi secret_token yang dikirim Telegram (jika dikonfigurasi).
    if settings.telegram_webhook_secret and secret != settings.telegram_webhook_secret:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    try:
        handle_update(
            payload, db, TelegramClient(), settings.telegram_chat_id or None
        )
    except Exception:  # jangan sampai Telegram retry tanpa henti
        log.exception("gagal memproses update telegram")

    return {"ok": True}
