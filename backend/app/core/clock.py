from datetime import datetime, timedelta, timezone

from app.core.config import settings

LOCAL_TZ = timezone(timedelta(hours=settings.tz_offset_hours))


def now_local() -> datetime:
    """Waktu sekarang di zona lokal (default WIB, +7)."""
    return datetime.now(LOCAL_TZ)
