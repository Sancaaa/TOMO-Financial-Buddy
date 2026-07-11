# TOMO 🍅

**TOMO** (友, "teman") adalah finance tracker pribadi yang dirancang agar **mencatat lebih
cepat daripada malas** — pencatat keuangan yang terasa seperti teman, dengan maskot si tomat.
Satu backend, tiga pintu masuk: Telegram bot, web app (PWA), dan Android.

## Fitur Utama

- ⚡ **Quick-add**: ketik `makan 15k` di Telegram → tercatat lengkap dengan kategori otomatis
- 📸 **OCR struk**: foto struk / screenshot e-wallet → transaksi draft tinggal dikonfirmasi
- 📊 **Analitik**: dashboard tren, heatmap, perbandingan bulanan
- 💰 **Budgeting**: budget per kategori, safe-to-spend harian, alert 80%/100%, proyeksi tanggal habis
- 🔁 **Otomasi**: transaksi berulang (kos, langganan), daily digest, review akhir periode

## Dokumentasi

- [Arsitektur Sistem](docs/ARCHITECTURE.md) — komponen, tech stack, skema DB, API, deployment
- [Requirement & Fitur](docs/REQUIREMENTS.md) — functional/non-functional requirements, prioritas, acceptance criteria
- [Design System](docs/DESIGN.md) — identitas visual, palet warna, tipografi, maskot, komponen UI

## Tech Stack (ringkas)

FastAPI · PostgreSQL · React PWA · Telegram Bot API (webhook) · Gemini Vision (OCR) · Docker Compose · Caddy

## Status

- ✅ **Fase 1 — Fondasi**: API (auth JWT, CRUD transaksi/kategori/akun), Docker + Caddy
- ✅ **Fase 2 — Telegram bot**: quick-add parser, auto-kategori yang belajar dari koreksi, tombol inline, ringkasan `/hariini` `/minggu` `/bulan`, `/undo`
- ✅ **Fase 3 — OCR struk**: foto struk/screenshot e-wallet → LLM Vision → draft transaksi (di bot & web), foto tersimpan & bisa dilihat lagi
- ⏭️ **Fase 4 — Web app (PWA)** (berikutnya)

Kode backend di [backend/](backend/) — 38 test lulus. Lihat [backend/README.md](backend/README.md) untuk cara menjalankan.
