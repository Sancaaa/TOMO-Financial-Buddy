export function rupiah(value: number | string | null | undefined): string {
  const n = Math.round(Number(value ?? 0));
  return "Rp" + n.toLocaleString("id-ID");
}

export function rupiahShort(value: number | string): string {
  const n = Math.round(Number(value));
  if (n >= 1_000_000) return "Rp" + (n / 1_000_000).toFixed(n % 1_000_000 ? 1 : 0).replace(".", ",") + "jt";
  if (n >= 1_000) return "Rp" + Math.round(n / 1000) + "rb";
  return "Rp" + n;
}

const MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];

export function monthShort(ym: string): string {
  const [, m] = ym.split("-");
  return MONTHS[Number(m)] ?? ym;
}

export function monthLong(ym: string): string {
  const [y, m] = ym.split("-");
  return `${MONTHS[Number(m)]} ${y}`;
}

export function dateLabel(iso: string): string {
  const d = new Date(iso);
  return `${d.getDate()} ${MONTHS[d.getMonth() + 1]}`;
}

export function currentMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function todayInput(): string {
  const d = new Date();
  const off = d.getTimezoneOffset();
  return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10);
}
