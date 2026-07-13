"""Scheduler in-process (APScheduler): recurring tx, digest harian, alert budget, review.

Satu job harian pada `digest_hour` (waktu lokal). Di tanggal 1, ikut kirim review
bulan sebelumnya. Kirim ke Telegram bila token & chat_id dikonfigurasi.
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.bot.telegram_client import TelegramClient
from app.core.clock import now_local
from app.core.config import settings
from app.core.database import SessionLocal
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


def _send(messages: list[str]) -> None:
    if not (settings.telegram_chat_id and settings.telegram_bot_token):
        return
    tg = TelegramClient()
    for msg in messages:
        if msg:
            try:
                tg.send_message(settings.telegram_chat_id, msg)
            except Exception:
                log.exception("gagal kirim pesan scheduler")


def daily_job() -> None:
    now = now_local()
    outbox: list[str] = []
    with SessionLocal() as db:
        try:
            run_due_recurring(db, now.date())
        except Exception:
            log.exception("recurring gagal")
        try:
            outbox.append(build_daily_digest(db, now))
        except Exception:
            log.exception("digest gagal")
        try:
            outbox.extend(check_budget_alerts(db))
        except Exception:
            log.exception("alert budget gagal")
        if now.day == 1:
            try:
                outbox.append(build_period_review(db, _prev_period(now)))
            except Exception:
                log.exception("review periode gagal")
    _send(outbox)


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    utc_hour = (settings.digest_hour - settings.tz_offset_hours) % 24
    scheduler.add_job(daily_job, "cron", hour=utc_hour, minute=0, id="daily")
    return scheduler
