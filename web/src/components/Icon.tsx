import type { ReactNode } from "react";

/**
 * Satu sumber ikon garis (stroke) bergaya konsisten — pengganti semua emoji.
 * Mewarisi warna lewat `currentColor`, jadi cukup set `color`/`fill` di induk.
 * Nama kategori (bowl, coffee, …) sengaja cocok dengan `Category.icon` dari backend.
 */
export type IconName =
  // nav
  | "home" | "list" | "plus" | "chart" | "settings" | "menu" | "logout"
  // kategori pengeluaran
  | "bowl" | "coffee" | "car" | "wifi" | "school" | "device-tv" | "heartbeat" | "dots"
  // kategori pemasukan
  | "wallet" | "award" | "briefcase"
  // aksi / status
  | "camera" | "check" | "target" | "trophy" | "close" | "trash"
  | "arrow-up" | "arrow-down" | "swap" | "refresh" | "tag" | "spark" | "alert";

const P: Record<IconName, ReactNode> = {
  home: <><path d="M4 11.5 12 4l8 7.5" /><path d="M6 10v9h12v-9" /></>,
  list: <><path d="M8 6h12M8 12h12M8 18h12" /><path d="M4 6h.01M4 12h.01M4 18h.01" /></>,
  plus: <path d="M12 5v14M5 12h14" />,
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  logout: <><path d="M14 7V5a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-2" /><path d="M10 12h10M17 9l3 3-3 3" /></>,
  chart: <><path d="M4 20h16" /><path d="M7 20v-6M12 20V5M17 20v-9" /></>,
  settings: (
    <>
      <path d="M4 8h16M4 16h16" />
      <circle cx="9" cy="8" r="2.3" fill="var(--paper)" />
      <circle cx="15" cy="16" r="2.3" fill="var(--paper)" />
    </>
  ),
  bowl: <><path d="M3.5 11h17a8.5 8.5 0 0 1-17 0Z" /><path d="M9 4.2c-.6 1 .3 1.6 0 2.8M13 3.6c-.6 1 .3 1.6 0 2.8" /></>,
  coffee: <><path d="M4 8h13v4.5A4.5 4.5 0 0 1 12.5 17h-4A4.5 4.5 0 0 1 4 12.5Z" /><path d="M17 9h1.6a2.4 2.4 0 0 1 0 4.8H17" /><path d="M8 3.5v1.8M12 3.5v1.8" /></>,
  car: <><path d="M5 14l1.3-4.2A2 2 0 0 1 8.2 8.4h7.6a2 2 0 0 1 1.9 1.4L19 14v3.2h-2.2M7.2 17.2H5V14h14" /><circle cx="8" cy="17.2" r="1.5" /><circle cx="16" cy="17.2" r="1.5" /></>,
  wifi: <><path d="M4.5 9.5a11 11 0 0 1 15 0" /><path d="M7.5 12.8a6.5 6.5 0 0 1 9 0" /><path d="M12 16.2h.01" /></>,
  school: <><path d="M12 5 21 9l-9 4-9-4 9-4Z" /><path d="M6.5 10.6V15c0 1.1 2.5 2.4 5.5 2.4s5.5-1.3 5.5-2.4v-4.4" /></>,
  "device-tv": <><rect x="3" y="5.5" width="18" height="11.5" rx="2" /><path d="M8.5 20.5h7M12 17v3.5" /></>,
  heartbeat: <><path d="M20.4 9.4c0 3.4-4 6.3-8.4 9.8-4.4-3.5-8.4-6.4-8.4-9.8A4.4 4.4 0 0 1 12 7a4.4 4.4 0 0 1 8.4 2.4Z" /><path d="M7.5 11.3h2l1-1.6 1.4 3 1-1.4H16" /></>,
  dots: <><circle cx="6" cy="12" r="1.5" fill="currentColor" stroke="none" /><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" /><circle cx="18" cy="12" r="1.5" fill="currentColor" stroke="none" /></>,
  wallet: <><rect x="3.5" y="6.5" width="17" height="13" rx="2.5" /><path d="M3.5 9.5h14a1 1 0 0 1 1 1v0" /><path d="M20.5 12.5H16a1.6 1.6 0 0 0 0 3.2h4.5" /></>,
  award: <><circle cx="12" cy="9" r="5" /><path d="M8.8 13.2 7.5 20.5l4.5-2.2 4.5 2.2-1.3-7.3" /></>,
  briefcase: <><rect x="3" y="8" width="18" height="11" rx="2" /><path d="M9 8V6.2A2.2 2.2 0 0 1 11.2 4h1.6A2.2 2.2 0 0 1 15 6.2V8" /><path d="M3 13h18" /></>,
  camera: <><path d="M4 8.5h3L8.3 6.4h7.4L17 8.5h3a1 1 0 0 1 1 1v8.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5a1 1 0 0 1 1-1Z" /><circle cx="12" cy="13.2" r="3.1" /></>,
  check: <path d="M5 12.5 10 17.5 19 6.5" />,
  target: <><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="3.8" /><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" /></>,
  trophy: <><path d="M8 4h8v4.5a4 4 0 0 1-8 0Z" /><path d="M8 5.2H5v1.2a3 3 0 0 0 3 3M16 5.2h3v1.2a3 3 0 0 1-3 3" /><path d="M12 12.5v3M9.2 19h5.6M10 19c0-1.6.6-2.2 2-2.2s2 .6 2 2.2" /></>,
  close: <path d="M6.5 6.5l11 11M17.5 6.5l-11 11" />,
  trash: <><path d="M4.5 7h15M10 7V4.8h4V7M6.5 7l1 12.5h9L17.5 7" /></>,
  alert: <><path d="M12 4.5 21 19H3l9-14.5Z" /><path d="M12 10v4.2" /><path d="M12 16.6h.01" /></>,
  "arrow-up": <path d="M12 19V5M6.5 10.5 12 5l5.5 5.5" />,
  "arrow-down": <path d="M12 5v14M6.5 13.5 12 19l5.5-5.5" />,
  swap: <><path d="M6 8h13l-3-3M18 16H5l3 3" /></>,
  refresh: <><path d="M20 11a8 8 0 0 0-13.7-5.2L4 8M4 4v4h4" /><path d="M4 13a8 8 0 0 0 13.7 5.2L20 16M20 20v-4h-4" /></>,
  tag: <><path d="M4 12.5V5.5A1.5 1.5 0 0 1 5.5 4h7l7.5 7.5-8 8L4 12.5Z" /><circle cx="8.2" cy="8.2" r="1.3" fill="currentColor" stroke="none" /></>,
  spark: <path d="M12 3.5c.6 4.4 1.6 5.4 6 6-4.4.6-5.4 1.6-6 6-.6-4.4-1.6-5.4-6-6 4.4-.6 5.4-1.6 6-6Z" />,
};

