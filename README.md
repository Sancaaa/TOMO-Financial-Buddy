# TOMO 🍅

**TOMO** (友, "teman") adalah finance tracker pribadi yang dirancang agar **mencatat lebih
cepat daripada malas** — pencatat keuangan yang terasa seperti teman, dengan maskot si tomat.
Satu backend, tiga pintu masuk: Telegram bot, web app (PWA), dan Android.

## Fitur Utama

- ⚡ **Quick-add**: ketik `makan 15k` di Telegram/web → tercatat lengkap dengan kategori otomatis
- 📸 **OCR struk**: foto struk / screenshot e-wallet → transaksi draft tinggal dikonfirmasi
- 📊 **Analitik**: dashboard donut kategori, tren bulanan, perbandingan
- 💰 **Budgeting**: budget per kategori + total, safe-to-spend harian, alert 80%/100%, proyeksi tanggal habis
- 🔁 **Otomasi**: transaksi berulang (kos, langganan), daily digest, review akhir bulan, export CSV

## Dokumentasi

- [Arsitektur Sistem](docs/ARCHITECTURE.md) — komponen, tech stack, skema DB, API, deployment
- [Requirement & Fitur](docs/REQUIREMENTS.md) — functional/non-functional requirements, prioritas, acceptance criteria
- [Design System](docs/DESIGN.md) — identitas visual, palet warna, tipografi, maskot, komponen UI

## Tech Stack (ringkas)

FastAPI · PostgreSQL · React + Vite PWA · Telegram Bot API (webhook) · Gemini Vision (OCR) · Docker Compose · Cloudflare Tunnel

## Status

- ✅ **Fase 1 — Fondasi**: API (auth JWT, CRUD transaksi/kategori/akun), Docker + Caddy
- ✅ **Fase 2 — Telegram bot**: quick-add parser, auto-kategori yang belajar dari koreksi, tombol inline, ringkasan `/hariini` `/minggu` `/bulan`, `/undo`
- ✅ **Fase 3 — OCR struk**: foto struk/screenshot e-wallet → LLM Vision → draft transaksi (di bot & web), foto tersimpan & bisa dilihat lagi
- ✅ **Fase 4 — Web app (PWA)**: dashboard, riwayat + filter, tambah (cepat/form/OCR), analitik (donut + tren), kelola kategori & akun, installable. Disajikan langsung oleh FastAPI (satu origin), akses publik via Cloudflare Tunnel
- ✅ **Fase 4.5 — UI revamp + desktop**: identitas editorial hangat (Playfair + DM Sans, grain, tomat gambar-tangan, palet warm-only), layout desktop (sidebar + multi-kolom) selain mobile
- ✅ **Fase 5 — Budgeting & otomasi**: budget per kategori + total, safe-to-spend, progress bar berwarna, `/budget` di bot, scheduler (recurring tx, digest harian, alert 80%/100%, review bulanan), export CSV
- ✅ **Fase 6 — Ekstra**: transfer antar akun, saving goals (target nabung), rollover budget
- ⏭️ **Sisa opsional**: siklus budget non-kalender, import CSV mutasi bank, split bill

Kode di [backend/](backend/) (60 test lulus) dan [web/](web/). Lihat [backend/README.md](backend/README.md) dan [web/README.md](web/README.md) untuk cara menjalankan.
