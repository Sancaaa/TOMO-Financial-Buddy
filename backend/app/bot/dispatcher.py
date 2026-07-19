"""Logika bot Telegram, terpisah dari transport agar mudah dites.

`handle_update` menerima dict update mentah dari Telegram, sebuah Session, dan
klien (punya send_message / edit_message_text / answer_callback_query). Multi-user:
pemilik update ditentukan dari `chat_id` → baris `User.telegram_chat_id`. Chat yang
belum terikat hanya bisa memakai `/link <kode>` (kode dibuat dari web).
"""

import re
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.bot import format as fmt
from app.core.clock import LOCAL_TZ, now_local
from app.models import Account, Category, Transaction, User
from app.services.budget import overview, set_budget
from app.services.categorizer import learn_from_correction, suggest_category
from app.services.ledger import apply_balance
from app.services.money import month_label, rupiah
from app.services.parser import parse_amount, parse_quick_input
from app.services.receipts import build_draft, process_receipt
from app.services.summary import period_summary

# Kode /link berlaku singkat; disimpan di User.settings oleh endpoint web.
LINK_CODE_TTL = timedelta(minutes=15)


def _resolve_user(db: Session, chat_id) -> User | None:
    if chat_id is None:
        return None
    return db.scalar(select(User).where(User.telegram_chat_id == str(chat_id)))


def handle_update(update: dict, db: Session, tg) -> None:
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = (cq.get("message") or {}).get("chat", {}).get("id")
        user = _resolve_user(db, chat_id)
        if user is None:
            tg.answer_callback_query(cq["id"], "Tidak diizinkan")
            return
        _handle_callback(cq, db, tg, user)
        return

    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    # /link <kode> atau /start <kode> (dari deep link) harus bisa dipakai chat yang BELUM terikat.
    if text.lower().startswith("/link") or text.lower().startswith("/start "):
        _handle_link(text, chat_id, db, tg)
        return

    user = _resolve_user(db, chat_id)
    if user is None:
        tg.send_message(
            chat_id,
            "Kamu belum terhubung ke akun TOMO.\n"
            f"chat_id kamu: <code>{chat_id}</code>\n"
            "Buka aplikasi web → <b>Kelola → Tautkan Telegram</b>, lalu kirim "
            "<code>/link KODE</code> ke sini.",
        )
        return

    if "photo" in msg:
        _handle_photo(msg, chat_id, db, tg, user)
        return
    if "document" in msg:
        tg.send_message(
            chat_id,
            "Kirim struk sebagai <b>foto</b> ya (bukan file), biar bisa dibaca OCR.",
        )
        return

    if not text:
        return
    if text.startswith("/"):
        _handle_command(text, chat_id, db, tg, user)
    else:
        _handle_quick_add(text, chat_id, db, tg, user)


def _handle_link(text: str, chat_id, db: Session, tg) -> None:
    parts = text.split()
    if len(parts) < 2:
        tg.send_message(chat_id, "Format: <code>/link KODE</code> (ambil kode di web).")
        return
    code = parts[1].strip()
    now = now_local()
    # cari user yang punya kode ini & belum kedaluwarsa
    for user in db.scalars(select(User)).all():
        stored = (user.settings or {}).get("link_code")
        if not stored or stored != code:
            continue
        expires = (user.settings or {}).get("link_expires")
        if expires and datetime.fromisoformat(expires) < now:
            tg.send_message(chat_id, "Kode sudah kedaluwarsa. Buat kode baru di web.")
            return
        # lepas ikatan lama chat ini (bila ada) agar unik
        prev = _resolve_user(db, chat_id)
        if prev is not None and prev.id != user.id:
            prev.telegram_chat_id = None
        user.telegram_chat_id = str(chat_id)
        s = dict(user.settings or {})
        s.pop("link_code", None)
        s.pop("link_expires", None)
        user.settings = s
        db.commit()
        tg.send_message(
            chat_id,
            f"✅ Terhubung sebagai <b>{fmt.esc(user.username)}</b>. "
            "Sekarang kamu bisa catat transaksi lewat chat ini.",
        )
        return
    tg.send_message(chat_id, "Kode tidak valid. Cek lagi di web ya.")


def _default_account(db: Session, user_id: int) -> Account | None:
    return db.scalars(
        select(Account).where(Account.user_id == user_id).order_by(Account.id)
    ).first()


