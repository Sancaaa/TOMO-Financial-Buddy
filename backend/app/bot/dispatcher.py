"""Logika bot Telegram, terpisah dari transport agar mudah dites.

`handle_update` menerima dict update mentah dari Telegram, sebuah objek Session,
dan sebuah klien (punya send_message / edit_message_text / answer_callback_query).
Klien di-inject supaya test bisa memakai fake tanpa jaringan.
"""

import re
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.bot import format as fmt
from app.core.clock import LOCAL_TZ, now_local
from app.models import Account, Category, Transaction
from app.services.budget import overview, set_budget
from app.services.categorizer import learn_from_correction, suggest_category
from app.services.ledger import apply_balance
from app.services.money import month_label, rupiah
from app.services.parser import parse_amount, parse_quick_input
from app.services.receipts import build_draft, process_receipt
from app.services.summary import period_summary


def handle_update(update: dict, db: Session, tg, allowed_chat_id: str | None) -> None:
    if "callback_query" in update:
        _handle_callback(update["callback_query"], db, tg, allowed_chat_id)
        return

    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]

    if not _authorized(chat_id, allowed_chat_id):
        tg.send_message(
            chat_id,
            "Kamu belum terdaftar untuk memakai bot ini.\n"
            f"chat_id kamu: <code>{chat_id}</code>\n"
            "Set TELEGRAM_CHAT_ID ke nilai itu lalu restart bot.",
        )
        return

    if "photo" in msg:
        _handle_photo(msg, chat_id, db, tg)
        return
    if "document" in msg:
        tg.send_message(
            chat_id,
            "Kirim struk sebagai <b>foto</b> ya (bukan file), biar bisa dibaca OCR.",
        )
        return

    text = (msg.get("text") or "").strip()
    if not text:
        return
    if text.startswith("/"):
        _handle_command(text, chat_id, db, tg)
    else:
        _handle_quick_add(text, chat_id, db, tg)


def _authorized(chat_id, allowed_chat_id: str | None) -> bool:
    return bool(allowed_chat_id) and str(chat_id) == str(allowed_chat_id)


def _default_account(db: Session) -> Account | None:
    return db.scalars(select(Account).order_by(Account.id)).first()


def _handle_quick_add(text: str, chat_id, db: Session, tg) -> None:
    now = now_local()
    parsed = parse_quick_input(text, now)
    if parsed is None:
        tg.send_message(
            chat_id,
            "Nominal tidak terbaca 🤔 Coba: <code>makan 15k</code> / "
            "<code>gojek 24rb</code> / <code>dapet 50k</code>",
        )
        return

    category = suggest_category(db, parsed.description, parsed.type)
    account = _default_account(db)
    tx = Transaction(
        amount=parsed.amount,
        type=parsed.type,
        category_id=category.id if category else None,
        account_id=account.id if account else None,
        description=parsed.description or None,
        occurred_at=parsed.occurred_at,
        source="telegram",
        raw_input=text,
    )
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)

    body = fmt.tx_confirmation(
        amount=tx.amount,
        ttype=tx.type,
        description=tx.description or "",
        category_name=category.name if category else None,
        occurred_at=tx.occurred_at.astimezone(LOCAL_TZ),
        now=now,
    )
    if tx.type == "expense":
        ov = overview(db)
        if ov.safe_to_spend is not None and ov.days_left > 0:
            body += f"\n💡 Aman jajan {rupiah(ov.safe_to_spend)}/hari sampai akhir bulan"
    tg.send_message(chat_id, body, reply_markup=fmt.confirm_keyboard(tx.id))


def _find_expense_category(db: Session, name: str) -> Category | None:
    name = name.strip().lower()
    cats = db.scalars(select(Category).where(Category.type == "expense")).all()
    for c in cats:
        if c.name.lower() == name:
            return c
    for c in cats:
        if name and (name in c.name.lower() or c.name.lower() in name):
            return c
    return None


