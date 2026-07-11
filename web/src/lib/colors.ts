// Palet chart per kategori (dari docs/DESIGN.md), fallback hashing yang stabil.
const CATEGORY_COLORS: Record<string, string> = {
  Makan: "#E4483A",
  Jajan: "#E8A93B",
  Transport: "#3E72A6",
  "Kuota/Pulsa": "#4F9D9A",
  Kos: "#A9743B",
  Kuliah: "#5E9A46",
  Hiburan: "#9B5DA6",
  Kesehatan: "#E27A8A",
  Lainnya: "#9A8F7E",
  Kiriman: "#5E9A46",
  Beasiswa: "#7BB662",
  "Gaji/Freelance": "#3E6B2C",
};

const FALLBACK = [
  "#E4483A", "#E8A93B", "#3E72A6", "#4F9D9A", "#A9743B",
  "#5E9A46", "#9B5DA6", "#E27A8A", "#9A8F7E",
];

export function categoryColor(name: string | null | undefined): string {
  if (!name) return "#9A8F7E";
  if (CATEGORY_COLORS[name]) return CATEGORY_COLORS[name];
  let h = 0;
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return FALLBACK[h % FALLBACK.length];
}
