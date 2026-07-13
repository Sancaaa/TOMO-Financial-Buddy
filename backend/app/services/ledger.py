from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Account, Transaction


def apply_balance(db: Session, tx: Transaction, sign: int) -> None:
    """Sesuaikan saldo akun. sign=+1 menerapkan tx, sign=-1 membatalkannya.

    - expense mengurangi saldo, income menambah.
    - transfer: akun sumber berkurang, akun tujuan bertambah.
    """
    if tx.type == "transfer":
        if tx.account_id is not None:
            src = db.get(Account, tx.account_id)
            if src is not None:
                src.balance = src.balance - tx.amount * sign
        if tx.dest_account_id is not None:
            dst = db.get(Account, tx.dest_account_id)
            if dst is not None:
                dst.balance = dst.balance + tx.amount * sign
        return

    if tx.account_id is None:
        return
    account = db.get(Account, tx.account_id)
    if account is None:
        return
    direction = Decimal(1) if tx.type == "income" else Decimal(-1)
    account.balance = account.balance + direction * tx.amount * sign