def _budget_text(db: Session) -> str:
    ov = overview(db)
    emoji = {"ok": "🟢", "warn": "🟡", "over": "🔴"}
    lines = [f"📊 <b>Budget {month_label(ov.period)}</b>"]
    if ov.total_budget is not None:
        pct = int(ov.total_spent / ov.total_budget * 100) if ov.total_budget else 0
        lines.append(f"Total: {rupiah(ov.total_spent)} / {rupiah(ov.total_budget)} ({pct}%)")
        if ov.safe_to_spend is not None and ov.days_left > 0:
            lines.append(f"Aman jajan <b>{rupiah(ov.safe_to_spend)}</b>/hari ({ov.days_left} hari lagi)")
    budgeted = [c for c in ov.categories if c.budget > 0]
    if budgeted:
        lines.append("")
        for c in budgeted:
            lines.append(f"{emoji.get(c.status, '🟢')} {c.name}: {rupiah(c.spent)}/{rupiah(c.budget)} ({c.pct}%)")
    if ov.total_budget is None and not budgeted:
        lines.append("Belum ada budget. Set: <code>/budget makan 900rb</code> atau <code>/budget total 2jt</code>")
    return "\n".join(lines)


def _handle_budget(arg: str, chat_id, db: Session, tg) -> None:
    arg = arg.strip()
    if not arg:
        tg.send_message(chat_id, _budget_text(db))
        return
    amount = parse_amount(arg)
    if amount is None:
        tg.send_message(chat_id, "Format: <code>/budget makan 900rb</code> atau <code>/budget total 2jt</code>")
        return
    name = re.sub(r"\d[\d.,]*\s*(juta|ribu|jt|rb|k)?", "", arg, flags=re.IGNORECASE).strip()
    if name.lower() in ("total", "semua", ""):
        set_budget(db, None, amount, None)
        tg.send_message(chat_id, f"✅ Budget total di-set <b>{rupiah(amount)}</b>/bulan.")
        return
    cat = _find_expense_category(db, name)
    if cat is None:
        tg.send_message(chat_id, f'Kategori "{name}" tak ketemu. Cek daftar di menu Kelola.')
        return
    set_budget(db, cat.id, amount, None)
    tg.send_message(chat_id, f"✅ Budget {cat.name} di-set <b>{rupiah(amount)}</b>/bulan.")


def _handle_photo(msg: dict, chat_id, db: Session, tg) -> None:
    tg.send_message(chat_id, "📸 Membaca struk…")
    # Telegram mengirim beberapa ukuran; ambil yang terbesar (terakhir).
    file_id = msg["photo"][-1]["file_id"]
    try:
        file_path = tg.get_file(file_id)
        image_bytes = tg.download_file(file_path)
    except Exception:
        tg.send_message(chat_id, "Gagal mengambil foto dari Telegram. Coba lagi ya.")
        return

    receipt, extraction = process_receipt(db, image_bytes, "image/jpeg")
    if extraction is None:
        tg.send_message(
            chat_id,
            "📸 Struk belum terbaca jelas. Coba foto lebih terang & rata, "
            "atau catat manual: <code>indomaret 32rb</code>",
        )
        return

    draft = build_draft(db, extraction)
    account = _default_account(db)
    now = now_local()
    tx = Transaction(
        amount=draft.amount,
        type=draft.type,
        category_id=draft.category_id,
        account_id=account.id if account else None,
        description=draft.description,
        occurred_at=draft.occurred_at,
        source="ocr",
        receipt_id=receipt.id,
    )
    db.add(tx)
    db.flush()
    apply_balance(db, tx, sign=1)
    db.commit()
    db.refresh(tx)

    header = fmt.tx_confirmation(
        amount=tx.amount,
        ttype=tx.type,
        description=tx.description or "",
        category_name=draft.category_name,
        occurred_at=tx.occurred_at.astimezone(LOCAL_TZ),
        now=now,
    )
    tg.send_message(
        chat_id, header + "\n<i>dari struk</i>", reply_markup=fmt.confirm_keyboard(tx.id)
    )