def _handle_quick_add(text: str, chat_id, db: Session, tg, user: User) -> None:
    now = now_local()
    parsed = parse_quick_input(text, now)
    if parsed is None:
        tg.send_message(
            chat_id,
            "Nominal tidak terbaca 🤔 Coba: <code>makan 15k</code> / "
            "<code>gojek 24rb</code> / <code>dapet 50k</code>",
        )
        return

    category = suggest_category(db, parsed.description, parsed.type, user.id)
    account = _default_account(db, user.id)
    tx = Transaction(
        user_id=user.id,
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
        ov = overview(db, user.id)
        if ov.safe_to_spend is not None and ov.days_left > 0:
            body += f"\n💡 Aman jajan {rupiah(ov.safe_to_spend)}/hari sampai akhir bulan"
    tg.send_message(chat_id, body, reply_markup=fmt.confirm_keyboard(tx.id))


def _find_expense_category(db: Session, name: str, user_id: int) -> Category | None:
    name = name.strip().lower()
    cats = db.scalars(
        select(Category).where(Category.user_id == user_id, Category.type == "expense")
    ).all()
    for c in cats:
        if c.name.lower() == name:
            return c
    for c in cats:
        if name and (name in c.name.lower() or c.name.lower() in name):
            return c
    return None


def _budget_text(db: Session, user_id: int) -> str:
    ov = overview(db, user_id)
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


def _handle_budget(arg: str, chat_id, db: Session, tg, user: User) -> None:
    arg = arg.strip()
    if not arg:
        tg.send_message(chat_id, _budget_text(db, user.id))
        return
    amount = parse_amount(arg)
    if amount is None:
        tg.send_message(chat_id, "Format: <code>/budget makan 900rb</code> atau <code>/budget total 2jt</code>")
        return
    name = re.sub(r"\d[\d.,]*\s*(juta|ribu|jt|rb|k)?", "", arg, flags=re.IGNORECASE).strip()
    if name.lower() in ("total", "semua", ""):
        set_budget(db, None, amount, user.id, None)
        tg.send_message(chat_id, f"✅ Budget total di-set <b>{rupiah(amount)}</b>/bulan.")
        return
    cat = _find_expense_category(db, name, user.id)
    if cat is None:
        tg.send_message(chat_id, f'Kategori "{name}" tak ketemu. Cek daftar di menu Kelola.')
        return
    set_budget(db, cat.id, amount, user.id, None)
    tg.send_message(chat_id, f"✅ Budget {cat.name} di-set <b>{rupiah(amount)}</b>/bulan.")


def _handle_photo(msg: dict, chat_id, db: Session, tg, user: User) -> None:
    tg.send_message(chat_id, "📸 Membaca struk…")
    # Telegram mengirim beberapa ukuran; ambil yang terbesar (terakhir).
    file_id = msg["photo"][-1]["file_id"]
    try:
        file_path = tg.get_file(file_id)
        image_bytes = tg.download_file(file_path)
    except Exception:
        tg.send_message(chat_id, "Gagal mengambil foto dari Telegram. Coba lagi ya.")
        return

    receipt, extraction = process_receipt(db, image_bytes, user.id, "image/jpeg")
    if extraction is None:
        tg.send_message(
            chat_id,
            "📸 Struk belum terbaca jelas. Coba foto lebih terang & rata, "
            "atau catat manual: <code>indomaret 32rb</code>",
        )
        return

    draft = build_draft(db, extraction, user.id)
    account = _default_account(db, user.id)
    now = now_local()
    tx = Transaction(
        user_id=user.id,
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


def _handle_command(text: str, chat_id, db: Session, tg, user: User) -> None:
    cmd = text.split()[0].lstrip("/").split("@")[0].lower()
    now = now_local()

    if cmd in ("start", "help"):
        tg.send_message(chat_id, fmt.HELP_TEXT)
    elif cmd == "hariini":
        start, end = _day_bounds(now)
        tg.send_message(chat_id, fmt.summary_text("Hari ini", period_summary(db, start, end, user.id)))
    elif cmd == "minggu":
        today_start, end = _day_bounds(now)
        start = today_start - timedelta(days=6)
        tg.send_message(chat_id, fmt.summary_text("7 hari terakhir", period_summary(db, start, end, user.id)))
    elif cmd == "bulan":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, end = _day_bounds(now)
        tg.send_message(chat_id, fmt.summary_text("Bulan ini", period_summary(db, start, end, user.id)))
    elif cmd == "budget":
        parts = text.split(maxsplit=1)
        _handle_budget(parts[1] if len(parts) > 1 else "", chat_id, db, tg, user)
    elif cmd == "undo":
        _handle_undo(chat_id, db, tg, user)
    else:
        tg.send_message(chat_id, "Perintah tidak dikenal. Ketik /help ya.")


def _handle_undo(chat_id, db: Session, tg, user: User) -> None:
    tx = db.scalars(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
    ).first()
    if tx is None:
        tg.send_message(chat_id, "Belum ada transaksi untuk dihapus.")
        return
    label = f"{fmt.format_rupiah(tx.amount)} — {fmt.esc(tx.description or '')}".strip(" —")
    apply_balance(db, tx, sign=-1)
    db.delete(tx)
    db.commit()
    tg.send_message(chat_id, f"↩️ Dihapus: {label}")


def _handle_callback(cq: dict, db: Session, tg, user: User) -> None:
    cq_id = cq["id"]
    message = cq.get("message") or {}
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    data = cq.get("data") or ""

    action, _, rest = data.partition(":")

    def _owned_tx(tx_id):
        tx = db.get(Transaction, tx_id)
        return tx if tx is not None and tx.user_id == user.id else None

    if action == "pc":
        tx = _owned_tx(_to_int(rest))
        if tx is None:
            tg.answer_callback_query(cq_id, "Transaksi tidak ada")
            return
        ttype = tx.type if tx.type in ("expense", "income") else "expense"
        categories = db.scalars(
            select(Category)
            .where(Category.user_id == user.id, Category.type == ttype)
            .order_by(Category.name)
        ).all()
        tg.edit_message_text(
            chat_id, message_id, "Pilih kategori:",
            reply_markup=fmt.category_keyboard(tx.id, categories),
        )
        tg.answer_callback_query(cq_id)

    elif action == "sc":
        tx_part, _, cat_part = rest.partition(":")
        tx = _owned_tx(_to_int(tx_part))
        category = db.get(Category, _to_int(cat_part))
        if tx is None or category is None or category.user_id != user.id:
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
        tx = _owned_tx(_to_int(rest))
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
