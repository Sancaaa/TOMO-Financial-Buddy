"""Tebak kategori transaksi dari deskripsi, dan belajar dari koreksi user.

Urutan penentuan:
  1. Aturan hasil belajar (tabel keyword_rules) — token dgn total hits tertinggi.
  2. Kata kunci bawaan (_BUILTIN).
  3. Fallback: 'Lainnya' (expense) / kategori income pertama.
"""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, KeywordRule

# nama kategori -> daftar token pemicu
_BUILTIN_EXPENSE: dict[str, list[str]] = {
    "Makan": [
        "makan", "nasi", "ayam", "warteg", "warung", "padang", "mie", "bakso",
        "soto", "sate", "gado", "geprek", "kantin", "sarapan", "lunch", "dinner",
        "gofood", "grabfood", "shopeefood", "seblak", "nasgor", "burger", "pizza",
    ],
    "Jajan": [
        "kopi", "ngopi", "starbucks", "boba", "milktea", "chatime", "snack",
        "cemilan", "jajan", "gorengan", "martabak", "roti", "cireng", "es",
        "minum", "cokelat", "coklat", "donat",
    ],
    "Transport": [
        "gojek", "gocar", "goride", "grab", "grabbike", "grabcar", "angkot",
        "busway", "transjakarta", "mrt", "krl", "bensin", "bbm", "pertalite",
        "pertamax", "parkir", "ojek", "ojol", "tol", "kereta", "tiket", "damri",
    ],
    "Kuota/Pulsa": [
        "kuota", "pulsa", "paket", "data", "internet", "indihome", "telkomsel",
        "axis", "byu", "smartfren", "wifi",
    ],
    "Kos": ["kos", "kost", "kontrakan", "sewa", "listrik", "token", "galon"],
    "Kuliah": [
        "kuliah", "ukt", "spp", "buku", "fotokopi", "fotocopy", "print", "ngeprint",
        "praktikum", "modul", "semester", "atk", "pulpen", "kertas",
    ],
    "Hiburan": [
        "nonton", "bioskop", "film", "netflix", "spotify", "youtube", "game",
        "steam", "langganan", "konser", "wisata", "liburan", "mabar",
    ],
    "Kesehatan": [
        "obat", "apotek", "apotik", "dokter", "klinik", "vitamin", "masker",
        "bpjs", "rumahsakit", "sabun", "skincare",
    ],
}

_BUILTIN_INCOME: dict[str, list[str]] = {
    "Kiriman": [
        "kiriman", "nyokap", "bokap", "ortu", "mama", "papa", "ibu", "ayah",
        "orangtua", "dikirim", "transferan", "uangsaku",
    ],
    "Beasiswa": ["beasiswa", "kip", "bidikmisi", "kipk"],
    "Gaji/Freelance": [
        "gaji", "gajian", "freelance", "proyek", "project", "honor", "fee",
        "magang", "parttime", "part", "ngajar", "les",
    ],
}

_STOPWORDS = {
    "buat", "untuk", "yang", "dari", "dengan", "pada", "beli", "bayar", "tadi",
    "ini", "itu", "dan", "aja", "sama", "juga", "lagi", "udah", "sudah",
}


def _builtin_lookup(ttype: str) -> dict[str, str]:
    """token -> nama kategori, untuk tipe transaksi tertentu."""
    source = _BUILTIN_INCOME if ttype == "income" else _BUILTIN_EXPENSE
    return {token: name for name, tokens in source.items() for token in tokens}


def tokenize(text: str) -> list[str]:
    tokens = re.split(r"[^a-z0-9]+", (text or "").lower())
    return [
        t for t in tokens
        if len(t) >= 3 and not t.isdigit() and t not in _STOPWORDS
    ]


def _category_by_name(db: Session, name: str, ttype: str, user_id: int) -> Category | None:
    return db.scalar(
        select(Category).where(
            Category.user_id == user_id, Category.name == name, Category.type == ttype
        )
    )


def suggest_category(
    db: Session, description: str, ttype: str, user_id: int
) -> Category | None:
    tokens = tokenize(description)

    # 1. aturan hasil belajar (hanya milik user ini)
    if tokens:
        rows = db.execute(
            select(KeywordRule.category_id, KeywordRule.hits)
            .join(Category, Category.id == KeywordRule.category_id)
            .where(
                KeywordRule.user_id == user_id,
                KeywordRule.keyword.in_(tokens),
                Category.type == ttype,
            )
        ).all()
        if rows:
            scores: dict[int, int] = {}
            for category_id, hits in rows:
                scores[category_id] = scores.get(category_id, 0) + hits
            best_id = max(scores, key=scores.get)
            return db.get(Category, best_id)

    # 2. kata kunci bawaan
    builtin = _builtin_lookup(ttype)
    for token in tokens:
        if token in builtin:
            cat = _category_by_name(db, builtin[token], ttype, user_id)
            if cat:
                return cat

    # 3. fallback
    if ttype == "income":
        return _category_by_name(db, "Kiriman", "income", user_id) or db.scalar(
            select(Category)
            .where(Category.user_id == user_id, Category.type == "income")
            .order_by(Category.id)
        )
    return _category_by_name(db, "Lainnya", "expense", user_id) or db.scalar(
        select(Category)
        .where(Category.user_id == user_id, Category.type == "expense")
        .order_by(Category.id)
    )


def learn_from_correction(db: Session, description: str, category: Category) -> None:
    """Petakan token deskripsi ke kategori yang dipilih user, naikkan hits.

    `category` sudah milik user tertentu → rule mewarisi `category.user_id`.
    """
    for token in set(tokenize(description)):
        rule = db.scalar(
            select(KeywordRule).where(
                KeywordRule.user_id == category.user_id,
                KeywordRule.keyword == token,
                KeywordRule.category_id == category.id,
            )
        )
        if rule is None:
            db.add(
                KeywordRule(
                    user_id=category.user_id,
                    keyword=token,
                    category_id=category.id,
                    hits=1,
                )
            )
        else:
            rule.hits += 1
    db.commit()
