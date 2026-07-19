"""Isolasi antar-user + guard admin — jaring pengaman multi-tenant.

Admin (user #1) dibuat oleh seed. User kedua dibuat lewat /admin/users.
"""


def _bob(auth_client) -> dict:
    """Buat user 'bob' via admin, kembalikan header Authorization-nya."""
    r = auth_client.post("/admin/users", json={"username": "bob", "password": "bobpass123"})
    assert r.status_code == 201, r.text
    tok = auth_client.post(
        "/auth/login", data={"username": "bob", "password": "bobpass123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _makan(auth_client, headers=None) -> int:
    cats = auth_client.get("/categories", headers=headers).json()
    return next(c for c in cats if c["name"] == "Makan")["id"]


def test_new_user_gets_own_seeded_defaults(auth_client):
    hb = _bob(auth_client)
    cats = auth_client.get("/categories", headers=hb).json()
    assert len(cats) == 12  # kategori default
    accs = auth_client.get("/accounts", headers=hb).json()
    assert [a["name"] for a in accs] == ["Cash"]
    # id kategori/akun bob TERPISAH dari admin
    admin_cat_ids = {c["id"] for c in auth_client.get("/categories").json()}
    bob_cat_ids = {c["id"] for c in cats}
    assert admin_cat_ids.isdisjoint(bob_cat_ids)


def test_transactions_isolated_between_users(auth_client):
    hb = _bob(auth_client)
    makan = _makan(auth_client)
    tx = auth_client.post(
        "/transactions", json={"amount": 50000, "type": "expense", "category_id": makan}
    ).json()

    # bob tak lihat transaksi admin
    assert auth_client.get("/transactions", headers=hb).json()["total"] == 0
    # analitik bob nol
    assert float(auth_client.get("/analytics/summary", headers=hb).json()["total_expense"]) == 0
    # bob tak bisa GET transaksi admin by id
    assert auth_client.get(f"/transactions/{tx['id']}", headers=hb).status_code == 404
    # bob tak bisa hapus transaksi admin
    assert auth_client.delete(f"/transactions/{tx['id']}", headers=hb).status_code == 404
    # admin tetap punya 1 transaksi
    assert auth_client.get("/transactions").json()["total"] == 1


def test_cannot_attach_another_users_category_or_account(auth_client):
    hb = _bob(auth_client)
    admin_makan = _makan(auth_client)  # kategori milik admin
    # bob mencoba pakai kategori admin → 422 (tidak ditemukan untuk bob)
    r = auth_client.post(
        "/transactions",
        json={"amount": 1000, "type": "expense", "category_id": admin_makan},
        headers=hb,
    )
    assert r.status_code == 422


def test_net_worth_isolated(auth_client):
    hb = _bob(auth_client)
    # admin punya saldo di Cash lewat income
    auth_client.post("/transactions", json={"amount": 100000, "type": "income"})
    # net worth bob hanya akun bob (Cash 0)
    nw = auth_client.get("/accounts/net-worth", headers=hb).json()
    assert float(nw["total"]) == 0
    assert [a["name"] for a in nw["accounts"]] == ["Cash"]


def test_admin_guard_blocks_non_admin(auth_client):
    hb = _bob(auth_client)
    assert auth_client.get("/admin/users", headers=hb).status_code == 403
    assert auth_client.post(
        "/admin/users", json={"username": "x", "password": "xxxxxxxx"}, headers=hb
    ).status_code == 403
    # admin sendiri boleh
    assert auth_client.get("/admin/users").status_code == 200


def test_me_reports_admin_flag(auth_client):
    assert auth_client.get("/auth/me").json()["is_admin"] is True
    hb = _bob(auth_client)
    assert auth_client.get("/auth/me", headers=hb).json()["is_admin"] is False


def test_admin_cannot_delete_self_or_last_admin(auth_client):
    me = auth_client.get("/auth/me").json()
    # hapus diri sendiri → 422
    assert auth_client.delete(f"/admin/users/{me['id']}").status_code == 422
    # cabut admin dari satu-satunya admin → 422
    assert auth_client.patch(
        f"/admin/users/{me['id']}", json={"is_admin": False}
    ).status_code == 422


def test_admin_reset_password_and_unlink(auth_client):
    hb = _bob(auth_client)
    bob_id = next(u for u in auth_client.get("/admin/users").json() if u["username"] == "bob")["id"]
    # reset password bob
    assert auth_client.patch(
        f"/admin/users/{bob_id}", json={"password": "newpass123"}
    ).status_code == 200
    # login lama gagal, baru sukses
    assert auth_client.post(
        "/auth/login", data={"username": "bob", "password": "bobpass123"}
    ).status_code == 401
    assert auth_client.post(
        "/auth/login", data={"username": "bob", "password": "newpass123"}
    ).status_code == 200


def test_link_code_endpoint(auth_client):
    r = auth_client.post("/auth/telegram/link-code")
    assert r.status_code == 200
    body = r.json()
    assert len(body["code"]) == 6 and body["expires_at"]
