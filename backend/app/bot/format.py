import html
from datetime import datetime
from decimal import Decimal

from app.services.summary import PeriodSummary

_MONTHS_ID = [
    "", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
]


def format_rupiah(value: Decimal | int) -> str:
    n = int(Decimal(value))
    return "Rp" + f"{n:,}".replace(",", ".")


def esc(text: str | None) -> str:
    return html.escape(text or "")


def _tanggal_id(dt: datetime) -> str:
    return f"{dt.day} {_MONTHS_ID[dt.month]} {dt.year}"


def tx_confirmation(
    *,
    amount: Decimal,
    ttype: str,
    description: str,
    category_name: str | None,
    occurred_at: datetime,
    now: datetime,
) -> str:
    kind = category_name or ("Pemasukan" if ttype == "income" else "Lainnya")
    head = "➕" if ttype == "income" else "🧾"
    desc = f" · {esc(description)}" if description else ""
    line = f"{head} <b>{format_rupiah(amount)}</b> — {esc(kind)}{desc}"
    if occurred_at.date() != now.date():
        line += f"\n🗓 {_tanggal_id(occurred_at)}"
    return "✅ Tercatat\n" + line


def confirm_keyboard(tx_id: int) -> dict:
    return {
        "inline_keyboard": [[
            {"text": "✏️ Kategori", "callback_data": f"pc:{tx_id}"},
            {"text": "🗑 Hapus", "callback_data": f"del:{tx_id}"},
        ]]
    }


def category_keyboard(tx_id: int, categories) -> dict:
    buttons = [
        {"text": c.name, "callback_data": f"sc:{tx_id}:{c.id}"} for c in categories
    ]
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    return {"inline_keyboard": rows}


def summary_text(title: str, s: PeriodSummary) -> str:
    lines = [f"📊 <b>{esc(title)}</b>"]
    lines.append(f"Pengeluaran: <b>{format_rupiah(s.total_expense)}</b>")
    if s.total_income > 0:
        lines.append(f"Pemasukan: {format_rupiah(s.total_income)}")
    if s.per_category:
        lines.append("")
        for ct in s.per_category[:6]:
            lines.append(f"• {esc(ct.name)}: {format_rupiah(ct.total)}")
    if s.count == 0:
        lines.append("Belum ada transaksi di periode ini.")
    return "\n".join(lines)


HELP_TEXT = (
    "🍅 <b>TOMO</b> — teman catat keuanganmu\n"
    "Catat pengeluaran cukup dengan mengetik, misalnya:\n"
    "• <code>makan 15k</code>\n"
    "• <code>gojek 24rb</code>\n"
    "• <code>kemarin nasi padang 25.000</code>\n"
    "• <code>dapet 50k dari nyokap</code>\n"
    "Atau <b>kirim foto struk</b> — Tomo baca sendiri 📸\n\n"
    "Perintah:\n"
    "/hariini · /minggu · /bulan — ringkasan\n"
    "/undo — hapus catatan terakhir\n"
    "/help — bantuan ini"
)
