# Web — TOMO PWA (Fase 4)

React + Vite + TypeScript. Progressive Web App, mobile-first, mengikuti design system
di [../docs/DESIGN.md](../docs/DESIGN.md). Disajikan langsung oleh FastAPI di produksi
(satu origin), jadi tidak butuh server web terpisah.

## Halaman

- **Beranda** — quick-add, ringkasan bulan berjalan, donut kategori, transaksi terbaru
- **Riwayat** — filter (bulan, kategori, cari) + edit/hapus, muat lebih
- **Tambah** — 3 mode: Cepat (`makan 15k`), Form lengkap, Struk 📸 (upload → OCR → konfirmasi)
- **Analitik** — donut per kategori, tren 6 bulan, perbandingan vs bulan lalu
- **Kelola** — CRUD kategori (+ budget) dan akun

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
