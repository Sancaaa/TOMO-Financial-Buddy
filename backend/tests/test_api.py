def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_requires_auth(client):
    # tanpa token → 401
    assert client.get("/transactions").status_code == 401


def test_wrong_password(client):
    resp = client.post(
        "/auth/login", data={"username": "admin", "password": "salah"}
    )
    assert resp.status_code == 401


def test_seed_categories_present(auth_client):
    cats = auth_client.get("/categories").json()
    names = {c["name"] for c in cats}
    assert {"Makan", "Transport", "Kiriman"} <= names
    # filter by type
    incomes = auth_client.get("/categories", params={"type": "income"}).json()
    assert all(c["type"] == "income" for c in incomes)


def test_transaction_crud_and_balance(auth_client):
    # akun cash default hasil seed, saldo 0
    account = auth_client.get("/accounts").json()[0]
    assert account["name"] == "Cash"
    makan = next(
        c for c in auth_client.get("/categories").json() if c["name"] == "Makan"
    )

    # buat pengeluaran 15.000 → saldo akun turun jadi -15000
    resp = auth_client.post(
        "/transactions",
        json={
            "amount": 15000,
            "type": "expense",
            "category_id": makan["id"],
            "account_id": account["id"],
            "description": "nasi goreng",
        },
    )
    assert resp.status_code == 201, resp.text
    tx = resp.json()
    assert tx["category"]["name"] == "Makan"

    bal = auth_client.get("/accounts").json()[0]["balance"]
    assert float(bal) == -15000

    # ubah jadi 20.000 → saldo -20000
    auth_client.patch(f"/transactions/{tx['id']}", json={"amount": 20000})
    assert float(auth_client.get("/accounts").json()[0]["balance"]) == -20000

    # tambah pemasukan 50.000 → saldo -20000 + 50000 = 30000
    auth_client.post(
        "/transactions",
        json={"amount": 50000, "type": "income", "account_id": account["id"]},
    )
    assert float(auth_client.get("/accounts").json()[0]["balance"]) == 30000

    # hapus pengeluaran 20.000 → saldo balik jadi 50000
    auth_client.delete(f"/transactions/{tx['id']}")
    assert float(auth_client.get("/accounts").json()[0]["balance"]) == 50000


def test_list_filters_and_pagination(auth_client):
    account = auth_client.get("/accounts").json()[0]
    for i in range(3):
        auth_client.post(
            "/transactions",
            json={
                "amount": 1000 * (i + 1),
                "type": "expense",
                "account_id": account["id"],
                "description": f"item-filter-{i}",
                "occurred_at": "2026-05-10T10:00:00Z",
            },
        )
    # filter bulan
    may = auth_client.get("/transactions", params={"month": "2026-05"}).json()
    assert may["total"] >= 3
    assert all(t["occurred_at"].startswith("2026-05") for t in may["items"])

    # search
    found = auth_client.get(
        "/transactions", params={"q": "item-filter-1"}
    ).json()
    assert found["total"] == 1

    # pagination
    page = auth_client.get(
        "/transactions", params={"month": "2026-05", "limit": 2}
    ).json()
    assert len(page["items"]) == 2 and page["limit"] == 2


def test_bad_month_format(auth_client):
    assert (
        auth_client.get("/transactions", params={"month": "2026/05"}).status_code
        == 422
    )


def test_amount_must_be_positive(auth_client):
    resp = auth_client.post(
        "/transactions", json={"amount": -5, "type": "expense"}
    )
    assert resp.status_code == 422


def test_month_window_consistent_history_vs_analytics(auth_client):
    """Transaksi di batas bulan (dini hari lokal) harus ikut terhitung sama di
    Riwayat maupun Analitik. Dulu Riwayat pakai batas UTC → total tidak cocok."""
    account = auth_client.get("/accounts").json()[0]
    # 02:00 waktu lokal (TZ_OFFSET_HOURS=7 di test) tgl 1 — di UTC ini jatuh ke
    # bulan sebelumnya, jadi memicu bug lama bila batas tidak konsisten.
    resp = auth_client.post(
        "/transactions",
        json={
            "amount": 12345,
            "type": "expense",
            "account_id": account["id"],
            "occurred_at": "2026-08-01T02:00:00+07:00",
        },
    )
    assert resp.status_code == 201, resp.text

    month = "2026-08"
    hist = auth_client.get("/transactions", params={"month": month}).json()
    hist_expense = sum(
        float(t["amount"]) for t in hist["items"] if t["type"] == "expense"
    )
    summary = auth_client.get("/analytics/summary", params={"month": month}).json()

    assert any(float(t["amount"]) == 12345 for t in hist["items"])
    assert float(summary["total_expense"]) == hist_expense == 12345