export function Icon({
  name,
  size = 22,
  stroke = 1.8,
  className,
  fill = false,
}: {
  name: IconName;
  size?: number;
  stroke?: number;
  className?: string;
  /** true untuk ikon berbentuk isian (mis. badge penuh) */
  fill?: boolean;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={stroke}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      style={fill ? { fill: "currentColor", stroke: "none" } : undefined}
    >
      {P[name]}
    </svg>
  );
}

/** Peta nama kategori → ikon, dipakai saat `Category.icon` kosong/tak dikenal. */
const CATEGORY_ICON: Record<string, IconName> = {
  bowl: "bowl", coffee: "coffee", car: "car", wifi: "wifi", home: "home",
  school: "school", "device-tv": "device-tv", heartbeat: "heartbeat", dots: "dots",
  wallet: "wallet", award: "award", briefcase: "briefcase",
};

const NAME_ICON: Record<string, IconName> = {
  Makan: "bowl", Jajan: "coffee", Transport: "car", "Kuota/Pulsa": "wifi",
  Kos: "home", Kuliah: "school", Hiburan: "device-tv", Kesehatan: "heartbeat",
  Lainnya: "dots", Kiriman: "wallet", Beasiswa: "award", "Gaji/Freelance": "briefcase",
};

export function categoryIcon(
  icon: string | null | undefined,
  name?: string | null,
): IconName {
  if (icon && CATEGORY_ICON[icon]) return CATEGORY_ICON[icon];
  if (name && NAME_ICON[name]) return NAME_ICON[name];
  return "tag";
}
