# Web — TOMO PWA (Fase 4)

React + Vite + TypeScript. Progressive Web App, mobile-first, mengikuti design system
di [../docs/DESIGN.md](../docs/DESIGN.md). Disajikan langsung oleh FastAPI di produksi
(satu origin), jadi tidak butuh server web terpisah.

## Halaman

- **Beranda** — quick-add, safe-to-spend + progress budget total, ringkasan bulan, donut kategori, transaksi terbaru, progress target nabung
- **Riwayat** — filter (bulan, kategori, cari) + edit/hapus, export CSV, muat lebih
- **Tambah** — 4 mode: Cepat (`makan 15k`), Form lengkap, Struk 📸 (OCR), **Transfer** antar akun
- **Analitik** — donut per kategori, budget per kategori (progress bar), tren 6 bulan, perbandingan
- **Kelola** — CRUD kategori (+ budget + rollover), akun, budget total bulanan, transaksi berulang, target nabung

## Dev

```bash
cd web
npm install
npm run dev        # http://localhost:5173, proxy API ke VITE_API_TARGET (default 127.0.0.1:8737)
```

Jalankan backend terpisah (mis. `uvicorn app.main:app --port 8737` atau `docker compose up`).
Set `VITE_API_TARGET` bila backend di port lain.

## Build

```bash
npm run build      # → web/dist
npm run typecheck  # cek TypeScript
```

Di produksi, `dist/` di-build oleh Dockerfile multi-stage dan disalin ke `/app/web`;
FastAPI menyajikannya lewat `STATIC_DIR` dengan fallback SPA ke `index.html`.

## Catatan

- Auth: token JWT disimpan di `localStorage`; request menyertakan `Authorization: Bearer`.
  Response 401 otomatis menghapus token → kembali ke layar login.
- Chart (donut & bar tren) digambar tangan pakai SVG + token warna TOMO — tanpa library chart.
- PWA (manifest + service worker) via `vite-plugin-pwa`. Ikon: `public/tomo.svg` (maskable).
- API dipanggil dengan path relatif (`/transactions`, dll.) → aman satu origin dengan backend.
