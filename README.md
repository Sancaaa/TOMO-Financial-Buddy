# 🍅 TOMO — Financial Buddy

> Pencatat keuangan yang terasa seperti teman.
> Ketik `makan 15k` → tercatat. Sesimpel itu.

**TOMO** (友, "teman") adalah personal finance tracker yang dibangun supaya **mencatat lebih cepat daripada malas**. Satu backend, tiga pintu masuk: **Telegram Bot**, **Web App (PWA)**, dan **Android**.

🌐 **Live**: [tomo.sanca.site](https://tomo.sanca.site)

---

## ✨ Fitur

| | Fitur | Detail |
|---|---|---|
| ⚡ | **Quick-add** | `makan 15k` → otomatis masuk kategori yang benar |
| 📸 | **OCR Struk** | Foto struk / screenshot e-wallet → transaksi draft |
| 📊 | **Analitik** | Dashboard donut, tren bulanan, perbandingan |
| 💰 | **Budgeting** | Budget per kategori, safe-to-spend harian, alert otomatis |
| 🔁 | **Otomasi** | Recurring transaction, daily digest, review bulanan |
| 🎯 | **Saving Goals** | Target nabung dengan tracking progress |
| 💸 | **Transfer** | Transfer antar akun + rollover budget |
| 📥 | **Export** | Download data CSV kapan saja |

---

## 🛠️ Tech Stack

```
Frontend     React · TypeScript · Vite PWA
Backend      FastAPI · PostgreSQL
AI/OCR       Gemini Vision API
Bot          Telegram Bot API (webhook)
Infra        Docker Compose · Cloudflare Tunnel
Mobile       Android WebView wrapper
```

---

## 📂 Struktur

```
├── backend/       # FastAPI server + Telegram bot
├── web/           # React PWA (Vite)
├── android/       # Android WebView wrapper
└── docs/          # Arsitektur, requirements, design system
```

---

## 🚀 Quick Start

```bash
# Clone & setup environment
cp .env.example .env
# Edit .env sesuai kebutuhan

# Jalankan dengan Docker
docker compose up -d
```

Selengkapnya: [backend/README.md](backend/README.md) · [web/README.md](web/README.md)

---

## 📄 Dokumentasi

- [Arsitektur Sistem](docs/ARCHITECTURE.md)
- [Requirements & Fitur](docs/REQUIREMENTS.md)
- [Design System](docs/DESIGN.md)

---

<p align="center">
  <sub>dibuat dengan ☕ dan banyak 🍅</sub>
</p>
