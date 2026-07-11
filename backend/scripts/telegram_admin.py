"""Kelola webhook Telegram dari CLI.

Contoh:
    python -m scripts.telegram_admin info
    python -m scripts.telegram_admin set https://finance.contohkamu.com/telegram/webhook
    python -m scripts.telegram_admin delete

Butuh TELEGRAM_BOT_TOKEN (dan opsional TELEGRAM_WEBHOOK_SECRET) di environment/.env.
"""

import sys

from app.bot.telegram_client import TelegramClient
from app.core.config import settings


def main(argv: list[str]) -> int:
    if not settings.telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN belum diset.")
        return 1
    tg = TelegramClient()
    cmd = argv[0] if argv else "info"

    if cmd == "info":
        print(tg.get_me())
    elif cmd == "set":
        if len(argv) < 2:
            print("Butuh URL. Contoh: set https://domain/telegram/webhook")
            return 1
        print(tg.set_webhook(argv[1], secret_token=settings.telegram_webhook_secret or None))
    elif cmd == "delete":
        print(tg.delete_webhook())
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
