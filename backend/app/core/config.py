from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://finance:finance@db:5432/finance"

    # Auth / JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 30  # 30 hari — device pribadi

    # User awal (di-seed sekali saat startup jika tabel users kosong)
    initial_username: str = "admin"
    initial_password: str = "changeme"
    telegram_chat_id: str | None = None

    # Telegram bot
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""

    # Zona waktu lokal untuk batas hari & backdate (WIB = +7)
    tz_offset_hours: int = 7

    # OCR (LLM Vision via Google Gemini)
    gemini_api_key: str = ""
    # Default hemat (free-tier); set ke gemini-2.5-pro untuk akurasi maksimal.
    ocr_model: str = "gemini-2.5-flash"
    receipts_dir: str = "/data/receipts"
    ocr_max_image_mb: int = 10

    # CORS — daftar origin dipisah koma, atau "*" untuk semua
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
