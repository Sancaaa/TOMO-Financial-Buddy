"""Regresi: transaksi tanpa akun tidak mengurangi saldo, tapi tetap muncul di
analitik. Ini adalah bug yang dilaporkan saat upload struk lewat web (OCR confirm
tak mengirim account_id). Fix ada di frontend (kirim account_id), tapi test ini
mengunci perilaku backend yang jadi sandarannya: assign akun via PATCH akan
menerapkan pengurangan saldo (jalur pemulihan lewat edit sheet)."""

from decimal import Decimal


def _account(client, acc_id):
    return next(a for a in client.get("/accounts").json() if a["id"] == acc_id)


def test_accountless_expense_shows_in_analytics_but_not_balance(auth_client):
    acc = auth_client.get("/accounts").json()[0]
    start = Decimal(acc["balance"])

    # Perilaku OCR lama (buggy): expense TANPA account_id, bertanggal Juni.
    resp = auth_client.post(
        "/transactions",
        json={
            "type": "expense",
            "amount": 25000,
            "occurred_at": "2026-06-15T12:00:00+07:00",
            "source": "ocr",
        },
    )
    assert resp.status_code == 201, resp.text
    tx_id = resp.json()["id"]

    # Saldo TIDAK berubah (apply_balance no-op saat account_id None)...
    assert Decimal(_account(auth_client, acc["id"])["balance"]) == start
    # ...tapi TERCATAT di analitik Juni.
    summ = auth_client.get("/analytics/summary?month=2026-06").json()
    assert Decimal(summ["total_expense"]) == Decimal(25000)

    # Jalur pemulihan (edit sheet setelah fix): assign akun → saldo berkurang.
    fix = auth_client.patch(f"/transactions/{tx_id}", json={"account_id": acc["id"]})
    assert fix.status_code == 200, fix.text
    assert Decimal(_account(auth_client, acc["id"])["balance"]) == start - 25000


def test_expense_created_with_account_reduces_balance(auth_client):
    acc = auth_client.get("/accounts").json()[0]
    start = Decimal(acc["balance"])

    # Perilaku OCR setelah fix: account_id ikut dikirim → langsung mengurangi saldo.
    resp = auth_client.post(
        "/transactions",
        json={
            "type": "expense",
            "amount": 25000,
            "account_id": acc["id"],
            "occurred_at": "2026-06-15T12:00:00+07:00",
            "source": "ocr",
        },
    )
    assert resp.status_code == 201, resp.text
    assert Decimal(_account(auth_client, acc["id"])["balance"]) == start - 25000
