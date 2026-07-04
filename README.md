# Finance Tracker Pribadi

Sistem pencatatan keuangan pribadi yang dirancang agar **mencatat lebih cepat daripada malas**.
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

## Tech Stack (ringkas)

FastAPI · PostgreSQL · React PWA · python-telegram-bot · LLM Vision (OCR) · Docker Compose · Caddy

## Status

📋 Tahap desain — implementasi dimulai dari Fase 1 (lihat roadmap di dokumen arsitektur).