def _handle_command(text: str, chat_id, db: Session, tg) -> None:
    cmd = text.split()[0].lstrip("/").split("@")[0].lower()
    now = now_local()

    if cmd in ("start", "help"):
        tg.send_message(chat_id, fmt.HELP_TEXT)
    elif cmd == "hariini":
        start, end = _day_bounds(now)
        tg.send_message(chat_id, fmt.summary_text("Hari ini", period_summary(db, start, end)))
    elif cmd == "minggu":
        today_start, end = _day_bounds(now)
        start = today_start - timedelta(days=6)
        tg.send_message(chat_id, fmt.summary_text("7 hari terakhir", period_summary(db, start, end)))
    elif cmd == "bulan":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, end = _day_bounds(now)
        tg.send_message(chat_id, fmt.summary_text("Bulan ini", period_summary(db, start, end)))
    elif cmd == "budget":
        parts = text.split(maxsplit=1)
        _handle_budget(parts[1] if len(parts) > 1 else "", chat_id, db, tg)
    elif cmd == "undo":
        _handle_undo(chat_id, db, tg)
    else:
        tg.send_message(chat_id, "Perintah tidak dikenal. Ketik /help ya.")


def _handle_undo(chat_id, db: Session, tg) -> None:
    tx = db.scalars(
        select(Transaction).order_by(Transaction.created_at.desc(), Transaction.id.desc())
    ).first()
    if tx is None:
        tg.send_message(chat_id, "Belum ada transaksi untuk dihapus.")
        return
    label = f"{fmt.format_rupiah(tx.amount)} — {fmt.esc(tx.description or '')}".strip(" —")
    apply_balance(db, tx, sign=-1)
    db.delete(tx)
    db.commit()
    tg.send_message(chat_id, f"↩️ Dihapus: {label}")


def _handle_callback(cq: dict, db: Session, tg, allowed_chat_id: str | None) -> None:
    cq_id = cq["id"]
    message = cq.get("message") or {}
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    data = cq.get("data") or ""

    if not _authorized(chat_id, allowed_chat_id):
        tg.answer_callback_query(cq_id, "Tidak diizinkan")
        return

    action, _, rest = data.partition(":")

    if action == "pc":
        tx = db.get(Transaction, _to_int(rest))
        if tx is None:
            tg.answer_callback_query(cq_id, "Transaksi tidak ada")
            return
        ttype = tx.type if tx.type in ("expense", "income") else "expense"
        categories = db.scalars(
            select(Category).where(Category.type == ttype).order_by(Category.name)
        ).all()
        tg.edit_message_text(
            chat_id, message_id, "Pilih kategori:",
            reply_markup=fmt.category_keyboard(tx.id, categories),
        )
        tg.answer_callback_query(cq_id)

    elif action == "sc":
        tx_part, _, cat_part = rest.partition(":")
        tx = db.get(Transaction, _to_int(tx_part))
        category = db.get(Category, _to_int(cat_part))
        if tx is None or category is None:
            tg.answer_callback_query(cq_id, "Data tidak ada")
            return
        tx.category_id = category.id
        db.commit()
        if tx.description:
            learn_from_correction(db, tx.description, category)
        tg.edit_message_text(
            chat_id, message_id,
            fmt.tx_confirmation(
                amount=tx.amount, ttype=tx.type, description=tx.description or "",
                category_name=category.name,
                occurred_at=tx.occurred_at.astimezone(LOCAL_TZ), now=now_local(),
            ),
            reply_markup=fmt.confirm_keyboard(tx.id),
        )
        tg.answer_callback_query(cq_id, "Kategori diperbarui")

    elif action == "del":
        tx = db.get(Transaction, _to_int(rest))
        if tx is None:
            tg.answer_callback_query(cq_id, "Sudah dihapus")
            return
        apply_balance(db, tx, sign=-1)
        db.delete(tx)
        db.commit()
        tg.edit_message_text(chat_id, message_id, "🗑 Transaksi dihapus")
        tg.answer_callback_query(cq_id, "Dihapus")

    else:
        tg.answer_callback_query(cq_id)


def _day_bounds(now: datetime) -> tuple[datetime, datetime]:
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return start, end


def _to_int(s: str) -> int | None:
    try:
        return int(s)
    except (ValueError, TypeError):
        return None
