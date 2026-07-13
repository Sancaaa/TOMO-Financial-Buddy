// Palet chart per kategori (earthy/warm, dari docs/DESIGN.md), fallback hashing stabil.
const CATEGORY_COLORS: Record<string, string> = {
  Makan: "#C0392B",
  Jajan: "#D9992E",
  Transport: "#8C6239",
  "Kuota/Pulsa": "#5B8C7B",
  Kos: "#7D5A50",
  Kuliah: "#4C7A34",
  Hiburan: "#9B5C6B",
  Kesehatan: "#D98C7A",
  Lainnya: "#A89A86",
  Kiriman: "#4CAF50",
  Beasiswa: "#6FAF52",
  "Gaji/Freelance": "#2E7D32",
};

const FALLBACK = [
  "#C0392B", "#D9992E", "#8C6239", "#5B8C7B", "#7D5A50",
  "#4C7A34", "#9B5C6B", "#D98C7A", "#A89A86",
];

export function categoryColor(name: string | null | undefined): string {
  if (!name) return "#A89A86";
  if (CATEGORY_COLORS[name]) return CATEGORY_COLORS[name];
  let h = 0;
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return FALLBACK[h % FALLBACK.length];
}
