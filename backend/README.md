# Backend — Finance Tracker (Fase 1)

FastAPI + PostgreSQL. Menyediakan auth JWT dan CRUD untuk transaksi, kategori, dan akun.

## Menjalankan dengan Docker (disarankan)

Dari root repo (`D:\Project\financeTracker`):

```bash
cp .env.example .env      # lalu edit password & secret di .env
docker compose up -d --build
```

- API di balik Caddy: `http://localhost` (atau domain di `DOMAIN`).
- Dokumentasi interaktif: `http://localhost/docs`.
- Saat pertama start, tabel dibuat otomatis dan diisi: user awal (`INITIAL_USERNAME`/`INITIAL_PASSWORD`), 12 kategori default, dan akun "Cash".

## Menjalankan lokal (tanpa Docker, untuk dev)

Butuh PostgreSQL lokal, atau set `DATABASE_URL` ke instans lain.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://finance:finance@localhost:5432/finance
uvicorn app.main:app --reload
```

## Menjalankan test

Test memakai SQLite sementara — tidak butuh PostgreSQL.

```bash
cd backend
pip install pytest httpx
pytest -q
```

## Endpoint (Fase 1)

| Method | Path | Keterangan |
|---|---|---|
| POST | `/auth/login` | Form `username`+`password` → JWT bearer |
| GET | `/auth/me` | Info user terautentikasi |
| GET/POST | `/transactions` | List (filter: `month`, `category_id`, `account_id`, `type`, `q`, `limit`, `offset`) / buat |
| GET/PATCH/DELETE | `/transactions/{id}` | Detail / ubah / hapus (saldo akun ikut disesuaikan) |
| GET/POST | `/categories` | List (filter `type`) / buat |
| PATCH/DELETE | `/categories/{id}` | Ubah / hapus |
| GET/POST | `/accounts` | List / buat |
| PATCH/DELETE | `/accounts/{id}` | Ubah / hapus |
| GET | `/health` | Health check |

Semua endpoint kecuali `/auth/login` dan `/health` butuh header `Authorization: Bearer <token>`.

## Catatan

- Skema dibuat via `Base.metadata.create_all` saat startup. Alembic akan diperkenalkan
  saat skema mulai berevolusi (Fase 3 OCR, Fase 5 budgeting).
- Saldo akun otomatis disesuaikan: `expense` mengurangi, `income` menambah. `transfer`
  belum diproses ke saldo (double-entry menyusul di fase berikutnya).
