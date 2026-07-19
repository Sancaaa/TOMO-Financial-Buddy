"""Scheduler in-process (APScheduler): recurring tx, digest harian, alert budget, review.

Satu job harian pada `digest_hour` (waktu lokal). Recurring dijalankan sekali untuk
semua user; digest/alert/review dibangun & dikirim per-user ke Telegram masing-masing
(user yang sudah menautkan `telegram_chat_id`). Di tanggal 1, ikut kirim review
bulan sebelumnya.
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.bot.telegram_client import TelegramClient
from app.core.clock import now_local
from app.core.config import settings
from app.core.database import SessionLocal
from app.models import User
from app.services.alerts import check_budget_alerts
from app.services.digest import build_daily_digest, build_period_review
from app.services.recurring import run_due_recurring

log = logging.getLogger("scheduler")


def _prev_period(now: datetime) -> str:
    year, mon = now.year, now.month - 1
    if mon == 0:
        mon = 12
        year -= 1
    return f"{year:04d}-{mon:02d}"


def _send(chat_id: str, messages: list[str]) -> None:
    if not (chat_id and settings.telegram_bot_token):
        return
    tg = TelegramClient()
    for msg in messages:
        if msg:
            try:
                tg.send_message(chat_id, msg)
            except Exception:
                log.exception("gagal kirim pesan scheduler")


def daily_job() -> None:
    now = now_local()
    with SessionLocal() as db:
        # recurring untuk semua user sekaligus (tiap tx mewarisi user_id-nya)
        try:
            run_due_recurring(db, now.date())
        except Exception:
            log.exception("recurring gagal")

        # digest + alert + review per user yang menautkan Telegram
        users = db.scalars(
            select(User).where(User.telegram_chat_id.is_not(None))
        ).all()
        for user in users:
            outbox: list[str] = []
            try:
                outbox.append(build_daily_digest(db, now, user.id))
            except Exception:
                log.exception("digest gagal untuk user %s", user.id)
            try:
                outbox.extend(check_budget_alerts(db, user.id))
            except Exception:
                log.exception("alert budget gagal untuk user %s", user.id)
            if now.day == 1:
                try:
                    outbox.append(build_period_review(db, _prev_period(now), user.id))
                except Exception:
                    log.exception("review periode gagal untuk user %s", user.id)
            _send(user.telegram_chat_id, outbox)


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    utc_hour = (settings.digest_hour - settings.tz_offset_hours) % 24
    scheduler.add_job(daily_job, "cron", hour=utc_hour, minute=0, id="daily")
    return scheduler
