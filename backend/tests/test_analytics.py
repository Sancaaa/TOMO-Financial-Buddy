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
