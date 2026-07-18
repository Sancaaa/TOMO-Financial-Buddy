"""Teks digest harian & review akhir periode untuk dikirim ke Telegram."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.services.budget import current_period, overview
from app.services.money import month_label, rupiah
from app.services.summary import period_summary


def build_daily_digest(db: Session, now: datetime) -> str:
    # Dikirim pagi hari (08:00 lokal) → rekap hari kemarin yang baru saja selesai.
    ref = now - timedelta(days=1)
    day_start = ref.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1) - timedelta(microseconds=1)
    yesterday = period_summary(db, day_start, day_end)
    ov = overview(db, current_period())

    lines = ["🍅 <b>Kabar Tomo kemarin</b>"]
    lines.append(f"Keluar kemarin: <b>{rupiah(yesterday.total_expense)}</b>")
    bulan = f"Bulan ini: {rupiah(ov.total_spent)}"
    if ov.total_budget is not None:
        bulan += f" / {rupiah(ov.total_budget)}"
    lines.append(bulan)
    if ov.safe_to_spend is not None and ov.days_left > 0:
        lines.append(
            f"Aman jajan <b>{rupiah(ov.safe_to_spend)}</b>/hari sampai akhir bulan "
            f"({ov.days_left} hari lagi)"
        )
    return "\n".join(lines)


def build_period_review(db: Session, period: str) -> str:
    ov = overview(db, period)
    lines = [f"📅 <b>Review {month_label(period)}</b>"]
    lines.append(f"Total pengeluaran: <b>{rupiah(ov.total_spent)}</b>")
    if ov.total_budget is not None:
        mark = "✅" if ov.total_spent <= ov.total_budget else "🔴"
        lines.append(f"{mark} Total budget {rupiah(ov.total_budget)}")
    budgeted = [c for c in ov.categories if c.budget > 0]
    if budgeted:
        lines.append("")
        for c in budgeted:
            mark = "✅" if c.spent <= c.budget else "🔴"
            lines.append(f"{mark} {c.name}: {rupiah(c.spent)} / {rupiah(c.budget)}")
    return "\n".join(lines)
