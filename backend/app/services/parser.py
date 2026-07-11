"""Parser input cepat: ubah teks bebas jadi transaksi.

Contoh yang didukung:
    "makan 15k"              -> expense 15.000, deskripsi "makan"
    "gojek 24rb"            -> expense 24.000
    "kemarin nasi padang 25.000"
    "dapet 50k dari nyokap" -> income 50.000
    "tgl 2 bayar kos 800rb" -> expense 800.000, tanggal 2 bulan ini/lalu
    "kopi 1,5jt"           -> expense 1.500.000
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation


@dataclass
class ParsedInput:
    amount: Decimal
    type: str  # expense | income
    description: str
    occurred_at: datetime


_SUFFIX_MULT = {
    "k": 1_000,
    "rb": 1_000,
    "ribu": 1_000,
    "jt": 1_000_000,
    "juta": 1_000_000,
}

# angka (greedy, diakhiri digit agar '25.000' utuh) + suffix opsional; lookahead
# mencegah "kg" terbaca "k" dan memastikan match berhenti di batas non-alfanumerik.
_TOKEN_RE = re.compile(
    r"(\d[\d.,]*\d|\d)\s*(juta|ribu|jt|rb|k)?(?![a-z\d])", re.IGNORECASE
)

_INCOME_KEYWORDS = [
    "dapet", "dapat", "gaji", "gajian", "transferan", "kiriman", "dikirim",
    "dikirimin", "beasiswa", "bonus", "thr", "cashback", "refund", "honor",
    "fee", "pemasukan", "gajar",
]

_FILLER_PREFIX_RE = re.compile(r"^(beli|bayar|beliin|byr|buat|untuk|utk)\s+", re.IGNORECASE)


def _amount_value(num_raw: str, suffix: str | None) -> Decimal | None:
    num_raw = num_raw.strip().strip(".,")
    if not num_raw:
        return None
    try:
        if suffix:
            # suffix hadir: pemisah adalah desimal (1,5jt / 1.5jt)
            value = Decimal(num_raw.replace(",", ".")) * _SUFFIX_MULT[suffix.lower()]
        else:
            # tanpa suffix: '.' dan ',' adalah pemisah ribuan (15.000 -> 15000)
            value = Decimal(num_raw.replace(".", "").replace(",", ""))
    except (InvalidOperation, ArithmeticError):
        return None
    return value


def _tgl(day: int, now: datetime) -> datetime:
    """Bangun tanggal 'day' pada bulan ini; jika day di masa depan, pakai bulan lalu."""
    try:
        cand = now.replace(day=day)
    except ValueError:
        return now
    if day > now.day:
        prev_last = now.replace(day=1) - timedelta(days=1)
        try:
            cand = prev_last.replace(day=day)
        except ValueError:
            cand = prev_last
    return cand


def _extract_date(low: str, orig: str, now: datetime) -> tuple[datetime, str, str]:
    """Deteksi & buang ekspresi tanggal. Kembalikan (waktu, low, orig) yang tersisa."""
    patterns: list[tuple[re.Pattern, object]] = [
        (re.compile(r"\bkemarin\s+lusa\b"), lambda m: now - timedelta(days=2)),
        (re.compile(r"\b(\d+)\s+hari\s+(?:yang\s+)?lalu\b"),
         lambda m: now - timedelta(days=int(m.group(1)))),
        (re.compile(r"\bkemarin\b"), lambda m: now - timedelta(days=1)),
        (re.compile(r"\b(?:hari\s+ini|tadi|barusan|sekarang)\b"), lambda m: now),
        (re.compile(r"\b(?:tgl|tanggal)\s*(\d{1,2})\b"),
         lambda m: _tgl(int(m.group(1)), now)),
    ]
    for pat, fn in patterns:
        m = pat.search(low)
        if m:
            dt = fn(m)
            s, e = m.span()
            return dt, low[:s] + low[e:], orig[:s] + orig[e:]
    return now, low, orig


def _detect_type(low: str) -> str:
    for kw in _INCOME_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", low):
            return "income"
    return "expense"


def _clean_desc(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip(" -.,")
    s = _FILLER_PREFIX_RE.sub("", s)
    return s.strip()


def parse_quick_input(text: str, now: datetime) -> ParsedInput | None:
    """Kembalikan ParsedInput, atau None jika nominal tidak terbaca."""
    orig = (text or "").strip()
    if not orig:
        return None
    low = orig.lower()
    occurred_at, low, orig = _extract_date(low, orig, now)

    best: tuple[tuple[bool, Decimal], int, int, Decimal] | None = None
    for m in _TOKEN_RE.finditer(low):
        value = _amount_value(m.group(1), m.group(2))
        if value is None or value <= 0:
            continue
        key = (bool(m.group(2)), value)
        if best is None or key > best[0]:
            best = (key, m.start(), m.end(), value)

    if best is None:
        return None
    _, start, end, amount = best
    description = _clean_desc(orig[:start] + orig[end:])
    return ParsedInput(
        amount=amount,
        type=_detect_type(low),
        description=description,
        occurred_at=occurred_at,
    )
