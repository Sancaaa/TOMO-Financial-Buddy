import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

declare const process: { env: Record<string, string | undefined> };

// Dev: proxy prefix API ke backend (bind di 127.0.0.1:8737 lewat docker, atau uvicorn).
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8737";
const apiPrefixes = [
  "/auth",
  "/transactions",
  "/categories",
  "/accounts",
  "/receipts",
  "/analytics",
  "/health",
];

export default defineConfig({
  server: {
    proxy: Object.fromEntries(
      apiPrefixes.map((p) => [p, { target: apiTarget, changeOrigin: true }]),
    ),
  },
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["tomo.svg"],
      manifest: {
        name: "TOMO — teman catat keuangan",
        short_name: "TOMO",
        description: "Finance tracker pribadi: quick-add, OCR struk, analitik.",
        theme_color: "#E4483A",
        background_color: "#FBF7F0",
        display: "standalone",
        start_url: "/",
        lang: "id",
        icons: [
          {
            src: "tomo.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any maskable",
          },
        ],
      },
    }),
  ],
});
