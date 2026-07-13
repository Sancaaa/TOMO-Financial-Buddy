from decimal import Decimal

_MONTHS_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def rupiah(value: Decimal | int | float) -> str:
    n = int(Decimal(str(value)))
    return "Rp" + f"{n:,}".replace(",", ".")


def month_label(period: str) -> str:
    year, mon = period.split("-")
    return f"{_MONTHS_ID[int(mon)]} {year}"
