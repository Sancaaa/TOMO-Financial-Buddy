from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Account, Transaction


def apply_balance(db: Session, tx: Transaction, sign: int) -> None:
    """Sesuaikan saldo akun. sign=+1 menerapkan tx, sign=-1 membatalkannya.

    expense mengurangi saldo, income menambah. transfer tidak diproses di sini
    (double-entry transfer menyusul di fase berikutnya).
    """
    if tx.account_id is None or tx.type == "transfer":
        return
    account = db.get(Account, tx.account_id)
    if account is None:
        return
    direction = Decimal(1) if tx.type == "income" else Decimal(-1)
    account.balance = account.balance + direction * tx.amount * sign
