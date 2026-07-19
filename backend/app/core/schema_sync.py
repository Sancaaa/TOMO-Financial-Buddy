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
    "ALTER TABLE saving_goals "
    "ADD COLUMN IF NOT EXISTS account_id INTEGER "
    "REFERENCES accounts(id) ON DELETE SET NULL",
    "ALTER TABLE accounts "
    "ADD COLUMN IF NOT EXISTS opening_balance NUMERIC(14, 2)",
    # --- multi-user: role admin ---
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE",
    # owner lama (user id terkecil) dijadikan admin
    "UPDATE users SET is_admin = TRUE WHERE id = (SELECT MIN(id) FROM users)",
    # satu chat Telegram hanya boleh terikat ke satu user (NULL boleh banyak)
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_telegram_chat_id "
    "ON users (telegram_chat_id) WHERE telegram_chat_id IS NOT NULL",
]

# --- multi-user: user_id di semua tabel data ---
# Tabel data yang harus di-scope per user. Untuk tiap tabel: tambah kolom
# (nullable), backfill semua baris lama ke admin (user id terkecil), lalu kunci
# NOT NULL. `ensure_schema` jalan SEBELUM seed, jadi di DB kosong subquery MIN
# aman (tak ada baris untuk di-backfill) dan seed mengisi admin setelahnya.
_USER_SCOPED_TABLES = [
    "accounts", "categories", "transactions", "budgets", "budget_alerts",
    "saving_goals", "keyword_rules", "recurring_txs", "receipts",
]

for _t in _USER_SCOPED_TABLES:
    _STATEMENTS += [
        f"ALTER TABLE {_t} ADD COLUMN IF NOT EXISTS user_id INTEGER "
        f"REFERENCES users(id) ON DELETE CASCADE",
        f"UPDATE {_t} SET user_id = (SELECT MIN(id) FROM users) WHERE user_id IS NULL",
        f"CREATE INDEX IF NOT EXISTS ix_{_t}_user_id ON {_t} (user_id)",
    ]

# Kunci NOT NULL setelah backfill (dipisah: hanya aman bila tak ada baris NULL
# tersisa; di DB kosong pun aman karena tak ada baris).
_NOT_NULL_STATEMENTS = [
    f"ALTER TABLE {_t} ALTER COLUMN user_id SET NOT NULL"
    for _t in _USER_SCOPED_TABLES
]


def ensure_schema(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        for stmt in _STATEMENTS:
            conn.execute(text(stmt))
        # SET NOT NULL bisa gagal bila ada user_id yatim (mis. data korup);
        # jangan gagalkan seluruh startup — coba satu per satu.
        for stmt in _NOT_NULL_STATEMENTS:
            try:
                with engine.begin() as conn2:
                    conn2.execute(text(stmt))
            except Exception:
                pass
