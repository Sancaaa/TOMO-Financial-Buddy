// Logika keputusan gesture swipe (murni, tanpa DOM) — dipisah agar bisa diuji.

export type Intent = "pending" | "vertical" | "horizontal";

/** Tentukan niat geseran dari delta pointer. `pending` = arah belum jelas. */
export function detectIntent(dxRaw: number, dyRaw: number, threshold = 8): Intent {
  if (Math.abs(dxRaw) < threshold && Math.abs(dyRaw) < threshold) return "pending";
  return Math.abs(dyRaw) > Math.abs(dxRaw) ? "vertical" : "horizontal";
}

/** Offset baris saat digeser, dibatasi [-width, 0] (hanya ke kiri). */
export function clampOffset(base: number, dxRaw: number, width: number): number {
  return Math.max(-width, Math.min(0, base + dxRaw));
}

/** Snap saat dilepas: terbuka penuh bila lewat separuh, else tertutup. */
export function resolveOffset(dx: number, width: number): number {
  return dx < -width / 2 ? -width : 0;
}

/** Aksi saat baris di-tap: abaikan bila baru saja digeser, tutup bila terbuka, else pilih. */
export function tapAction(moved: boolean, isOpen: boolean): "noop" | "close" | "select" {
  if (moved) return "noop";
  if (isOpen) return "close";
  return "select";
}
