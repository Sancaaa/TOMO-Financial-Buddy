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

    # CORS — daftar origin dipisah koma, atau "*" untuk semua
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
