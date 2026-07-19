from decimal import Decimal

from sqlalchemy import case, func, select
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


def transaction_effects(db: Session, user_id: int) -> dict[int, Decimal]:
    """Net efek semua transaksi milik `user_id` per account_id.

    income = +amount · expense = -amount · transfer keluar (account_id) = -amount ·
    transfer masuk (dest_account_id) = +amount.
    """
    effects: dict[int, Decimal] = {}

    # income (+) / expense & transfer-keluar (-) → berdasarkan account_id
    rows = db.execute(
        select(
            Transaction.account_id,
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.type == "income", Transaction.amount),
                        else_=-Transaction.amount,
                    )
                ),
                0,
            ),
        )
        .where(Transaction.user_id == user_id, Transaction.account_id.is_not(None))
        .group_by(Transaction.account_id)
    ).all()
    for acc_id, net in rows:
        effects[acc_id] = effects.get(acc_id, Decimal(0)) + Decimal(net)

    # transfer-masuk (+) → berdasarkan dest_account_id
    rows2 = db.execute(
        select(Transaction.dest_account_id, func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == user_id,
            Transaction.type == "transfer",
            Transaction.dest_account_id.is_not(None),
        )
        .group_by(Transaction.dest_account_id)
    ).all()
    for acc_id, net in rows2:
        effects[acc_id] = effects.get(acc_id, Decimal(0)) + Decimal(net)

    return effects


def reconcile_balances(db: Session, user_id: int) -> list[dict]:
    """Hitung ulang saldo tiap akun = opening_balance + Σ efek transaksi.

    Akun tanpa opening_balance di-baseline dari kondisi sekarang (dianggap benar),
    jadi run pertama tak mengubah apa pun tapi menetapkan titik acuan. Run
    berikutnya mengoreksi drift (transaksi yang masuk tanpa lewat apply_balance).
    Kembalikan daftar akun yang saldonya dikoreksi.
    """
    effects = transaction_effects(db, user_id)
    corrections: list[dict] = []
    for acc in db.scalars(select(Account).where(Account.user_id == user_id)).all():
        eff = effects.get(acc.id, Decimal(0))
        if acc.opening_balance is None:
            acc.opening_balance = acc.balance - eff  # baseline dari kondisi sekarang
        expected = acc.opening_balance + eff
        if expected != acc.balance:
            corrections.append(
                {"id": acc.id, "name": acc.name, "before": acc.balance, "after": expected}
            )
            acc.balance = expected
    db.commit()
    return corrections
