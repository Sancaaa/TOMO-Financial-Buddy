def _mk(auth_client, amount, ttype, occurred_at, category_id=None):
    return auth_client.post(
        "/transactions",
        json={
            "amount": amount,
            "type": ttype,
            "category_id": category_id,
            "occurred_at": occurred_at,
        },
    )


def test_quick_add_endpoint(auth_client):
    resp = auth_client.post("/transactions/quick", json={"text": "makan 15k"})
    assert resp.status_code == 201, resp.text
    tx = resp.json()
    assert float(tx["amount"]) == 15000
    assert tx["type"] == "expense"
    assert tx["source"] == "web"
    assert tx["category"]["name"] == "Makan"


def test_quick_add_bad_input(auth_client):
    resp = auth_client.post("/transactions/quick", json={"text": "halo apa kabar"})
    assert resp.status_code == 422


def test_summary_endpoint(auth_client):
    makan = next(
        c for c in auth_client.get("/categories").json() if c["name"] == "Makan"
    )["id"]
    _mk(auth_client, 15000, "expense", "2026-05-03T10:00:00Z", makan)
    _mk(auth_client, 25000, "expense", "2026-05-04T10:00:00Z", makan)
    _mk(auth_client, 500000, "income", "2026-05-05T10:00:00Z")

    s = auth_client.get("/analytics/summary", params={"month": "2026-05"}).json()
    assert s["month"] == "2026-05"
    assert float(s["total_expense"]) == 40000
    assert float(s["total_income"]) == 500000
    names = {c["name"]: float(c["total"]) for c in s["per_category"]}
    assert names.get("Makan") == 40000


def test_trend_endpoint(auth_client):
    resp = auth_client.get("/analytics/trend", params={"months": 6})
    assert resp.status_code == 200
    points = resp.json()["points"]
    assert len(points) == 6
    # kronologis menaik
    assert points[0]["month"] < points[-1]["month"]


def _cid(auth_client, name):
    return next(c for c in auth_client.get("/categories").json() if c["name"] == name)["id"]


def test_comparison_reports_driver_category(auth_client):
    # T2.1: perbandingan menyebut kategori pendorong perubahan.
    jajan, makan = _cid(auth_client, "Jajan"), _cid(auth_client, "Makan")
    _mk(auth_client, 100000, "expense", "2026-04-10T10:00:00Z", jajan)
    _mk(auth_client, 100000, "expense", "2026-04-11T10:00:00Z", makan)
    _mk(auth_client, 250000, "expense", "2026-05-10T10:00:00Z", jajan)  # Jajan naik tajam
    _mk(auth_client, 100000, "expense", "2026-05-11T10:00:00Z", makan)

    c = auth_client.get("/analytics/comparison", params={"month": "2026-05"}).json()
    assert c["up"] is True
    assert c["pct"] == 75  # (350rb − 200rb) / 200rb
    assert c["driver_category"] == "Jajan"
    assert float(c["driver_delta"]) == 150000
    assert c["prev_month"] == "2026-04"


def test_comparison_none_when_no_prev(auth_client):
    makan = _cid(auth_client, "Makan")
    _mk(auth_client, 50000, "expense", "2026-05-10T10:00:00Z", makan)
    c = auth_client.get("/analytics/comparison", params={"month": "2026-05"}).json()
    assert float(c["prev_total_expense"]) == 0
    assert c["pct"] is None  # tak bisa dibandingkan


def test_trend_anchor_to_selected_month(auth_client):
    _mk(auth_client, 20000, "expense", "2026-05-10T10:00:00Z")
    points = auth_client.get(
        "/analytics/trend", params={"months": 6, "month": "2026-05"}
    ).json()["points"]
    assert points[-1]["month"] == "2026-05"
    assert len(points) == 6
