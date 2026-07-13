"""Penyesuaian skema ringan untuk kolom baru pada tabel yang sudah ada.

`create_all` membuat tabel baru (mis. receipts) otomatis, tapi tidak menambah
kolom ke tabel lama. Sampai Alembic diperkenalkan, fungsi ini menjembatani lewat
ADD COLUMN IF NOT EXISTS (Postgres). Idempoten dan aman diulang; tidak berjalan
di SQLite (skema test dibangun ulang penuh dari model).
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

_STATEMENTS = [
    "ALTER TABLE transactions "
    "ADD COLUMN IF NOT EXISTS receipt_id INTEGER "
    "REFERENCES receipts(id) ON DELETE SET NULL",
    "ALTER TABLE transactions "
    "ADD COLUMN IF NOT EXISTS dest_account_id INTEGER "
    "REFERENCES accounts(id) ON DELETE SET NULL",
    "ALTER TABLE categories "
    "ADD COLUMN IF NOT EXISTS budget_rollover BOOLEAN DEFAULT FALSE",
]


def ensure_schema(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        for stmt in _STATEMENTS:
            conn.execute(text(stmt))
