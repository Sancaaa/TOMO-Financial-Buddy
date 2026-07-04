from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, auth, categories, transactions
from app.core.database import Base, SessionLocal, engine
from app.core.config import settings
from app.seed import seed

# pastikan semua model terdaftar di metadata sebelum create_all
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fase 1: create_all + seed. Migrasi Alembic diperkenalkan saat skema
    # mulai berevolusi di fase berikutnya.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(
    title="Finance Tracker API",
    version="0.1.0",
    description="Backend fondasi (Fase 1): auth, transaksi, kategori, akun.",
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


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
