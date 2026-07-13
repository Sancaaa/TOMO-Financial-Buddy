# Backend — TOMO (友) · Fase 1–6

FastAPI + PostgreSQL. Auth JWT, CRUD transaksi/kategori/akun, analitik, **budgeting +
otomasi** (scheduler), bot Telegram (quick-add + auto-kategori + `/budget`), dan OCR
struk via LLM Vision. Menyajikan web PWA sebagai satu origin.

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
| POST | `/transactions/quick` | Quick-add teks bebas (parser sama dgn bot) |
| POST | `/transactions/transfer` | Pindah saldo antar akun (type `transfer`) |
| POST | `/transactions/ocr` | Upload foto struk (multipart) → draft transaksi + receipt_id |
| GET | `/receipts/{id}` · `/receipts/{id}/image` | Metadata / foto struk |
| GET | `/analytics/summary` · `/analytics/trend` | Ringkasan bulan / tren |
| GET | `/budgets` · `/budgets/safe-to-spend` | Progress budget + safe-to-spend |
| PUT | `/budgets` | Set budget total/kategori (body: category_id, amount, period) |
| GET/POST/PATCH/DELETE | `/recurring` | Transaksi berulang bulanan |
| GET/POST/PATCH/DELETE | `/goals` · `POST /goals/{id}/contribute` | Target nabung (saving goals) |
| GET | `/export?month=` | Export transaksi CSV |
| POST | `/telegram/webhook` | Entry point bot (diverifikasi via secret header) |
| GET | `/health` | Health check |

Semua endpoint kecuali `/auth/login`, `/telegram/webhook`, dan `/health` butuh header
`Authorization: Bearer <token>`.

## OCR struk (Fase 3)

Foto struk (Indomaret, Alfamart, GoFood, warung) atau screenshot e-wallet (GoPay,
OVO, DANA, m-banking) diekstrak jadi transaksi via LLM Vision (Google Gemini).

- **Bot Telegram:** kirim foto → Tomo baca → transaksi tercatat (source `ocr`) dengan
  tombol koreksi ✏️/🗑, plus foto tersimpan dan tertaut ke transaksi.
- **Web/API:** `POST /transactions/ocr` mengembalikan draft (belum tersimpan); client
  konfirmasi lewat `POST /transactions` dengan `receipt_id`.

Alur (`app/services/receipts.py`): simpan foto (`storage.py`) → ekstrak
(`ocr.py`, panggilan Gemini diisolasi di `_call_vision` sehingga bisa difake saat
test) → tebak kategori pakai categorizer Fase 2. Hasil mentah LLM disimpan di
`receipts.ocr_raw`, jadi kalau ekstraksi salah tak perlu foto ulang.

### Setup OCR

Isi `GEMINI_API_KEY` dari [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
(free-tier akun Google/student sudah cukup). `OCR_MODEL` default `gemini-2.5-flash`
(hemat, sesuai budget NFR-5); ganti ke `gemini-2.5-pro` untuk akurasi maksimal. Foto
disimpan di volume `receipts` (`RECEIPTS_DIR`, default `/data/receipts`).

## Telegram bot (Fase 2)

Ketik ke bot tanpa perintah untuk mencatat: `makan 15k`, `gojek 24rb`,
`kemarin nasi padang 25.000`, `dapet 50k dari nyokap`. Bot membalas dengan konfirmasi +
tombol inline **✏️ Kategori** / **🗑 Hapus**. Mengoreksi kategori mengajari bot untuk
input serupa berikutnya.

Perintah: `/hariini`, `/minggu`, `/bulan` (ringkasan), `/budget` (lihat/atur budget, mis.
`/budget makan 900rb` atau `/budget total 2jt`), `/undo`, `/help`. Setiap quick-add
pengeluaran menambahkan baris safe-to-spend bila budget total sudah diset.

### Setup

1. Buat bot via [@BotFather](https://t.me/BotFather), salin token ke `TELEGRAM_BOT_TOKEN`.
2. Isi `TELEGRAM_WEBHOOK_SECRET` (secret acak) dan `DOMAIN` (butuh HTTPS publik).
3. Deploy, lalu daftarkan webhook:
   ```bash
   docker compose exec api python -m scripts.telegram_admin set https://DOMAIN/telegram/webhook
   ```
4. Kirim pesan pertama ke bot. Karena `chat_id` belum terdaftar, bot membalas dengan
   `chat_id` kamu — masukkan ke `TELEGRAM_CHAT_ID`, restart, selesai. Bot hanya
   merespons chat_id itu.

Modul inti bisa dites tanpa jaringan/DB Postgres: parser (`app/services/parser.py`),
kategorizer (`app/services/categorizer.py`), dan dispatcher (`app/bot/dispatcher.py`,
klien Telegram di-inject sehingga bisa difake).

## Budgeting & otomasi (Fase 5)

- **Budget** (`app/services/budget.py`): default per-kategori (`Category.monthly_budget`),
  override per-periode + budget total (tabel `budgets`). `overview()` menghitung progress
  (terpakai/sisa/persen + status hijau/kuning/merah), **safe-to-spend** (sisa ÷ sisa hari),
  dan proyeksi tanggal habis.
- **Scheduler** (`app/scheduler.py`, APScheduler): satu job harian jam `DIGEST_HOUR` lokal
  yang menjalankan transaksi berulang jatuh tempo, mengirim digest harian, cek alert budget
  (80%/100%, sekali per ambang/periode via tabel `budget_alerts`), dan di tanggal 1 kirim
  review bulan sebelumnya ke Telegram. Dimatikan saat test lewat `SCHEDULER_ENABLED=false`.
- **Recurring** (`app/services/recurring.py`): transaksi berulang bulanan (`day_of_month`),
  catch-up bila server sempat mati.
- Fungsi job/service dites langsung (bukan timing scheduler): lihat `tests/test_budget.py`,
  `test_recurring.py`, `test_budget_bot.py`.

## Fase 6 (opsional)

- **Transfer antar akun**: `POST /transactions/transfer` membuat tx type `transfer` yang
  mengurangi akun sumber & menambah akun tujuan (`app/services/ledger.py`); tidak dihitung
  sebagai pengeluaran/pemasukan di analitik & budget. Kolom baru `transactions.dest_account_id`.
- **Rollover budget**: kolom `categories.budget_rollover`; bila aktif, `budget.overview` menambah
  sisa positif budget bulan lalu ke budget bulan ini.
- **Saving goals**: model `saving_goals`, endpoint `/goals` (+ `/contribute`).
- Tidak dibangun (opsional sisa): siklus budget non-kalender, import CSV mutasi, split bill.

## Catatan

- Skema dibuat via `Base.metadata.create_all` saat startup (tabel baru seperti
  `keyword_rules`, `receipts`, `budgets`, `budget_alerts`, `recurring_txs` ikut dibuat
  otomatis). Untuk kolom baru pada tabel lama (mis. `transactions.receipt_id`),
  `app/core/schema_sync.py` menjalankan `ADD COLUMN IF NOT EXISTS` di Postgres sebagai
  stopgap sampai Alembic diperkenalkan.
- Saldo akun otomatis disesuaikan: `expense` mengurangi, `income` menambah. `transfer`
  belum diproses ke saldo (double-entry menyusul di fase berikutnya).
