import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from app.api import (
    accounts,
    analytics,
    auth,
    budgets,
    categories,
    export,
    goals,
    receipts,
    recurring,
    telegram,
    transactions,
)
from app.core.database import Base, SessionLocal, engine
from app.core.config import settings
from app.core.schema_sync import ensure_schema
from app.seed import seed

# pastikan semua model terdaftar di metadata sebelum create_all
import app.models  # noqa: F401


class SPAStaticFiles(StaticFiles):
    """StaticFiles dengan fallback ke index.html (client-side routing PWA)."""

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema(engine)  # tambah kolom baru pada tabel lama (Postgres)
    with SessionLocal() as db:
        seed(db)

    scheduler = None
    if settings.scheduler_enabled:
        from app.scheduler import build_scheduler

        scheduler = build_scheduler()
        scheduler.start()
    try:
        yield
    finally:
        if scheduler is not None:
            scheduler.shutdown(wait=False)


app = FastAPI(
    title="TOMO API",
    version="0.6.0",
    description="Backend TOMO (友) — finance tracker: auth, transaksi, transfer, kategori, akun, analitik, budgeting (+rollover), saving goals, otomasi, bot Telegram, OCR struk, web PWA.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(accounts.router)
app.include_router(receipts.router)
app.include_router(analytics.router)
app.include_router(budgets.router)
app.include_router(recurring.router)
app.include_router(goals.router)
app.include_router(export.router)
app.include_router(telegram.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Sajikan web PWA (build Vite) bila STATIC_DIR di-set. Dipasang paling akhir agar
# rute API menang; sisanya jatuh ke index.html untuk routing sisi klien.
if settings.static_dir and os.path.isdir(settings.static_dir):
    app.mount(
        "/", SPAStaticFiles(directory=settings.static_dir, html=True), name="spa"
    )
