"""Tes keamanan auth: ganti password + rate-limit login."""


def test_change_password_flow(auth_client):
    # ganti password admin (login awal admin123 via fixture)
    resp = auth_client.post(
        "/auth/change-password",
        json={"old_password": "admin123", "new_password": "rahasia-baru-123"},
    )
    assert resp.status_code == 204, resp.text

    # password lama tak lagi berlaku
    old = auth_client.post(
        "/auth/login", data={"username": "admin", "password": "admin123"}
    )
    assert old.status_code == 401

    # password baru berlaku
    new = auth_client.post(
        "/auth/login", data={"username": "admin", "password": "rahasia-baru-123"}
    )
    assert new.status_code == 200, new.text


def test_change_password_wrong_old(auth_client):
    resp = auth_client.post(
        "/auth/change-password",
        json={"old_password": "salah", "new_password": "rahasia-baru-123"},
    )
    assert resp.status_code == 400


def test_change_password_too_short(auth_client):
    resp = auth_client.post(
        "/auth/change-password",
        json={"old_password": "admin123", "new_password": "pendek"},
    )
    assert resp.status_code == 422  # new_password min_length=8


def test_login_rate_limited_after_repeated_failures(client):
    # username unik agar tidak mengganggu / terganggu test lain (dict rate-limit global)
    user = "brute-force-probe"
    for _ in range(5):
        r = client.post("/auth/login", data={"username": user, "password": "x"})
        assert r.status_code == 401
    # percobaan ke-6 dalam window → diblokir
    blocked = client.post("/auth/login", data={"username": user, "password": "x"})
    assert blocked.status_code == 429
